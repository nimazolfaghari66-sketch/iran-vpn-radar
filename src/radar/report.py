"""Machine-readable status reporting.

Two report tiers:

* **internal** (``data/`` / stdout) — full detail for the operator, still free
  of secrets, private IPs and runtime infrastructure details.
* **public** (``status/summary.json``) — safe aggregate statistics only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import config as cfg
from . import quality
from .models import iso, utcnow
from .storage import read_json

SAFE_STATES = cfg.ALL_STATES


def _checkhost_aggregate(settings) -> dict[str, Any]:
    """Safe Check-Host aggregate: counts and cities only, no per-config data."""
    try:
        from . import checkhost

        records = checkhost.load_results(settings.state_dir)
    except Exception:
        return {"available": False}
    summary = checkhost.summarize_records(records)
    return {
        "available": True,
        "configs_tested": summary.get("configs_tested", 0),
        "by_summary": summary.get("by_summary", {}),
        "by_city": summary.get("by_city", {}),
        "by_protocol": summary.get("by_protocol", {}),
        "note": (
            "Check-Host Iranian nodes report reachability only; results are "
            "diagnostic and never publishable. Only the Iran probe can verify a tunnel."
        ),
    }


def _globalping_aggregate(settings) -> dict[str, Any]:
    """Safe Globalping aggregate: counts and cities only, no per-config data."""
    try:
        from . import globalping

        records = globalping.load_results(settings.state_dir)
        probes = globalping.parse_probes(store_probes(settings))
    except Exception:
        return {"available": False}
    summary = globalping.summarize_records(records)
    return {
        "available": True,
        "probes": len([p for p in probes if p.is_iran]),
        "configs_tested": summary.get("configs_tested", 0),
        "tls_verified": summary.get("tls_verified", 0),
        "by_summary": summary.get("by_summary", {}),
        "by_city": summary.get("by_city", {}),
        "by_protocol": summary.get("by_protocol", {}),
        "note": (
            "Globalping Iranian probes run a real HTTP/TLS client, so a TLS handshake "
            "from Iran is observed. Results are diagnostic and never publishable; only "
            "the Iran probe can verify a tunnel."
        ),
    }


def _tunnel_aggregate(settings, configs: dict) -> dict[str, Any]:
    """Safe aggregate of the global (non-Iranian) tunnel-verification tier."""
    try:
        from . import tunnel_verify

        cand = tunnel_verify.summarize_candidates(configs)
    except Exception:
        return {"available": False}
    return {
        "available": True,
        "candidates": cand.get("total", 0),
        "iran_reachable": cand.get("iran_reachable", 0),
        "by_protocol": cand.get("by_protocol", {}),
        "note": (
            "Configurations whose tunnel was verified from this engine host (NOT Iran). "
            "Ranked by Iranian reachability evidence; published only to the candidate pool, "
            "never to the Iran-verified files."
        ),
    }


def store_probes(settings) -> list:
    """Load the cached Globalping probe list (best-effort)."""
    raw = read_json(settings.state_dir / "globalping_probes.json", {})
    return list(raw.get("probes", [])) if isinstance(raw, dict) else []


def build_summary(
    settings,
    configs: dict,
    sources: dict,
    probe_health: dict,
    publish_result: dict | None,
    cycle_stats: dict,
    runs: list[dict] | None = None,
) -> dict[str, Any]:
    """Build the full internal summary (safe to log; contains no secrets)."""
    stats = quality.stats(configs)
    last_success = max((c.last_success_at for c in configs.values() if c.last_success_at), default=None)
    runs = runs or []
    last_run = runs[-1] if runs else {}

    return {
        "generated_at": iso(utcnow()),
        "repository": f"{settings.owner}/{settings.repo}",
        "branch": settings.branch,
        "last_discovery_time": last_run.get("finished_at"),
        "last_iran_test_time": last_success,
        "last_publish_time": (publish_result or {}).get("published_at") or last_run.get("finished_at"),
        "sources": {
            "total": len(sources),
            "ok": sum(1 for s in sources.values() if s.last_status == "ok"),
            "error": sum(1 for s in sources.values() if s.last_status == "error"),
        },
        "configurations": {
            "total": stats["total"],
            "publishable": stats["publishable"],
            "working": stats["by_state"].get(cfg.WORKING, 0),
            "degraded": stats["by_state"].get(cfg.DEGRADED, 0),
            "failed": stats["by_state"].get(cfg.FAILED, 0),
            "expired": stats["by_state"].get(cfg.EXPIRED, 0),
            "pending_iran_test": stats["by_state"].get(cfg.PENDING_IRAN_TEST, 0),
            "duplicate": stats["by_state"].get(cfg.DUPLICATE, 0),
            "by_protocol": stats["by_protocol"],
        },
        "cycle": cycle_stats,
        "probe": probe_health,
        "checkhost": _checkhost_aggregate(settings),
        "globalping": _globalping_aggregate(settings),
        "tunnel": _tunnel_aggregate(settings, configs),
        "publish": publish_result or {"ok": None, "note": "not run"},
    }


def public_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Strip everything that must not appear in the public repository."""
    configs = summary.get("configurations", {})
    probe = summary.get("probe", {})
    publish = summary.get("publish", {})
    return {
        "generated_at": summary.get("generated_at"),
        "repository": summary.get("repository"),
        "protocols": list(cfg.PROTOCOLS),
        "sources_total": summary.get("sources", {}).get("total", 0),
        "configs": {
            "total": configs.get("total", 0),
            "working": configs.get("working", 0),
            "degraded": configs.get("degraded", 0),
            "pending_iran_test": configs.get("pending_iran_test", 0),
            "by_protocol": configs.get("by_protocol", {}),
        },
        "candidates": _public_tunnel(summary.get("tunnel", {})),
        "iran_testing": {
            "available": bool(probe.get("is_iran")),
            "verified_configs": probe.get("verified_configs", 0),
            "last_verified_test": probe.get("last_verified_test"),
        },
        "last_publish_ok": publish.get("ok"),
        "cycle": {
            "configs_added": summary.get("cycle", {}).get("added", 0),
            "configs_removed": summary.get("cycle", {}).get("removed", 0),
        },
        "checkhost": _public_checkhost(summary.get("checkhost", {})),
        "globalping": _public_globalping(summary.get("globalping", {})),
    }


