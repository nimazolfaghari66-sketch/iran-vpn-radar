"""Iranian vantage-point testing via the public Globalping network.

Globalping (https://globalping.io) is a free, public, volunteer-run network of
measurement probes. Unlike Check-Host — whose Iranian nodes only expose a bare
TCP socket — a Globalping probe runs a **real HTTP client**, so we can observe,
from inside Iran, a genuine DNS lookup, TCP connect, TLS handshake and HTTP
response against a configuration's server.

Why this matters
----------------
For a TLS-based configuration (VLESS/VMess/Trojan with TLS, or any server that
terminates TLS on its port) a successful Globalping HTTPS measurement proves the
server performs a real TLS handshake *from an Iranian ISP*. That is strictly
stronger evidence than a TCP port check.

What this still cannot prove
----------------------------
A Globalping probe cannot run a VLESS/VMess/Trojan/Shadowsocks/Hysteria2/TUIC
client, so it can never establish the *tunnel*, send traffic *through* it, or
observe the tunnel exit IP. Therefore — exactly like Check-Host — every result
this module produces is **diagnostic only and never publishable**. It can never
move a configuration to ``WORKING``. Only the dedicated Iran probe agent
(:mod:`radar.iran_probe`), which runs a real VPN client on a host inside Iran,
may produce ``IRAN_FULL_TUNNEL_VERIFIED``.

Probe identity is discovered dynamically from the live registry. We never
hard-code a probe: the network is volunteer-run and its Iranian members change.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from . import config as cfg
from .logging_setup import get_logger, redact
from .models import Config, iso, utcnow
from .storage import _atomic_write_json, read_json

log = get_logger("radar.globalping")

BASE = "https://api.globalping.io/v1"
PROBES_URL = f"{BASE}/probes"
MEASUREMENTS_URL = f"{BASE}/measurements"
DEFAULT_USER_AGENT = (
    "IranVPNRadar/1.0 (+https://github.com/nimazolfaghari66-sketch/iran-vpn-radar)"
)

# Rank of reachability signals, weakest to strongest. The per-configuration
# summary is the strongest stage any Iranian probe reached.
_REACH_RANK = {
    cfg.IRAN_UNREACHABLE: 0,
    cfg.IRAN_TIMEOUT: 1,
    cfg.IRAN_DNS_OK: 2,
    cfg.IRAN_ICMP_REACHABLE: 3,
    cfg.IRAN_TCP_REACHABLE: 4,
    cfg.IRAN_TLS_OK: 5,
    cfg.IRAN_HTTP_REACHABLE: 6,
    cfg.IRAN_UDP_REACHABLE: 6,
}

# A Globalping target must be a bare hostname or IP literal. Anything else
# (e.g. a URL mistakenly stored as a host) is not a valid measurement target.
_HOST_RE = re.compile(r"^[A-Za-z0-9._:-]+$")


def is_valid_target(host: str) -> bool:
    if not host or len(host) > 253:
        return False
    if "://" in host or "/" in host or " " in host:
        return False
    return bool(_HOST_RE.match(host))


# --------------------------------------------------------------------- models
@dataclass
class Probe:
    """A single Globalping probe location."""

    country: str
    city: str | None
    asn: int | None
    network: str | None
    tags: list[str] = field(default_factory=list)

    @property
    def is_iran(self) -> bool:
        return (self.country or "").upper() == "IR"

    @property
    def key(self) -> str:
        return f"{self.city or '?'}/AS{self.asn or '?'}/{self.network or '?'}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProbeCheck:
    """Result of one measurement performed by one Iranian probe."""

    city: str | None
    asn: int | None
    network: str | None
    ok: bool
    classification: str
    latency_ms: float | None = None
    tls: bool = False
    status_code: int | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GlobalpingRecord:
    """Timestamped results for one configuration across Iranian probes."""

    fingerprint: str
    host: str
    port: int | None
    protocol: str
    checked_at: str = field(default_factory=lambda: iso(utcnow()))
    measurement_id: str | None = None
    checks: list[ProbeCheck] = field(default_factory=list)
    summary: str = cfg.IRAN_UNREACHABLE
    cities_reachable: list[str] = field(default_factory=list)
    cities_unreachable: list[str] = field(default_factory=list)
    tls_verified: bool = False
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["checks"] = [c.to_dict() if isinstance(c, ProbeCheck) else c for c in self.checks]
        return data


# ------------------------------------------------------------------ discovery
def _probe_from_raw(raw: dict) -> Probe:
    loc = raw.get("location") or {}
    return Probe(
        country=str(loc.get("country", "")),
        city=loc.get("city"),
        asn=loc.get("asn"),
        network=loc.get("network"),
        tags=list(raw.get("tags") or []),
    )


def parse_probes(payload: Any) -> list[Probe]:
    """Parse the ``/v1/probes`` payload into :class:`Probe` objects."""
    items = payload if isinstance(payload, list) else (payload or {}).get("results", [])
    probes: list[Probe] = []
    for raw in items or []:
        if isinstance(raw, dict):
            probes.append(_probe_from_raw(raw))
    return probes


def fetch_probes(
    user_agent: str = DEFAULT_USER_AGENT, timeout: float = 25.0
) -> list[Probe]:
    """Fetch the current Globalping probe list."""
    req = urllib.request.Request(
        PROBES_URL, headers={"Accept": "application/json", "User-Agent": user_agent}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8", "replace"))
    return parse_probes(data)


def discover_probes(
    user_agent: str = DEFAULT_USER_AGENT, timeout: float = 25.0
) -> list[Probe]:
    """Discover all currently available Iranian Globalping probes."""
    return [p for p in fetch_probes(user_agent=user_agent, timeout=timeout) if p.is_iran]


# -------------------------------------------------------------------- client
class GlobalpingError(RuntimeError):
    pass


class GlobalpingClient:
    """Thin client over the Globalping measurement API.

    The API is asynchronous: creating a measurement returns an ``id``; we poll
    ``GET /v1/measurements/<id>`` until ``status`` becomes ``finished``.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 25.0,
        poll_interval: float = 3.0,
        max_polls: int = 12,
        min_interval: float = 1.5,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.max_polls = max_polls
        self.min_interval = min_interval
        self._last = 0.0

    def _throttle(self) -> None:
        delta = time.time() - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.time()

    def _get_json(self, url: str) -> Any:
        req = urllib.request.Request(
            url, headers={"Accept": "application/json", "User-Agent": self.user_agent}
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def _post_json(self, url: str, payload: dict) -> Any:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))

    def create(self, payload: dict) -> str:
        """Create a measurement and return its id."""
        self._throttle()
        try:
            data = self._post_json(MEASUREMENTS_URL, payload)
        except urllib.error.HTTPError as exc:
            raise GlobalpingError(f"create measurement failed: http {exc.code}") from exc
        except Exception as exc:  # network hiccup
            raise GlobalpingError(f"create measurement failed: {redact(str(exc))}") from exc
        if not isinstance(data, dict) or not data.get("id"):
            raise GlobalpingError("create measurement returned no id")
        return str(data["id"])

    def poll(self, measurement_id: str) -> dict[str, Any]:
        """Poll until the measurement finishes, or the poll budget is exhausted."""
        url = f"{MEASUREMENTS_URL}/{measurement_id}"
        last: dict[str, Any] = {}
        for _ in range(self.max_polls):
            time.sleep(self.poll_interval)
            try:
                last = self._get_json(url)
            except Exception:
                continue
            if isinstance(last, dict) and last.get("status") == "finished":
                return last
        return last if isinstance(last, dict) else {}

    def measure(self, payload: dict) -> tuple[str, dict[str, Any]]:
        measurement_id = self.create(payload)
        return measurement_id, self.poll(measurement_id)


