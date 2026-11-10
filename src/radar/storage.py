"""Persistent state.

State is stored as pretty-printed JSON so it is reviewable and diff-friendly in
the public repository. All writes are atomic (temp file + rename) so an
interrupted cycle can never corrupt the previous good state.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .logging_setup import get_logger
from .models import Config, Source, iso, utcnow

log = get_logger("radar.storage")


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("state read failed, using default", extra={"context": {"path": str(path), "err": str(exc)}})
        return default


class Store:
    """Facade over the JSON state files."""

    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------- configs
    @property
    def configs_path(self) -> Path:
        return self.state_dir / "configs.json"

    @property
    def sources_path(self) -> Path:
        return self.state_dir / "sources.json"

    @property
    def runs_path(self) -> Path:
        return self.state_dir / "runs.json"

    @property
    def probe_health_path(self) -> Path:
        return self.state_dir / "probe_health.json"

    def load_configs(self) -> dict[str, Config]:
        raw = read_json(self.configs_path, {"configs": []})
        items = raw.get("configs", []) if isinstance(raw, dict) else raw
        out: dict[str, Config] = {}
        for item in items:
            try:
                conf = Config.from_dict(item)
            except (TypeError, KeyError):
                continue
            out[conf.fingerprint] = conf
        return out

    def save_configs(self, configs: dict[str, Config]) -> None:
        payload = {
            "updated_at": iso(utcnow()),
            "count": len(configs),
            "configs": [c.to_dict() for c in configs.values()],
        }
        _atomic_write_json(self.configs_path, payload)

    # ------------------------------------------------------------- sources
    def load_sources(self) -> dict[str, Source]:
        raw = read_json(self.sources_path, {"sources": []})
        items = raw.get("sources", []) if isinstance(raw, dict) else raw
        out: dict[str, Source] = {}
        for item in items:
            try:
                src = Source.from_dict(item)
            except TypeError:
                continue
            out[src.url] = src
        return out

    def save_sources(self, sources: dict[str, Source]) -> None:
        payload = {
            "updated_at": iso(utcnow()),
            "count": len(sources),
            "sources": sorted((s.to_dict() for s in sources.values()), key=lambda s: s["url"]),
        }
        _atomic_write_json(self.sources_path, payload)

    # ---------------------------------------------------------------- runs
    def load_runs(self) -> list[dict]:
        raw = read_json(self.runs_path, {"runs": []})
        if isinstance(raw, dict):
            return list(raw.get("runs", []))
        return list(raw)

    def append_run(self, record: dict, keep: int = 100) -> None:
        runs = self.load_runs()
        runs.append(record)
        runs = runs[-keep:]
        _atomic_write_json(self.runs_path, {"updated_at": iso(utcnow()), "runs": runs})

    # -------------------------------------------------------- probe health
    def load_probe_health(self) -> dict:
        return read_json(self.probe_health_path, {})

    def save_probe_health(self, payload: dict) -> None:
        _atomic_write_json(self.probe_health_path, payload)

    # ----------------------------------------------------- check-host nodes
    @property
    def checkhost_nodes_path(self) -> Path:
        return self.state_dir / "checkhost_nodes.json"

    def load_checkhost_nodes(self) -> dict:
        return read_json(self.checkhost_nodes_path, {"nodes": [], "history": []})

    def save_checkhost_nodes(self, payload: dict) -> None:
        _atomic_write_json(self.checkhost_nodes_path, payload)

    @property
    def globalping_probes_path(self) -> Path:
        return self.state_dir / "globalping_probes.json"

    def load_globalping_probes(self) -> dict:
        return read_json(self.globalping_probes_path, {"probes": [], "cities": []})

    def save_globalping_probes(self, payload: dict) -> None:
        _atomic_write_json(self.globalping_probes_path, payload)
