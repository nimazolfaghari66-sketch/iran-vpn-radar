"""Iranian vantage-point testing via the public Check-Host API.

Check-Host (https://check-host.net) operates a set of network diagnostic nodes
around the world, including several inside Iran. This module uses those Iranian
nodes to answer a narrow, honest question: **is this configuration's server
reachable from inside Iran, and does it resolve?**

What this module can prove
--------------------------
* the server hostname resolves from an Iranian vantage point (DNS);
* the server's TCP port accepts a connection from an Iranian city;
* an HTTP/HTTPS endpoint responds from Iran;
* a UDP socket is reachable where applicable.

What this module can **never** prove
------------------------------------
* that a VLESS/VMess/Trojan/Shadowsocks/Hysteria2/TUIC *tunnel* works. A
  Check-Host node is a remote diagnostic probe; we cannot install or execute a
  VPN client on it. A reachable port is not a working tunnel.

Consequently no result from this module is publishable. Every classification it
produces (``IRAN_TCP_REACHABLE`` and friends) is informational. Only the
dedicated Iran probe agent (:mod:`radar.iran_probe`), which runs a real VPN
client on a host inside Iran, may produce ``IRAN_FULL_TUNNEL_VERIFIED`` and move
a configuration to ``WORKING``.

Node identity is discovered dynamically from the current registry; the historic
IP list below is kept only for *comparison* and is never treated as an
authoritative node identity.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import config as cfg
from .logging_setup import get_logger, redact
from .models import Config, iso, utcnow
from .storage import _atomic_write_json, read_json

log = get_logger("radar.checkhost")

BASE = "https://check-host.net"
NODES_HOSTS = f"{BASE}/nodes/hosts"
NODES_IPS = f"{BASE}/nodes/ips"

# Historic Iranian node IPs, recorded for comparison only. These are NOT used
# as node identities: a node may be reassigned, and an IP may change hands.
HISTORICAL_IRAN_IPS: dict[str, str] = {
    "185.105.238.209": "Tehran",
    "88.135.75.5": "Tehran",
    "91.102.127.2": "Tehran",
    "178.239.146.199": "Tehran",
    "195.182.38.164": "Isfahan",
    "77.104.108.3": "Shiraz",
    "195.234.80.20": "Shiraz",
    "45.135.242.142": "Qom",
}

DEFAULT_USER_AGENT = "IranVPNRadar/1.0 (+https://github.com/nimazolfaghari66-sketch/iran-vpn-radar)"


# --------------------------------------------------------------------- models
@dataclass
class NodeInfo:
    """A single Check-Host diagnostic node."""

    identifier: str
    ip: str
    country: str
    city: str | None
    asn: str | None
    country_code: str = ""

    @property
    def is_iran(self) -> bool:
        return self.country_code.upper() == "IR"

    @property
    def historical_city(self) -> str | None:
        """City this IP was historically associated with, if any."""
        return HISTORICAL_IRAN_IPS.get(self.ip)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NodeCheck:
    """Result of one check performed by one node."""

    node: str
    city: str | None
    asn: str | None
    ip: str
    check: str  # dns | tcp | http | udp | ping
    ok: bool
    classification: str
    latency_ms: float | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CheckHostRecord:
    """Timestamped results for one configuration across Iranian nodes."""

    fingerprint: str
    host: str
    port: int | None
    protocol: str
    checked_at: str = field(default_factory=lambda: iso(utcnow()))
    checks: list[NodeCheck] = field(default_factory=list)
    # Aggregate classification across all nodes for this configuration.
    summary: str = cfg.IRAN_UNREACHABLE
    cities_reachable: list[str] = field(default_factory=list)
    cities_unreachable: list[str] = field(default_factory=list)
    request_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["checks"] = [c.to_dict() if isinstance(c, NodeCheck) else c for c in self.checks]
        return data


# ------------------------------------------------------------------ discovery
def fetch_registry(timeout: float = 20.0, user_agent: str = DEFAULT_USER_AGENT) -> dict[str, dict]:
    """Fetch the current Check-Host node registry (``/nodes/hosts``)."""
    req = urllib.request.Request(
        NODES_HOSTS,
        headers={"Accept": "application/json", "User-Agent": user_agent},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    nodes = data.get("nodes", {}) if isinstance(data, dict) else {}
    return nodes if isinstance(nodes, dict) else {}


def parse_node(identifier: str, raw: dict) -> NodeInfo:
    location = raw.get("location") or []
    country_code = location[0] if len(location) > 0 else ""
    country = location[1] if len(location) > 1 else ""
    city = location[2] if len(location) > 2 else None
    return NodeInfo(
        identifier=identifier,
        ip=str(raw.get("ip", "")),
        country=country,
        city=city,
        asn=raw.get("asn"),
        country_code=str(country_code),
    )


def discover_nodes(user_agent: str = DEFAULT_USER_AGENT, timeout: float = 20.0) -> list[NodeInfo]:
    """Discover all currently available Iranian Check-Host nodes."""
    registry = fetch_registry(timeout=timeout, user_agent=user_agent)
    nodes = [parse_node(name, raw) for name, raw in registry.items()]
    return [n for n in nodes if n.is_iran]


def compare_with_historical(nodes: list[NodeInfo]) -> dict[str, Any]:
    """Compare the current Iranian nodes with the historic IP list.

    Returns a report describing which historic IPs are still present, which are
    gone, and whether any node's city has changed relative to the historical
    association. This is deliberately a *comparison*: current registry data is
    authoritative, never the historic list.
    """
    current_by_ip = {n.ip: n for n in nodes}
    still_active: list[dict] = []
    missing: list[dict] = []
    city_changed: list[dict] = []

    for ip, historic_city in HISTORICAL_IRAN_IPS.items():
        node = current_by_ip.get(ip)
        if node is None:
            missing.append({"ip": ip, "historical_city": historic_city})
            continue
        entry = {
            "ip": ip,
            "identifier": node.identifier,
            "historical_city": historic_city,
            "current_city": node.city,
            "asn": node.asn,
        }
        still_active.append(entry)
        if node.city and historic_city and node.city.lower() != historic_city.lower():
            city_changed.append(entry)

    new_nodes = [
        n.to_dict()
        for n in nodes
        if n.ip not in HISTORICAL_IRAN_IPS
    ]
    return {
        "checked_at": iso(utcnow()),
        "current_iran_nodes": len(nodes),
        "historical_reference": len(HISTORICAL_IRAN_IPS),
        "still_active": still_active,
        "missing": missing,
        "city_changed": city_changed,
        "new_since_history": new_nodes,
        "cities": sorted({n.city for n in nodes if n.city}),
    }


# -------------------------------------------------------------------- checking
class CheckHostError(RuntimeError):
    pass


class RateLimiter:
    """Token-free politeness: minimum spacing between Check-Host submissions."""

    def __init__(self, min_interval: float = 2.5):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self) -> None:
        delta = time.time() - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.time()


class CheckHostClient:
    """Thin client over the Check-Host HTTP API.

    The API is asynchronous: a ``/check-<type>`` request returns a
    ``request_id``, and ``/check-result/<id>`` is polled until every node has
    reported (a node that has not finished yet appears as ``null``).
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 20.0,
        poll_interval: float = 2.0,
        max_polls: int = 8,
        min_interval: float = 2.5,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_polls = max_polls
        self.limiter = RateLimiter(min_interval)

    # -------------------------------------------------------------- transport
    def _get_json(self, url: str) -> Any:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": self.user_agent})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def submit(self, check: str, host: str, nodes: list[str]) -> tuple[str, dict[str, list]]:
        """Submit a check and return ``(request_id, node_locations)``."""
        params = [("host", host)]
        for node in nodes:
            params.append(("node", node))
        url = f"{BASE}/check-{check}?" + urllib.parse.urlencode(params)
        self.limiter.wait()
        try:
            data = self._get_json(url)
        except urllib.error.HTTPError as exc:
            raise CheckHostError(f"submit {check} failed: http {exc.code}") from exc
        except Exception as exc:  # network hiccup
            raise CheckHostError(f"submit {check} failed: {redact(str(exc))}") from exc
        if not isinstance(data, dict) or not data.get("request_id"):
            raise CheckHostError(f"submit {check} returned no request_id")
        return str(data["request_id"]), data.get("nodes", {})

    def poll(self, request_id: str) -> dict[str, Any]:
        """Poll until every node has reported, or the poll budget is exhausted."""
        url = f"{BASE}/check-result/{urllib.parse.quote(request_id)}"
        results: dict[str, Any] = {}
        for _ in range(self.max_polls):
            time.sleep(self.poll_interval)
            try:
                results = self._get_json(url)
            except Exception:
                continue
            if isinstance(results, dict) and results and all(v is not None for v in results.values()):
                return results
        return results if isinstance(results, dict) else {}

    def run(self, check: str, host: str, nodes: list[str]) -> tuple[str, dict[str, list], dict[str, Any]]:
        request_id, locations = self.submit(check, host, nodes)
        results = self.poll(request_id)
        return request_id, locations, results