# ------------------------------------------------------------- classification
def classify_http_result(result: dict[str, Any]) -> ProbeCheck | None:
    """Classify a Globalping HTTP measurement result into the taxonomy.

    The strongest observed stage wins: a real HTTP response outranks a TLS
    handshake, which outranks a bare TCP connect, which outranks DNS. Any of
    these is still non-publishable reachability evidence.
    """
    if not isinstance(result, dict):
        return None
    timings = result.get("timings") or {}
    resolved = result.get("resolvedAddress")
    status = result.get("status")
    status_code = result.get("statusCode")

    # Only report latency for a stage that actually completed; a timed-out
    # measurement reports its full timeout budget, which is not a latency.
    latency_ms: float | None = None
    for key in ("firstByte", "tls", "tcp"):
        value = timings.get(key)
        if isinstance(value, (int, float)):
            latency_ms = float(value)
            break

    tls_done = bool(timings.get("tls")) or bool(result.get("tls"))
    if status == "finished" and status_code is not None:
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True,
            classification=cfg.IRAN_HTTP_REACHABLE, latency_ms=latency_ms,
            tls=tls_done, status_code=status_code,
        )
    if tls_done:
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True,
            classification=cfg.IRAN_TLS_OK, latency_ms=latency_ms,
            tls=True, status_code=status_code,
        )
    if timings.get("tcp"):
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True,
            classification=cfg.IRAN_TCP_REACHABLE, latency_ms=latency_ms,
        )
    if resolved:
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True,
            classification=cfg.IRAN_DNS_OK, latency_ms=latency_ms,
        )
    raw = str(result.get("rawOutput", ""))
    cls = cfg.IRAN_TIMEOUT if "time" in raw.lower() else cfg.IRAN_UNREACHABLE
    return ProbeCheck(
        city=None, asn=None, network=None, ok=False,
        classification=cls, detail=raw[:200] or "no response",
    )


