"""Global real-tunnel verification tier.

The Iran gate (see :mod:`radar.iran_probe`) is absolute: a configuration is
published in the Iran-verified subscription files *only* after a probe inside
Iran established a real tunnel. That gate is not touched here.

This module answers a different, honest question: **does this configuration
actually work as a VPN tunnel at all?** It launches a real protocol client
(``sing-box``/``xray``/``v2ray``), opens the tunnel and pushes real HTTPS
traffic through it. Because the engine host is not inside Iran, every result is
labelled ``GLOBAL`` — never ``IRAN`` — and configurations that pass are written
to a clearly separated **candidate** pool (``subscriptions/candidates/*``),
never to the Iran-verified files.

Candidates are *ranked* by the strongest Iranian evidence the system can obtain
(Globalping TLS/TCP reachability from Tehran/Tabriz), so the most Iran-plausible
tunnel-verified configurations surface first — but they are published as
"tunnel-verified (not Iran-verified)", never as Iranian tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import config as cfg
from .logging_setup import get_logger, redact
from .models import Config, iso, utcnow
from .storage import _atomic_write_json, read_json

log = get_logger("radar.tunnel")

# Dedicated tunnel-verification lifecycle, kept separate from ``Config.status``
# so the Iran gate's state machine is never affected by this tier.
TUNNEL_VERIFIED = "TUNNEL_VERIFIED"
TUNNEL_FAILED = "TUNNEL_FAILED"

# Ranking weight: a configuration seen reachable from Iran (Globalping) is far
# more plausible for Iranian users than one that only worked from a foreign host.
_IRAN_REACHABLE_CLASSIFICATIONS = {
    "IRAN_TLS_OK",
    "IRAN_HTTP_REACHABLE",
    "IRAN_TCP_REACHABLE",
    "IRAN_DNS_OK",
}
_GRADE_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}


@dataclass
class TunnelRecord:
    fingerprint: str
    protocol: str
    endpoint: str
    success: bool
    location: str = "GLOBAL"  # never "IRAN"
    latency_ms: float | None = None
    download_kbps: float | None = None
    grade: str | None = None
    stages: dict[str, bool] = field(default_factory=dict)
    error: str | None = None
    checked_at: str = field(default_factory=lambda: iso(utcnow()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "protocol": self.protocol,
            "endpoint": self.endpoint,
            "success": self.success,
            "location": self.location,
            "latency_ms": self.latency_ms,
            "download_kbps": self.download_kbps,
            "grade": self.grade,
            "stages": self.stages,
            "error": self.error,
            "checked_at": self.checked_at,
        }


def results_path(state_dir: Path) -> Path:
    return Path(state_dir) / "tunnel_tests.json"


def load_results(state_dir: Path) -> list[dict[str, Any]]:
    return read_json(results_path(state_dir), {"records": []}).get("records", [])


def save_results(state_dir: Path, records: list[TunnelRecord], keep_per_fingerprint: int = 5) -> Path:
    existing = load_results(state_dir)
    by_fp: dict[str, list[dict]] = {}
    for rec in existing + [r.to_dict() for r in records]:
        by_fp.setdefault(rec["fingerprint"], []).append(rec)
    trimmed: list[dict] = []
    for rows in by_fp.values():
        rows.sort(key=lambda r: r.get("checked_at") or "")
        trimmed.extend(rows[-keep_per_fingerprint:])
    trimmed.sort(key=lambda r: r.get("checked_at") or "")
    payload = {
        "note": (
            "GLOBAL real-tunnel verification. Not Iranian tests. "
            "Feeds the candidate pool only; never the Iran-verified files."
        ),
        "updated_at": iso(utcnow()),
        "count": len(trimmed),
        "records": trimmed,
    }
    path = results_path(state_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(path, payload)
    return path


def _iran_reachability_index(state_dir: Path) -> dict[str, str]:
    """Map fingerprint -> best Iranian reachability classification seen.

    Sourced from Globalping records (real HTTP/TLS observations from Iranian
    probes). Purely a *ranking* input; it can never promote a configuration.
    """
    index: dict[str, str] = {}
    payload = read_json(Path(state_dir) / "globalping_results.json", {"records": []})
    for rec in payload.get("records", []):
        fp = rec.get("fingerprint")
        summary = rec.get("summary")
        if fp and summary:
            index[fp] = summary
    return index


def select_candidates(configs: dict[str, Config], max_batch: int, iran_index: dict[str, str] | None = None) -> list[Config]:
    """Choose which configurations to tunnel-test this round.

    Priority:

    1. never-tunnel-tested configs that an Iranian probe (Globalping) already
       saw reachable — by far the highest hit rate, so we test these first;
    2. other never-tunnel-tested configs (protocol-diverse);
    3. previously tunnel-tested configs due for re-validation.

    Configurations already Iran-verified are skipped: they are strictly better
    and already published in the Iran-verified files.
    """
    iran_index = iran_index or {}
    iran_reachable: list[Config] = []
    fresh: list[Config] = []
    retest: list[Config] = []
    seen_proto: set[str] = set()

    for conf in configs.values():
        if conf.status == cfg.DUPLICATE or not conf.port or conf.status == cfg.WORKING:
            continue
        tested = getattr(conf, "tunnel_status", None)
        if tested:
            retest.append(conf)
            continue
        if iran_index.get(conf.fingerprint) in _IRAN_REACHABLE_CLASSIFICATIONS:
            iran_reachable.append(conf)
        else:
            fresh.append(conf)

    def _rank(conf: Config) -> tuple:
        # IPv4/domain first; keep deterministic ordering so cycles are stable.
        return (conf.host_kind, conf.protocol, conf.host, conf.port or 0, conf.fingerprint)

    iran_reachable.sort(key=_rank)
    fresh.sort(key=_rank)
    retest.sort(key=lambda c: getattr(c, "tunnel_verified_at", None) or c.last_tunnel_test_at or c.discovered_at or "")

    selected: list[Config] = []
    # 1. Iran-reachable first.
    selected.extend(iran_reachable[:max_batch])
    # 2. Then protocol-diverse fresh configs.
    if len(selected) < max_batch:
        for conf in fresh:
            if len(selected) >= max_batch:
                break
            if conf.protocol in seen_proto and len(selected) < max_batch // 2:
                continue
            selected.append(conf)
            seen_proto.add(conf.protocol)
        for conf in fresh:
            if len(selected) >= max_batch:
                break
            if conf not in selected:
                selected.append(conf)
    # 3. Then re-validation of previously tested configs.
    if len(selected) < max_batch:
        selected.extend(retest[: max_batch - len(selected)])
    return selected


def _apply_tunnel_result(conf: Config, success: bool, record: TunnelRecord) -> None:
    conf.tunnel_test_count = getattr(conf, "tunnel_test_count", 0) + 1
    conf.last_tunnel_test_at = record.checked_at
    if success:
        conf.tunnel_status = TUNNEL_VERIFIED
        conf.tunnel_consecutive_failures = 0
        conf.tunnel_verified_at = record.checked_at
        conf.tunnel_latency_ms = record.latency_ms
        conf.tunnel_download_kbps = record.download_kbps
        conf.tunnel_grade = record.grade
        conf.tunnel_last_error = None
    else:
        conf.tunnel_consecutive_failures = getattr(conf, "tunnel_consecutive_failures", 0) + 1
        conf.tunnel_last_error = (record.error or "tunnel test failed")[:300]
        # One transient failure does not drop a previously verified config; two
        # consecutive failures do (mirrors the Iran failure policy).
        if conf.tunnel_consecutive_failures >= 2 or conf.tunnel_status != TUNNEL_VERIFIED:
            conf.tunnel_status = TUNNEL_FAILED


def run_tunnel_round(configs: dict[str, Config], settings, store, max_batch: int = 40) -> dict[str, Any]:
    """Run one global real-tunnel verification round.

    Best-effort: a missing client binary or a single bad config never aborts the
    cycle. Returns an aggregate summary (safe for the public status file).
    """
    from .local_probe import find_client, run_tunnel_test

    result: dict[str, Any] = {
        "enabled": bool(getattr(settings, "tunnel_enabled", False)),
        "available": False,
        "client": None,
        "tested": 0,
        "passed": 0,
        "failed": 0,
        "error": None,
        "note": None,
    }
    if not result["enabled"]:
        result["note"] = "global tunnel verification disabled"
        return result

    client = find_client()
    if client is None:
        result["note"] = (
            "no VPN client binary installed (sing-box/xray/v2ray); "
            "global tunnel verification cannot run"
        )
        log.warning("tunnel verification skipped: no client binary")
        return result
    result["available"] = True
    result["client"] = client[0]

    iran_index = _iran_reachability_index(store.state_dir)
    selected = select_candidates(configs, max_batch, iran_index)
    if not selected:
        result["note"] = "nothing eligible for tunnel verification"
        return result

    for conf in selected:
        summary = iran_index.get(conf.fingerprint)
        if summary:
            conf.iran_reachability = summary
            conf.iran_reachability_at = iso(utcnow())

    options = {
        "download_bytes": int(getattr(settings, "tunnel_download_bytes", 500_000)),
        "stability_seconds": float(getattr(settings, "tunnel_stability_seconds", 4)),
    }
    workers = max(1, int(getattr(settings, "tunnel_workers", 8)))

    def _one(conf: Config) -> TunnelRecord:
        try:
            stages, raw, error = run_tunnel_test(conf, options)
            success = bool(raw.get("success"))
            return TunnelRecord(
                fingerprint=conf.fingerprint,
                protocol=conf.protocol,
                endpoint=conf.endpoint,
                success=success,
                location="GLOBAL",
                latency_ms=raw.get("latency_ms"),
                download_kbps=raw.get("download_kbps"),
                grade=raw.get("grade"),
                stages=stages.to_dict(),
                error=None if success else (error or "tunnel test failed"),
            )
        except Exception as exc:  # never let one bad config abort the round
            return TunnelRecord(
                fingerprint=conf.fingerprint,
                protocol=conf.protocol,
                endpoint=conf.endpoint,
                success=False,
                error=f"internal error: {redact(str(exc))}",
            )

    records: list[TunnelRecord] = []
    if workers > 1:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=workers) as pool:
            for record in pool.map(_one, selected):
                records.append(record)
    else:
        records = [_one(conf) for conf in selected]

    for record in records:
        conf = configs.get(record.fingerprint)
        if conf is not None:
            _apply_tunnel_result(conf, record.success, record)
        result["tested"] += 1
        result["passed" if record.success else "failed"] += 1

    save_results(store.state_dir, records)
    return result


def candidate_configs(configs: dict[str, Config]) -> list[Config]:
    """Configurations eligible for the candidate pool, ranked best-first.

    A candidate is any configuration with a *real, tunnel-verified* result from
    this tier. Ranking prefers Iranian evidence then tunnel quality.
    """
    chosen = [
        c
        for c in configs.values()
        if getattr(c, "tunnel_status", None) == TUNNEL_VERIFIED and c.status != cfg.DUPLICATE
    ]
    return sorted(chosen, key=rank_key)


def rank_key(conf: Config) -> tuple:
    """Sort key: Iran-verified, then Iran-reachable, then grade, then latency."""
    iran_verified = 0 if conf.status == cfg.WORKING else 1
    reach = getattr(conf, "iran_reachability", None)
    iran_reach = 0 if reach in _IRAN_REACHABLE_CLASSIFICATIONS else 1
    grade = _GRADE_RANK.get(getattr(conf, "tunnel_grade", None) or "D", 3)
    latency = getattr(conf, "tunnel_latency_ms", None) or 99999.0
    return (iran_verified, iran_reach, grade, latency, conf.protocol, conf.host, conf.port or 0, conf.fingerprint)


def summarize_candidates(configs: dict[str, Config]) -> dict[str, Any]:
    """Aggregate-only summary of the candidate pool (safe for the public file)."""
    candidates = candidate_configs(configs)
    by_protocol: dict[str, int] = {}
    iran_reachable = 0
    for conf in candidates:
        by_protocol[conf.protocol] = by_protocol.get(conf.protocol, 0) + 1
        if getattr(conf, "iran_reachability", None) in _IRAN_REACHABLE_CLASSIFICATIONS:
            iran_reachable += 1
    return {
        "total": len(candidates),
        "iran_reachable": iran_reachable,
        "by_protocol": by_protocol,
    }