# ------------------------------------------------------------- classification
# The Check-Host API wraps each node's result in a single-element list, e.g.
#   TCP  ok    -> [{"address": "...", "time": 0.08}]
#   TCP  fail  -> [{"error": "Connection timed out"}]
#   DNS  ok    -> [{"A": [...], "AAAA": [...], "TTL": 20}]
#   HTTP ok    -> [[1, 0.158, "OK", "200", "1.2.3.4"]]
def _unwrap(entry: Any) -> Any:
    """Unwrap the API's single-element list wrapper, returning the inner value."""
    if isinstance(entry, list) and entry:
        return entry[0]
    return entry


def classify_tcp(entry: Any) -> tuple[bool, str, float | None, str | None]:
    inner = _unwrap(entry)
    if isinstance(inner, dict):
        if inner.get("time") is not None and inner.get("address") is not None:
            return True, cfg.IRAN_TCP_REACHABLE, float(inner["time"]) * 1000.0, None
        if "error" in inner:
            err = str(inner["error"])
            cls = cfg.IRAN_TIMEOUT if "timed out" in err.lower() or "timeout" in err.lower() else cfg.IRAN_UNREACHABLE
            return False, cls, None, err
    return False, cfg.IRAN_UNREACHABLE, None, "no result"


def classify_dns(entry: Any) -> tuple[bool, str, float | None, str | None]:
    inner = _unwrap(entry)
    if isinstance(inner, dict):
        if inner.get("A") or inner.get("AAAA"):
            return True, cfg.IRAN_DNS_OK, None, None
        if "error" in inner:
            return False, cfg.IRAN_UNREACHABLE, None, str(inner["error"])
        # An IP literal resolves to an empty PTR record: that still proves the
        # node reached its resolver, but we do not treat it as DNS success.
        if "PTR" in inner:
            return False, cfg.IRAN_UNREACHABLE, None, "no A/AAAA record (IP literal)"
    return False, cfg.IRAN_UNREACHABLE, None, "no result"