# --------------------------------------------------------------- orchestration
def _protocol_for(conf: Config) -> str:
    """Pick a Globalping HTTP protocol for the configuration's port.

    A TLS-terminating port is probed with HTTPS so we can observe a real
    handshake; a plaintext proxy port is probed with HTTP. Both still yield a
    TCP stage, so a non-TLS server is never misreported as unreachable.
    """
    if conf.protocol in ("http", "socks"):
        return "HTTP"
    return "HTTPS"


def _is_udp_protocol(conf: Config) -> bool:
    return conf.protocol in ("hysteria2", "tuic")


def build_measurement_payload(conf: Config, limit: int, city: str | None = None) -> dict[str, Any]:
    """Build a Globalping measurement payload for a configuration.

    UDP-based protocols (Hysteria2, TUIC) are probed with ICMP ping: an HTTP
    client cannot speak their transport, but an ICMP echo still tells us whether
    the server host is reachable from an Iranian network at all.
    """
    location = {"country": "IR", "city": city} if city else {"country": "IR"}
    if _is_udp_protocol(conf):
        return {
            "type": "ping",
            "target": conf.host,
            "locations": [location],
            "limit": max(1, int(limit)),
        }
    options: dict[str, Any] = {"protocol": _protocol_for(conf)}
    if conf.port:
        options["port"] = conf.port
    return {
        "type": "http",
        "target": conf.host,
        "locations": [location],
        "limit": max(1, int(limit)),
        "measurementOptions": options,
    }


