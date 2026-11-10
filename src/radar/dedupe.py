"""De-duplication of configurations.

Deduplication is fingerprint based (see :meth:`radar.models.Config.compute_fingerprint`).
The first configuration seen for a fingerprint wins; later duplicates are
recorded as ``DUPLICATE`` so that provenance is still tracked, but they never
reach the published output.
"""

from __future__ import annotations

from . import config as cfg
from .models import Config


def dedupe(configs: list[Config]) -> tuple[list[Config], list[Config]]:
    """Split *configs* into ``(unique, duplicates)``.

    ``unique`` keeps the first occurrence of each fingerprint, preferring an
    entry that has already been verified (so a working config is never replaced
    by a fresh copy from another source).
    """
    best: dict[str, Config] = {}
    order: list[str] = []
    duplicates: list[Config] = []

    def rank(conf: Config) -> int:
        if conf.status in cfg.PUBLISHABLE_STATES:
            return 0
        if conf.status == cfg.DISCOVERED:
            return 1
        return 2

    for conf in configs:
        fp = conf.fingerprint
        existing = best.get(fp)
        if existing is None:
            best[fp] = conf
            order.append(fp)
            continue
        if rank(conf) < rank(existing):
            # A higher-ranked duplicate (e.g. already verified) supersedes the
            # earlier one; the superseded copy is recorded as DUPLICATE.
            best[fp] = conf
            existing.status = cfg.DUPLICATE
            duplicates.append(existing)
        else:
            conf.status = cfg.DUPLICATE
            duplicates.append(conf)

    return [best[fp] for fp in order], duplicates


def merge_with_store(new_configs: list[Config], stored: dict[str, Config]) -> tuple[list[Config], int]:
    """Merge freshly discovered configs into the stored set.

    Returns ``(merged_unique_configs, added_count)``. Existing configurations
    keep their test history; only ``last_seen_at`` and provenance are refreshed.
    """
    added = 0
    merged: dict[str, Config] = dict(stored)
    for conf in new_configs:
        existing = merged.get(conf.fingerprint)
        if existing is None:
            merged[conf.fingerprint] = conf
            added += 1
            continue
        existing.mark_seen()
        existing.last_seen_at = conf.last_seen_at
        if not existing.source_url and conf.source_url:
            existing.source_url = conf.source_url
            existing.source_id = conf.source_id
    return list(merged.values()), added
