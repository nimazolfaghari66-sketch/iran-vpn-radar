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
import time
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
    shortage = _protocols_below_target(configs)
    iran_reachable: list[Config] = []
    fresh: list[Config] = []
    retest: list[Config] = []

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
        # Deterministic order so cycles are stable.
        return (conf.host_kind, conf.host, conf.port or 0, conf.fingerprint)

    iran_reachable.sort(key=_rank)
    fresh.sort(key=_rank)
    retest.sort(key=lambda c: getattr(c, "tunnel_verified_at", None) or c.last_tunnel_test_at or c.discovered_at or "")

    def _interleave(pool: list[Config], cap: int) -> list[Config]:
        """Round-robin across protocols, most-short protocol first.

        This guarantees a single batch samples every protocol still below
        target instead of exhausting one protocol's list.
        """
        buckets: dict[str, list[Config]] = {}
        for conf in pool:
            buckets.setdefault(conf.protocol, []).append(conf)
        # Biggest shortage first, then protocol name for determinism.
        order = sorted(buckets, key=lambda p: (-shortage.get(p, 0), p))
        out: list[Config] = []
        idx = {p: 0 for p in order}
        while len(out) < cap:
            progressed = False
            for p in order:
                if len(out) >= cap:
                    break
                i = idx[p]
                if i < len(buckets[p]):
                    out.append(buckets[p][i])
                    idx[p] = i + 1
                    progressed = True
            if not progressed:
                break
        return out

    selected: list[Config] = []
    # 1. Iran-reachable first (highest hit rate), interleaved across protocols.
    selected.extend(_interleave(iran_reachable, max_batch))
    # 2. Then other fresh configs, interleaved across protocols.
    if len(selected) < max_batch:
        chosen = {c.fingerprint for c in selected}
        rest = [c for c in _interleave(fresh, max_batch * 2) if c.fingerprint not in chosen]
        selected.extend(rest[: max_batch - len(selected)])
    # 3. Then re-validation of previously tested configs.
    if len(selected) < max_batch:
        chosen = {c.fingerprint for c in selected}
        rest = [c for c in retest if c.fingerprint not in chosen]
        selected.extend(rest[: max_batch - len(selected)])
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


