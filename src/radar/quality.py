"""Configuration quality state machine (specification section 7).

Failure policy:

* first consecutive failure  -> ``DEGRADED`` (retained, still published)
* second consecutive failure -> ``FAILED``  (removed from published output)
* confirmed expiry / invalid -> ``EXPIRED`` (removed from published output)
* successful retest          -> ``WORKING`` (restored to published output)
"""

from __future__ import annotations

from datetime import datetime

from . import config as cfg
from .models import Config, iso, utcnow


def is_publishable(conf: Config) -> bool:
    return conf.status in cfg.PUBLISHABLE_STATES


def apply_success(conf: Config, result: dict, when: datetime | None = None) -> None:
    """Apply a positive Iran test result."""
    when = when or utcnow()
    conf.status = cfg.WORKING
    conf.consecutive_failures = 0
    conf.test_count += 1
    conf.success_count += 1
    conf.last_success_at = iso(when)
    conf.last_test_at = iso(when)
    conf.last_error = None
    if result.get("latency_ms") is not None:
        conf.last_latency_ms = float(result["latency_ms"])
    if result.get("download_kbps") is not None:
        conf.last_download_kbps = float(result["download_kbps"])
    if result.get("grade"):
        conf.last_grade = str(result["grade"])


def apply_failure(conf: Config, error: str | None = None, when: datetime | None = None, expired: bool = False) -> None:
    """Apply a negative Iran test result and advance the failure policy."""
    when = when or utcnow()
    conf.test_count += 1
    conf.last_test_at = iso(when)
    conf.last_failure_at = iso(when)
    conf.last_error = (error or "unknown")[:300]

    if expired:
        conf.status = cfg.EXPIRED
        conf.consecutive_failures += 1
        return

    conf.consecutive_failures += 1
    if conf.consecutive_failures <= 1:
        conf.status = cfg.DEGRADED
    else:
        conf.status = cfg.FAILED


def mark_pending(conf: Config) -> None:
    """Mark a configuration as awaiting a genuine Iran based test."""
    if conf.status in (cfg.DISCOVERED, cfg.TESTING):
        conf.status = cfg.PENDING_IRAN_TEST


def select_for_testing(configs: dict[str, Config], max_batch: int) -> list[Config]:
    """Choose which configurations to send to the probe this cycle.

    Priority order:

    1. never-tested configurations (``DISCOVERED`` / ``PENDING_IRAN_TEST``)
    2. previously degraded / failed configurations (retest)
    3. stalest working configurations (refresh)
    """
    fresh: list[Config] = []
    retest: list[Config] = []
    refresh: list[Config] = []
    for conf in configs.values():
        if conf.status == cfg.DUPLICATE:
            continue
        if conf.status in (cfg.DISCOVERED, cfg.PENDING_IRAN_TEST, cfg.TESTING):
            fresh.append(conf)
        elif conf.status in (cfg.DEGRADED, cfg.FAILED, cfg.EXPIRED):
            retest.append(conf)
        elif conf.status == cfg.WORKING:
            refresh.append(conf)

    def staleness(conf: Config) -> str:
        return conf.last_test_at or conf.discovered_at or ""

    retest.sort(key=staleness)
    refresh.sort(key=staleness)

    selected: list[Config] = []
    selected.extend(fresh[:max_batch])
    remaining = max_batch - len(selected)
    if remaining > 0:
        selected.extend(retest[:remaining])
        remaining = max_batch - len(selected)
    if remaining > 0:
        selected.extend(refresh[:remaining])
    return selected


def stats(configs: dict[str, Config]) -> dict:
    """Aggregate per-state and per-protocol counts."""
    by_state: dict[str, int] = {state: 0 for state in cfg.ALL_STATES}
    by_protocol: dict[str, dict[str, int]] = {}
    for conf in configs.values():
        by_state[conf.status] = by_state.get(conf.status, 0) + 1
        bucket = by_protocol.setdefault(conf.protocol, {"total": 0, "publishable": 0})
        bucket["total"] += 1
        if is_publishable(conf):
            bucket["publishable"] += 1
    return {
        "total": len(configs),
        "by_state": by_state,
        "by_protocol": by_protocol,
        "publishable": sum(1 for c in configs.values() if is_publishable(c)),
    }