def classify_http(entry: Any) -> tuple[bool, str, float | None, str | None]:
    inner = _unwrap(entry)
    if isinstance(inner, list) and len(inner) >= 2 and inner[0] == 1:
        latency = float(inner[1]) * 1000.0 if isinstance(inner[1], (int, float)) else None
        return True, cfg.IRAN_HTTP_REACHABLE, latency, None
    if isinstance(inner, dict) and "error" in inner:
        return False, cfg.IRAN_UNREACHABLE, None, str(inner["error"])
    return False, cfg.IRAN_UNREACHABLE, None, "no result"


def classify_udp(entry: Any) -> tuple[bool, str, float | None, str | None]:
    inner = _unwrap(entry)
    if isinstance(inner, dict):
        if inner.get("timeout"):
            return False, cfg.IRAN_TIMEOUT, None, "timeout"
        if inner.get("time") is not None and inner.get("address") is not None:
            return True, cfg.IRAN_UDP_REACHABLE, float(inner["time"]) * 1000.0, None
        if "error" in inner:
            return False, cfg.IRAN_UNREACHABLE, None, str(inner["error"])
    return False, cfg.IRAN_UNREACHABLE, None, "no result"


CLASSIFIERS = {
    "tcp": classify_tcp,
    "dns": classify_dns,
    "http": classify_http,
    "udp": classify_udp,
}


# ------------------------------------------------------------------ orchestrate
def _check_host_for(conf: Config) -> str:
    if conf.protocol in ("hysteria2", "tuic"):
        return f"{conf.host}:{conf.port}" if conf.port else conf.host
    if conf.port:
        return f"{conf.host}:{conf.port}"
    return conf.host