def _public_globalping(gp: dict[str, Any]) -> dict[str, Any]:
    """Aggregate-only Globalping view: no hostnames, IPs or per-config rows."""
    if not gp or not gp.get("available"):
        return {"available": False}
    return {
        "available": True,
        "probes": gp.get("probes", 0),
        "configs_tested": gp.get("configs_tested", 0),
        "tls_verified": gp.get("tls_verified", 0),
        "by_summary": gp.get("by_summary", {}),
        "by_city": gp.get("by_city", {}),
        "note": (
            "Iranian Globalping probes observe DNS/TCP/TLS reachability from Iran. "
            "Diagnostic only; never used to publish a configuration."
        ),
    }


def _public_tunnel(t: dict[str, Any]) -> dict[str, Any]:
    """Aggregate-only view of the global tunnel-verified candidate pool."""
    if not t or not t.get("available"):
        return {"available": False, "total": 0, "by_protocol": {}}
    return {
        "available": True,
        "total": t.get("candidates", 0),
        "iran_reachable": t.get("iran_reachable", 0),
        "by_protocol": t.get("by_protocol", {}),
        "note": t.get("note"),
    }


def _public_checkhost(ch: dict[str, Any]) -> dict[str, Any]:
    """Aggregate-only Check-Host view: no hostnames, IPs or per-config rows."""
    if not ch or not ch.get("available"):
        return {"available": False}
    return {
        "available": True,
        "configs_tested": ch.get("configs_tested", 0),
        "by_summary": ch.get("by_summary", {}),
        "by_city": ch.get("by_city", {}),
        "note": (
            "Iranian Check-Host nodes measure reachability from Iran only. "
            "These results are diagnostic and never used to publish a configuration."
        ),
    }


def write_reports(settings, summary: dict, cycle: dict) -> list[Path]:
    """Write both report tiers. Returns written paths."""
    import json

    from .generate import _atomic_write_text

    written: list[Path] = []
    settings.status_dir.mkdir(parents=True, exist_ok=True)

    summary_path = settings.status_dir / "summary.json"
    _atomic_write_text(summary_path, json.dumps(public_summary(summary), ensure_ascii=False, indent=2) + "\n")
    written.append(summary_path)

    cycle_path = settings.status_dir / "latest-cycle.json"
    _atomic_write_text(cycle_path, json.dumps(cycle, ensure_ascii=False, indent=2) + "\n")
    written.append(cycle_path)

    internal_path = settings.state_dir / "summary.internal.json"
    internal_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(internal_path, json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    written.append(internal_path)

    return written


def load_public_summary(status_dir: Path) -> dict:
    return read_json(Path(status_dir) / "summary.json", {})
