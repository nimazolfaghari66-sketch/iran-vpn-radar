"""Iran test orchestration.

This module is the *only* place where a configuration may become ``WORKING``.
It enforces the project's hard rule: a configuration is published as
Iran-verified **only** when a probe physically located in Iran returned a
successful, real connection test. There is no fallback that labels a
foreign-location or local test as Iranian.

When no probe is available every eligible configuration stays
``PENDING_IRAN_TEST`` and the missing dependency is reported explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from . import config as cfg
from . import quality
from .logging_setup import get_logger, redact
from .models import Config, iso, parse_iso, utcnow
from .probe_protocol import (
    NullProbe,
    ProbeClient,
    ProbeInfo,
    ProbeUnavailable,
    TestOutcome,
    config_to_probe_item,
    validate_result,
)

log = get_logger("radar.iran")


@dataclass
class IranTestReport:
    """Result of one Iran testing round."""

    status: str  # "tested" | "unavailable" | "error"
    probe: ProbeInfo | None = None
    tested: int = 0
    passed: int = 0
    failed: int = 0
    pending: int = 0
    message: str = ""
    results: list[TestOutcome] = field(default_factory=list)
    tested_at: str = field(default_factory=lambda: iso(utcnow()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "probe": self.probe.to_dict() if self.probe else None,
            "probe_is_iran": bool(self.probe and self.probe.is_iran),
            "tested": self.tested,
            "passed": self.passed,
            "failed": self.failed,
            "pending": self.pending,
            "message": self.message,
            "tested_at": self.tested_at,
        }


def build_client(settings) -> ProbeClient | NullProbe:
    """Construct a probe client from settings, or a NullProbe when unset.

    ``IRAN_RADAR_PROBE_MODE`` values:

    * ``remote``      — talk to ``IRAN_PROBE_URL`` (a real Iran based agent)
    * ``local_iran``  — the runner itself is inside Iran and may test directly
    * ``unavailable`` — no Iran testing possible (default); configs stay pending
    """
    mode = settings.probe_mode
    if mode == "remote" and settings.probe_url and settings.probe_token:
        return ProbeClient(settings.probe_url, settings.probe_token, timeout=settings.probe_timeout)
    if mode == "local_iran":
        # Handled by the local probe runner, which sets its own country to IR.
        return NullProbe()
    return NullProbe()


def _probe_info_local_iran(settings) -> ProbeInfo:
    return ProbeInfo(
        name="local-iran-runner",
        country="IR",
        city=None,
        version="1.0.0",
        checked_at=iso(utcnow()),
    )


def run_iran_tests(
    configs: dict[str, Config],
    settings,
    max_batch: int = 60,
) -> IranTestReport:
    """Run one Iran testing round against the eligible configurations.

    Returns an :class:`IranTestReport` describing exactly what happened. When no
    probe is available, eligible configs are marked ``PENDING_IRAN_TEST`` and
    nothing is published as verified.
    """
    selected = quality.select_for_testing(configs, max_batch)
    if not selected:
        return IranTestReport(status="tested", tested=0, message="nothing eligible for testing")

    client = build_client(settings)

    # ---- No probe: mark pending, report the missing dependency honestly.
    if isinstance(client, NullProbe) and settings.probe_mode != "local_iran":
        for conf in selected:
            quality.mark_pending(conf)
        report = IranTestReport(
            status="unavailable",
            tested=0,
            pending=len(selected),
            message=(
                "No Iran based probe configured. Set IRAN_RADAR_PROBE_MODE=remote with "
                "IRAN_PROBE_URL and IRAN_PROBE_TOKEN, or run the engine with "
                "IRAN_RADAR_PROBE_MODE=local_iran on a host physically inside Iran. "
                "Configurations remain PENDING_IRAN_TEST and are not published as verified."
            ),
        )
        log.warning("iran testing unavailable", extra={"context": report.to_dict()})
        return report

    # ---- Local runner that is physically inside Iran.
    if settings.probe_mode == "local_iran":
        from .local_probe import run_local_tests

        probe = _probe_info_local_iran(settings)
        if not settings.local_is_iran:
            for conf in selected:
                quality.mark_pending(conf)
            return IranTestReport(
                status="unavailable",
                probe=probe,
                pending=len(selected),
                message=(
                    "IRAN_RADAR_PROBE_MODE=local_iran requires IRAN_RADAR_LOCAL_IS_IRAN=1. "
                    "Refusing to label non-Iranian tests as Iranian."
                ),
            )
        outcomes = run_local_tests(selected, probe)
        return _apply_outcomes(configs, outcomes, probe)

    # ---- Remote probe.
    try:
        probe = client.health()
    except ProbeUnavailable as exc:
        for conf in selected:
            quality.mark_pending(conf)
        return IranTestReport(
            status="error",
            tested=0,
            pending=len(selected),
            message=f"Iran probe unreachable: {redact(str(exc))}",
        )

    if probe is None or not probe.is_iran:
        for conf in selected:
            quality.mark_pending(conf)
        country = probe.country if probe else "unknown"
        return IranTestReport(
            status="error",
            probe=probe,
            tested=0,
            pending=len(selected),
            message=f"Probe did not identify as Iran based (country={country!r}); results rejected.",
        )

    items = [config_to_probe_item(c) for c in selected]
    try:
        response = client.test(
            items,
            options={
                "stages": ["dns", "reachability", "handshake", "tunnel", "internet", "latency", "download", "stability"],
                "download_bytes": 1_000_000,
                "stability_seconds": 10,
            },
        )
    except ProbeUnavailable as exc:
        for conf in selected:
            quality.mark_pending(conf)
        return IranTestReport(
            status="error", probe=probe, tested=0, pending=len(selected),
            message=f"Iran probe test call failed: {redact(str(exc))}",
        )

    outcomes = _parse_outcomes(response, probe)
    return _apply_outcomes(configs, outcomes, probe)


def _parse_outcomes(response: dict[str, Any], probe: ProbeInfo) -> list[TestOutcome]:
    outcomes: list[TestOutcome] = []
    for result in response.get("results", []):
        ok, reason = validate_result(result, probe)
        outcomes.append(
            TestOutcome(
                fingerprint=str(result.get("fingerprint", "")),
                success=bool(result.get("success")) and ok,
                probe_is_iran=probe.is_iran and ok,
                latency_ms=result.get("latency_ms"),
                download_kbps=result.get("download_kbps"),
                grade=result.get("grade"),
                error=None if ok else reason,
                stages=result.get("stages", {}) or {},
                raw={k: v for k, v in result.items() if k not in ("uri",)},
            )
        )
    return outcomes


def _apply_outcomes(
    configs: dict[str, Config], outcomes: list[TestOutcome], probe: ProbeInfo
) -> IranTestReport:
    passed = failed = 0
    for outcome in outcomes:
        conf = configs.get(outcome.fingerprint)
        if conf is None:
            continue
        tested_at = utcnow()
        if outcome.success and outcome.probe_is_iran:
            quality.apply_success(
                conf,
                {"latency_ms": outcome.latency_ms, "download_kbps": outcome.download_kbps, "grade": outcome.grade},
                when=tested_at,
            )
            passed += 1
        else:
            expired = bool(outcome.raw.get("expired"))
            quality.apply_failure(conf, error=outcome.error or "test failed", when=tested_at, expired=expired)
            failed += 1
    return IranTestReport(
        status="tested",
        probe=probe,
        tested=len(outcomes),
        passed=passed,
        failed=failed,
        message=f"Iran probe tested {len(outcomes)} configurations ({passed} passed).",
        results=outcomes,
    )


def probe_health(configs: dict[str, Config], settings) -> dict[str, Any]:
    """Health snapshot for the Iran probe, for the internal status report."""
    client = build_client(settings)
    info: dict[str, Any] = {
        "mode": settings.probe_mode,
        "configured": bool(getattr(client, "configured", False)),
        "is_iran": False,
        "reachable": False,
        "pending_configs": sum(1 for c in configs.values() if c.status == cfg.PENDING_IRAN_TEST),
        "verified_configs": sum(1 for c in configs.values() if c.status == cfg.WORKING),
        "last_verified_test": max(
            (c.last_success_at for c in configs.values() if c.last_success_at), default=None
        ),
    }
    if settings.probe_mode == "local_iran":
        info.update({"reachable": settings.local_is_iran, "is_iran": settings.local_is_iran, "name": "local-iran-runner"})
        return info
    if isinstance(client, NullProbe):
        info["message"] = "No Iran probe configured"
        return info
    try:
        probe = client.health()
    except ProbeUnavailable as exc:
        info["message"] = redact(str(exc))
        return info
    if probe:
        info.update({"reachable": True, "is_iran": probe.is_iran, **probe.to_dict()})
    return info
