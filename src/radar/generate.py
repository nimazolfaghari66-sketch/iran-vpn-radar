"""Subscription file generation.

Produces one plain-text subscription per protocol plus an ``all`` file. Each
file contains exactly one canonical share link per line, de-duplicated, LF-only
newlines, sorted deterministically so repeated runs are byte-stable (which
avoids pointless commits).

Two encodings are emitted:

* ``subscriptions/<name>``        — plain text, one link per line
* ``subscriptions/<name>.b64``    — base64 of the plain text (for clients that
  expect a base64 subscription body)

Only configurations in a publishable state (``WORKING`` / ``DEGRADED``) are
included.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from . import config as cfg
from . import quality
from .models import Config


@dataclass
class GeneratedFile:
    name: str
    path: Path
    content: str
    count: int
    protocol: str | None

    @property
    def b64_content(self) -> str:
        return base64.b64encode(self.content.encode("utf-8")).decode("ascii")


def _sort_key(conf: Config) -> tuple:
    # WORKING before DEGRADED, then protocol, then host, then fingerprint.
    rank = 0 if conf.status == cfg.WORKING else 1
    return (rank, conf.protocol, conf.host, conf.port or 0, conf.fingerprint)


def active_configs(configs: dict[str, Config]) -> list[Config]:
    unique: dict[str, Config] = {}
    for conf in configs.values():
        if not quality.is_publishable(conf):
            continue
        unique.setdefault(conf.fingerprint, conf)
    return sorted(unique.values(), key=_sort_key)


def _render(configs: list[Config]) -> str:
    if not configs:
        return ""
    body = "\n".join(c.uri.strip() for c in configs)
    return body + "\n"


def build_files(configs: dict[str, Config], sub_dir: Path) -> list[GeneratedFile]:
    """Build every subscription file in memory (nothing is written here)."""
    sub_dir = Path(sub_dir)
    active = active_configs(configs)
    files: list[GeneratedFile] = []

    files.append(
        GeneratedFile(name="all", path=sub_dir / "all", content=_render(active), count=len(active), protocol=None)
    )
    for proto in cfg.PROTOCOLS:
        subset = [c for c in active if c.protocol == proto]
        files.append(
            GeneratedFile(
                name=proto,
                path=sub_dir / proto,
                content=_render(subset),
                count=len(subset),
                protocol=proto,
            )
        )
    return files


def write_files(files: list[GeneratedFile], write_b64: bool = True) -> list[Path]:
    """Write generated files atomically. Returns the list of written paths."""
    written: list[Path] = []
    for gen in files:
        gen.path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(gen.path, gen.content)
        written.append(gen.path)
        if write_b64:
            b64_path = gen.path.with_suffix(gen.path.suffix + ".b64")
            _atomic_write_text(b64_path, gen.b64_content + "\n")
            written.append(b64_path)
    return written


def _atomic_write_text(path: Path, content: str) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    tmp.replace(path)


def build_candidate_files(configs: dict[str, Config], sub_dir: Path) -> list[GeneratedFile]:
    """Build the *candidate* pool files (tunnel-verified, not Iran-verified).

    These live under ``subscriptions/candidates/`` and are clearly separated
    from the Iran-verified files. They are ranked best-first (Iranian
    reachability, then tunnel quality) so the most plausible entries come first.
    """
    from . import tunnel_verify

    sub_dir = Path(sub_dir) / "candidates"
    ranked = tunnel_verify.candidate_configs(configs)
    files: list[GeneratedFile] = []

    files.append(
        GeneratedFile(
            name="candidates/all",
            path=sub_dir / "all",
            content=_render(ranked),
            count=len(ranked),
            protocol=None,
        )
    )
    for proto in cfg.PROTOCOLS:
        subset = [c for c in ranked if c.protocol == proto]
        files.append(
            GeneratedFile(
                name=f"candidates/{proto}",
                path=sub_dir / proto,
                content=_render(subset),
                count=len(subset),
                protocol=proto,
            )
        )
    return files


def write_index(files: list[GeneratedFile], path: Path, settings) -> Path:
    """Write a machine-readable index of subscription files (public, safe)."""
    import json

    from .models import iso, utcnow

    payload = {
        "updated_at": iso(utcnow()),
        "repository": f"{settings.owner}/{settings.repo}",
        "branch": settings.branch,
        "subscriptions": [
            {
                "name": gen.name,
                "protocol": gen.protocol or "all",
                "count": gen.count,
                "url": settings.subscription_url(gen.name),
                "base64_url": settings.subscription_url(gen.name + ".b64"),
            }
            for gen in files
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return path
