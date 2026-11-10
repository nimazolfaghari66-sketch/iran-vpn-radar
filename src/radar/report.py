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