def run_tunnel_rounds(
    configs: dict[str, Config],
    settings,
    store,
    min_batch: int | None = None,
    max_batch: int | None = None,
    time_budget_s: float | None = None,
) -> dict[str, Any]:
    """Run real tunnel tests, accumulating successes across rounds.

    The 200-test batch is a **minimum**, not a maximum. Each round:

    1. selects fresh (never-tunnel-tested) configurations, prioritising the
       protocols still below ``cfg.TARGET_PER_PROTOCOL``;
    2. runs real sing-box tunnel tests;
    3. **accumulates** every success into the healthy pool (never replaces a
       previously verified configuration with a new batch).

    Additional rounds keep running until every protocol has reached the target,
    or no untested configurations remain, or the time budget is exhausted —
    whichever comes first. Partial progress is always persisted, so the next
    cycle continues where this one stopped.

    Returns an aggregate summary (safe for the public status file).
    """
    min_batch = int(min_batch if min_batch is not None else getattr(settings, "tunnel_batch", 40))
    min_batch = max(min_batch, cfg.MIN_TUNNEL_BATCH)
    max_batch = int(max_batch if max_batch is not None else getattr(settings, "tunnel_max_batch", min_batch))
    max_batch = max(max_batch, min_batch)
    if time_budget_s is None:
        time_budget_s = float(getattr(settings, "tunnel_time_budget_s", 1800.0))

    started = time.monotonic()
    result: dict[str, Any] = {
        "enabled": bool(getattr(settings, "tunnel_enabled", False)),
        "available": False,
        "client": None,
        "rounds": 0,
        "tested": 0,
        "passed": 0,
        "failed": 0,
        "batch_min": min_batch,
        "time_budget_s": time_budget_s,
        "stop_reason": None,
        "error": None,
        "note": None,
    }
    if not result["enabled"]:
        result["note"] = "global tunnel verification disabled"
        return result

    from .local_probe import find_client

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

    while True:
        remaining = max_batch - result["tested"]
        if remaining <= 0:
            result["stop_reason"] = "max_batch_reached"
            break
        # Always allow at least the minimum batch, then respect the time budget.
        need_min = result["tested"] < min_batch
        if not need_min and (time.monotonic() - started) >= time_budget_s:
            result["stop_reason"] = "time_budget_reached"
            break

        round_batch = min(remaining, max(min_batch - result["tested"], 1) if need_min else remaining)
        round_batch = min(round_batch, remaining)
        round_result = run_tunnel_round(configs, settings, store, max_batch=round_batch)
        result["rounds"] += 1
        result["tested"] += round_result.get("tested", 0)
        result["passed"] += round_result.get("passed", 0)
        result["failed"] += round_result.get("failed", 0)

        if round_result.get("tested", 0) == 0:
            result["stop_reason"] = "no_untested_configs_left"
            break

        # Stop early only when every protocol has reached the target.
        if not _protocols_below_target(configs):
            result["stop_reason"] = "targets_reached"
            break

    if result["stop_reason"] is None:
        result["stop_reason"] = "completed"
    result["healthy_by_protocol"] = healthy_counts(configs)
    result["dashboard"] = build_dashboard(configs)
    log.info(
        "tunnel rounds complete",
        extra={"context": {"rounds": result["rounds"], "tested": result["tested"], "passed": result["passed"], "stop": result["stop_reason"]}},
    )
    return result


def healthy_counts(configs: dict[str, Config]) -> dict[str, int]:
    """Count genuinely working (tunnel-verified) configs per protocol."""
    counts = {proto: 0 for proto in cfg.PROTOCOLS}
    for conf in configs.values():
        if getattr(conf, "tunnel_status", None) == TUNNEL_VERIFIED and conf.status != cfg.DUPLICATE:
            counts[conf.protocol] = counts.get(conf.protocol, 0) + 1
    return counts


def _protocols_below_target(configs: dict[str, Config]) -> dict[str, int]:
    """Protocols with fewer healthy configs than the target (shortage > 0)."""
    counts = healthy_counts(configs)
    return {p: cfg.TARGET_PER_PROTOCOL - counts.get(p, 0) for p in cfg.PROTOCOLS if counts.get(p, 0) < cfg.TARGET_PER_PROTOCOL}


def build_dashboard(configs: dict[str, Config]) -> list[dict[str, Any]]:
    """Per-protocol dashboard: discovered, tested, successful, healthy, target,
    shortage, iran-priority count and the public subscription URL."""
    healthy = healthy_counts(configs)
    priority = {proto: 0 for proto in cfg.PROTOCOLS}
    for conf in iran_priority_configs(configs):
        priority[conf.protocol] = priority.get(conf.protocol, 0) + 1

    per_proto_total: dict[str, int] = {p: 0 for p in cfg.PROTOCOLS}
    per_proto_tested: dict[str, int] = {p: 0 for p in cfg.PROTOCOLS}
    per_proto_passed: dict[str, int] = {p: 0 for p in cfg.PROTOCOLS}
    for conf in configs.values():
        p = conf.protocol
        per_proto_total[p] = per_proto_total.get(p, 0) + 1
        if getattr(conf, "tunnel_test_count", 0):
            per_proto_tested[p] = per_proto_tested.get(p, 0) + 1
        if getattr(conf, "tunnel_status", None) == TUNNEL_VERIFIED:
            per_proto_passed[p] = per_proto_passed.get(p, 0) + 1

    rows: list[dict[str, Any]] = []
    for proto in cfg.PROTOCOLS:
        h = healthy.get(proto, 0)
        rows.append(
            {
                "protocol": proto,
                "discovered": per_proto_total.get(proto, 0),
                "tested": per_proto_tested.get(proto, 0),
                "successful": per_proto_passed.get(proto, 0),
                "healthy": h,
                "target": cfg.TARGET_PER_PROTOCOL,
                "shortage": max(0, cfg.TARGET_PER_PROTOCOL - h),
                "iran_priority": priority.get(proto, 0),
                "subscription": f"subscriptions/candidates/{proto}",
                "iran_priority_subscription": f"subscriptions/iran-priority/{proto}",
            }
        )
    return rows