def classify_ping_result(result: dict[str, Any]) -> ProbeCheck | None:
    """Classify a Globalping ICMP ping result."""
    if not isinstance(result, dict):
        return None
    stats = result.get("stats") or {}
    timings = result.get("timings") or []
    received = stats.get("rcv")
    if result.get("status") == "finished" and received:
        latency = stats.get("avg")
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True,
            classification=cfg.IRAN_ICMP_REACHABLE,
            latency_ms=float(latency) if isinstance(latency, (int, float)) else None,
        )
    if timings:
        return ProbeCheck(
            city=None, asn=None, network=None, ok=True, classification=cfg.IRAN_ICMP_REACHABLE
        )
    raw = str(result.get("rawOutput", ""))
    cls = cfg.IRAN_TIMEOUT if "time" in raw.lower() else cfg.IRAN_UNREACHABLE
    return ProbeCheck(
        city=None, asn=None, network=None, ok=False,
        classification=cls, detail=raw[:200] or "no response",
    )


def _apply_results(record: GlobalpingRecord, response: dict[str, Any]) -> None:
    is_udp = record.protocol in ("hysteria2", "tuic")
    classifier = classify_ping_result if is_udp else classify_http_result
    for item in response.get("results", []) or []:
        probe = item.get("probe") or {}
        check = classifier(item.get("result") or {})
        if check is None:
            continue
        check.city = probe.get("city")
        check.asn = probe.get("asn")
        check.network = probe.get("network")
        record.checks.append(check)
        if check.classification in (cfg.IRAN_TLS_OK, cfg.IRAN_HTTP_REACHABLE) and check.tls:
            record.tls_verified = True


def test_config(
    conf: Config,
    client: GlobalpingClient,
    limit: int = 2,
    city: str | None = None,
) -> GlobalpingRecord:
    """Test one configuration's server from Iranian Globalping probes.

    Never raises for a per-probe failure; failures are recorded as results.
    """
    record = GlobalpingRecord(
        fingerprint=conf.fingerprint,
        host=conf.host,
        port=conf.port,
        protocol=conf.protocol,
    )
    if _is_udp_protocol(conf):
        record.note = "UDP-based protocol; probed with ICMP ping (transport cannot be exercised)."
    if not is_valid_target(conf.host):
        record.note = "host is not a valid measurement target"
        return record
    try:
        measurement_id, response = client.measure(build_measurement_payload(conf, limit, city))
    except GlobalpingError as exc:
        log.warning("globalping measurement failed", extra={"context": {"fp": conf.fingerprint, "err": str(exc)}})
        record.note = redact(str(exc))
        return record
    record.measurement_id = measurement_id
    _apply_results(record, response)
    _summarize(record)
    return record


def _summarize(record: GlobalpingRecord) -> None:
    """Aggregate per-probe checks into a per-configuration summary.

    The summary is the strongest reachability signal observed and is never
    ``IRAN_FULL_TUNNEL_VERIFIED`` — that can only come from the Iran probe.
    """
    reachable: set[str] = set()
    unreachable: set[str] = set()
    best = cfg.IRAN_UNREACHABLE
    for check in record.checks:
        city = check.city or "unknown"
        if check.ok:
            reachable.add(city)
            if _REACH_RANK.get(check.classification, 0) > _REACH_RANK.get(best, 0):
                best = check.classification
        else:
            unreachable.add(city)
    record.cities_reachable = sorted(reachable)
    record.cities_unreachable = sorted(unreachable - reachable)
    record.summary = best


# --------------------------------------------------------------------- storage
def results_path(state_dir) -> Path:
    return Path(state_dir) / "globalping_results.json"


def save_results(state_dir, records: list[GlobalpingRecord], keep_per_fingerprint: int = 5) -> Path:
    path = results_path(state_dir)
    existing = read_json(path, {"records": []})
    history: dict[str, list] = {}
    for item in (existing.get("records", []) if isinstance(existing, dict) else []):
        fp = item.get("fingerprint")
        if fp:
            history.setdefault(fp, []).append(item)
    for record in records:
        history.setdefault(record.fingerprint, []).append(record.to_dict())
    trimmed: list[dict] = []
    for items in history.values():
        trimmed.extend(items[-keep_per_fingerprint:])
    payload = {"updated_at": iso(utcnow()), "count": len(trimmed), "records": trimmed}
    _atomic_write_json(path, payload)
    return path