def test_config(
    conf: Config,
    nodes: list[NodeInfo],
    client: CheckHostClient,
    checks: tuple[str, ...] = ("dns", "tcp"),
) -> CheckHostRecord:
    """Test one configuration from the given Iranian nodes.

    Never raises for a per-node failure; failures are recorded as results.
    """
    record = CheckHostRecord(
        fingerprint=conf.fingerprint,
        host=conf.host,
        port=conf.port,
        protocol=conf.protocol,
    )
    node_ids = [n.identifier for n in nodes]
    by_id = {n.identifier: n for n in nodes}

    # DNS resolution is only meaningful for hostnames; an IP-literal host has no
    # A/AAAA record to look up, so we skip DNS for it rather than record noise.
    effective_checks = tuple(c for c in checks if c != "dns" or conf.host_kind == "domain")

    for check in effective_checks:
        target = _check_host_for(conf)
        if check == "dns":
            target = conf.host
        try:
            request_id, locations, results = client.run(check, target, node_ids)
        except CheckHostError as exc:
            log.warning("check-host check failed", extra={"context": {"check": check, "err": str(exc)}})
            continue
        record.request_ids.append(request_id)
        classifier = CLASSIFIERS.get(check)
        if classifier is None:
            continue
        for node_id, entry in results.items():
            node = by_id.get(node_id)
            city = node.city if node else (locations.get(node_id, [None, None, None])[2] if node_id in locations else None)
            asn = node.asn if node else None
            ip = node.ip if node else ""
            ok, classification, latency, detail = classifier(entry)
            record.checks.append(
                NodeCheck(
                    node=node_id,
                    city=city,
                    asn=asn,
                    ip=ip,
                    check=check,
                    ok=ok,
                    classification=classification,
                    latency_ms=latency,
                    detail=detail,
                )
            )

    _summarize(record)
    return record


def _summarize(record: CheckHostRecord) -> None:
    """Aggregate per-node checks into a per-configuration summary.

    The summary is the strongest *reachability* signal observed, and is never
    ``IRAN_FULL_TUNNEL_VERIFIED`` — that can only come from the Iran probe.
    """
    reachable_cities: set[str] = set()
    unreachable_cities: set[str] = set()
    best = cfg.IRAN_UNREACHABLE
    rank = {
        cfg.IRAN_UNREACHABLE: 0,
        cfg.IRAN_TIMEOUT: 1,
        cfg.IRAN_DNS_OK: 2,
        cfg.IRAN_UDP_REACHABLE: 3,
        cfg.IRAN_HTTP_REACHABLE: 4,
        cfg.IRAN_TCP_REACHABLE: 5,
    }
    for check in record.checks:
        city = check.city or "unknown"
        if check.ok:
            reachable_cities.add(city)
            if rank.get(check.classification, 0) > rank.get(best, 0):
                best = check.classification
        else:
            unreachable_cities.add(city)
    record.cities_reachable = sorted(reachable_cities)
    record.cities_unreachable = sorted(unreachable_cities - reachable_cities)
    record.summary = best


# --------------------------------------------------------------------- storage
def results_path(state_dir) -> Path:
    return Path(state_dir) / "checkhost_results.json"


def save_results(state_dir, records: list[CheckHostRecord], keep_per_fingerprint: int = 5) -> Path:
    """Persist timestamped results, retaining history per fingerprint."""
    path = results_path(state_dir)
    existing = read_json(path, {"records": []})
    history: dict[str, list] = {}
    for item in existing.get("records", []) if isinstance(existing, dict) else []:
        fp = item.get("fingerprint")
        if fp:
            history.setdefault(fp, []).append(item)

    for record in records:
        history.setdefault(record.fingerprint, []).append(record.to_dict())

    trimmed: list[dict] = []
    for fp, items in history.items():
        trimmed.extend(items[-keep_per_fingerprint:])

    payload = {
        "updated_at": iso(utcnow()),
        "count": len(trimmed),
        "records": trimmed,
    }
    _atomic_write_json(path, payload)
    return path


def load_results(state_dir) -> list[dict]:
    raw = read_json(results_path(state_dir), {"records": []})
    if isinstance(raw, dict):
        return list(raw.get("records", []))
    return list(raw)