def dashboard_maps(configs: dict[str, Config]) -> dict[str, dict[str, int]]:
    """Flat per-protocol maps (directly addressable from the public summary).

    These feed the README's dynamic badges, so every number shown there is the
    latest published value rather than a hand-copied figure.
    """
    rows = build_dashboard(configs)
    keys = ("discovered", "tested", "successful", "healthy", "target", "shortage", "iran_priority")
    return {
        key: {row["protocol"]: row[key] for row in rows}
        for key in keys
    }


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

    # Attach the latest Iranian reachability label to every config that has one,
    # not only the ones selected this round — it feeds candidate ranking.
    for conf in configs.values():
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


def has_positive_iran_reachability(conf: Config) -> bool:
    """True when an Iranian vantage point actually connected to this endpoint.

    Requires a TCP-handshake-or-better observation (see
    ``cfg.IRAN_PRIORITY_REACHABLE``). DNS-only or ICMP-only evidence does not
    qualify: neither proves the proxy port answers.
    """
    return getattr(conf, "iran_reachability", None) in cfg.IRAN_PRIORITY_REACHABLE


def evidence_level(conf: Config) -> str | None:
    """Strongest honest evidence label for a configuration, or ``None``."""
    if conf.status == cfg.WORKING and getattr(conf, "last_success_at", None):
        # Only the Iran probe sets WORKING; that is a real tunnel from Iran.
        return cfg.IRAN_FULL_TUNNEL_VERIFIED
    if getattr(conf, "tunnel_status", None) == TUNNEL_VERIFIED:
        if has_positive_iran_reachability(conf):
            return cfg.IRAN_PRIORITY_CANDIDATE
        return cfg.GLOBAL_TUNNEL_TESTED
    if has_positive_iran_reachability(conf):
        return cfg.IRAN_NETWORK_REACHABLE
    return None


def iran_priority_configs(configs: dict[str, Config]) -> list[Config]:
    """Category B: real global tunnel test **and** positive Iranian reachability.

    These are the strongest candidates obtainable without a probe inside Iran.
    They are ranked best-first and published to ``subscriptions/iran-priority/*``.
    They are explicitly **not** ``IRAN_FULL_TUNNEL_VERIFIED``.
    """
    chosen = [
        c
        for c in configs.values()
        if getattr(c, "tunnel_status", None) == TUNNEL_VERIFIED
        and c.status != cfg.DUPLICATE
        and has_positive_iran_reachability(c)
    ]
    return sorted(chosen, key=rank_key)


def summarize_priority(configs: dict[str, Config]) -> dict[str, Any]:
    """Aggregate-only summary of the Iran-priority pool (safe for publication)."""
    priority = iran_priority_configs(configs)
    by_protocol: dict[str, int] = {}
    for conf in priority:
        by_protocol[conf.protocol] = by_protocol.get(conf.protocol, 0) + 1
    return {"total": len(priority), "by_protocol": by_protocol}


def evidence_distribution(configs: dict[str, Config]) -> dict[str, int]:
    """Count configurations by their strongest evidence level (public-safe)."""
    counts = {level: 0 for level in cfg.EVIDENCE_LEVELS}
    for conf in configs.values():
        level = evidence_level(conf)
        if level:
            counts[level] += 1
    return counts