def load_results(state_dir) -> list[dict]:
    raw = read_json(results_path(state_dir), {"records": []})
    return list(raw.get("records", [])) if isinstance(raw, dict) else list(raw)


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
    tls_verified = 0
    for rec in latest.values():
        proto = rec.get("protocol", "unknown")
        bucket = by_protocol.setdefault(proto, {"tested": 0, "reachable": 0})
        bucket["tested"] += 1
        summary = rec.get("summary", cfg.IRAN_UNREACHABLE)
        by_summary[summary] = by_summary.get(summary, 0) + 1
        if summary in cfg.GLOBALPING_REACHABLE:
            bucket["reachable"] += 1
        if rec.get("tls_verified"):
            tls_verified += 1
        for city in rec.get("cities_reachable", []) or []:
            by_city.setdefault(city, {"reachable": 0, "unreachable": 0})["reachable"] += 1
        for city in rec.get("cities_unreachable", []) or []:
            by_city.setdefault(city, {"reachable": 0, "unreachable": 0})["unreachable"] += 1
    return {
        "configs_tested": len(latest),
        "tls_verified": tls_verified,
        "by_summary": by_summary,
        "by_protocol": by_protocol,
        "by_city": by_city,
    }


def select_sample(configs: dict[str, Config], max_batch: int) -> list[Config]:
    """Pick a protocol-diverse sample of candidate configurations."""
    chosen: list[Config] = []
    seen: set[str] = set()
    for conf in configs.values():
        if conf.status in (cfg.DUPLICATE, cfg.EXPIRED):
            continue
        if conf.protocol not in seen:
            chosen.append(conf)
            seen.add(conf.protocol)
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


def run_globalping_round(configs: dict[str, Config], settings, store) -> dict[str, Any]:
    """Run one diagnostic Globalping round from Iranian probes.

    Best-effort: a Globalping outage must not affect the subscription pipeline.
    Records results but does **not** modify configuration status — Globalping
    cannot promote anything to ``WORKING``.
    """
    result: dict[str, Any] = {
        "enabled": bool(getattr(settings, "globalping_enabled", False)),
        "probes": 0,
        "cities": [],
        "tested": 0,
        "error": None,
    }
    if not result["enabled"]:
        result["note"] = "globalping diagnostics disabled"
        return result

    try:
        probes = discover_probes(user_agent=settings.user_agent)
    except Exception as exc:
        result["error"] = redact(str(exc))
        log.warning("globalping probe discovery failed", extra={"context": {"err": str(exc)}})
        return result

    result["probes"] = len(probes)
    result["cities"] = sorted({p.city for p in probes if p.city})
    if not probes:
        result["note"] = "no Iranian Globalping probes available"
        return result

    store.save_globalping_probes(
        {
            "updated_at": iso(utcnow()),
            "probes": [p.to_dict() for p in probes],
            "cities": result["cities"],
        }
    )

    batch = int(getattr(settings, "globalping_batch", 10))
    limit = int(getattr(settings, "globalping_limit", 2))
    sample = select_sample(configs, batch)
    client = GlobalpingClient(
        user_agent=settings.user_agent,
        timeout=float(getattr(settings, "globalping_timeout", 60.0)),
        min_interval=float(getattr(settings, "globalping_min_interval", 1.5)),
    )
    records: list[GlobalpingRecord] = []
    for conf in sample:
        try:
            records.append(test_config(conf, client, limit=limit))
        except Exception as exc:  # never let diagnostics break the cycle
            log.warning("globalping test failed", extra={"context": {"fp": conf.fingerprint, "err": str(exc)}})
    save_results(store.state_dir, records)
    result["tested"] = len(records)
    result["summary"] = summarize_records(load_results(store.state_dir))
    return result