def select_sample(configs: dict[str, Config], max_batch: int) -> list[Config]:
    """Pick a representative, protocol-diverse sample for diagnostic testing."""
    chosen: list[Config] = []
    seen_proto: set[str] = set()
    for conf in configs.values():
        if conf.status == cfg.DUPLICATE or conf.status == cfg.EXPIRED:
            continue
        if conf.protocol not in seen_proto:
            chosen.append(conf)
            seen_proto.add(conf.protocol)
        if len(chosen) >= max_batch:
            return chosen
    if len(chosen) < max_batch:
        for conf in configs.values():
            if conf in chosen or conf.status in (cfg.DUPLICATE, cfg.EXPIRED):
                continue
            chosen.append(conf)
            if len(chosen) >= max_batch:
                break
    return chosen


def run_checkhost_round(configs: dict[str, Config], settings, store) -> dict[str, Any]:
    """Run one diagnostic Check-Host round from Iranian nodes.

    This is best-effort and never raises to the caller: a Check-Host outage must
    not affect the subscription pipeline. It records results but does **not**
    modify configuration status — Check-Host cannot promote anything to
    ``WORKING``.
    """
    result: dict[str, Any] = {
        "enabled": bool(getattr(settings, "checkhost_enabled", False)),
        "nodes": 0,
        "cities": [],
        "tested": 0,
        "error": None,
    }
    if not result["enabled"]:
        result["note"] = "check-host diagnostics disabled"
        return result

    try:
        nodes = discover_nodes(user_agent=settings.user_agent)
    except Exception as exc:
        result["error"] = redact(str(exc))
        log.warning("check-host node discovery failed", extra={"context": {"err": str(exc)}})
        return result

    result["nodes"] = len(nodes)
    result["cities"] = sorted({n.city for n in nodes if n.city})
    if not nodes:
        result["note"] = "no Iranian Check-Host nodes available"
        return result

    # Record the current registry (timestamped) for historical comparison.
    payload = store.load_checkhost_nodes()
    history = list(payload.get("history", []))
    history.append({"discovered_at": iso(utcnow()), "nodes": [n.to_dict() for n in nodes]})
    store.save_checkhost_nodes(
        {"updated_at": iso(utcnow()), "nodes": [n.to_dict() for n in nodes], "history": history[-50:]}
    )

    checks = tuple(getattr(settings, "checkhost_checks", ("dns", "tcp")))
    batch = int(getattr(settings, "checkhost_batch", 12))
    sample = select_sample(configs, batch)
    client = CheckHostClient(
        user_agent=settings.user_agent,
        min_interval=float(getattr(settings, "checkhost_min_interval", 2.5)),
    )
    records: list[CheckHostRecord] = []
    for conf in sample:
        try:
            records.append(test_config(conf, nodes, client, checks=checks))
        except Exception as exc:  # never let diagnostics break the cycle
            log.warning("check-host test failed", extra={"context": {"fp": conf.fingerprint, "err": str(exc)}})
    save_results(store.state_dir, records)
    result["tested"] = len(records)
    result["summary"] = summarize_records(load_results(store.state_dir))
    return result


def summarize_records(records: list[dict]) -> dict[str, Any]:
    """Aggregate the latest result per fingerprint, by city and protocol."""
    latest: dict[str, dict] = {}
    for rec in records:
        fp = rec.get("fingerprint")
        if not fp:
            continue
        prev = latest.get(fp)
        if prev is None or (rec.get("checked_at") or "") >= (prev.get("checked_at") or ""):
            latest[fp] = rec

    by_protocol: dict[str, dict[str, int]] = {}
    by_city: dict[str, dict[str, int]] = {}
    by_summary: dict[str, int] = {}
    for rec in latest.values():
        proto = rec.get("protocol", "unknown")
        bucket = by_protocol.setdefault(proto, {"tested": 0, "reachable": 0})
        bucket["tested"] += 1
        summary = rec.get("summary", cfg.IRAN_UNREACHABLE)
        by_summary[summary] = by_summary.get(summary, 0) + 1
        if summary in cfg.CHECKHOST_REACHABLE:
            bucket["reachable"] += 1
        for city in rec.get("cities_reachable", []) or []:
            cb = by_city.setdefault(city, {"reachable": 0, "unreachable": 0})
            cb["reachable"] += 1
        for city in rec.get("cities_unreachable", []) or []:
            cb = by_city.setdefault(city, {"reachable": 0, "unreachable": 0})
            cb["unreachable"] += 1

    return {
        "configs_tested": len(latest),
        "by_summary": by_summary,
        "by_protocol": by_protocol,
        "by_city": by_city,
    }
