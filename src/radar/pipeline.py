"""The 2-hour cycle orchestration.

One call to :func:`run_cycle` performs the full pipeline:

1.  discover new public sources
2.  retrieve updated source data (conditional requests, polite backoff)
3.  extract new configurations
4.  normalise configurations
5.  de-duplicate
6.  send eligible configurations to the Iran test agent
7.  receive and validate test results
8.  remove failed configurations per the failure policy
9.  add newly verified working configurations
10. generate all protocol-specific subscription files
11. validate every generated file
12. publish changes to the public GitHub repository
13. generate a concise execution report

The pipeline is idempotent and crash-safe: state is written atomically, and a
failed run never overwrites the last valid published subscription files.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import config as cfg
from . import (
    checkhost,
    dedupe,
    discovery,
    extract,
    generate,
    globalping,
    publish as publish_mod,
    quality,
    report as report_mod,
    tunnel_verify,
    validate,
)
from .iran_probe import IranTestReport, probe_health, run_iran_tests
from .logging_setup import get_logger, log, redact
from .models import Config, Source, iso, utcnow
from .retrieval import fetch
from .storage import Store

log = get_logger("radar.pipeline")


@dataclass
class CycleStats:
    started_at: str = field(default_factory=lambda: iso(utcnow()))
    finished_at: str | None = None
    sources_total: int = 0
    sources_ok: int = 0
    sources_error: int = 0
    sources_new: int = 0
    tokens_seen: int = 0
    configs_discovered: int = 0
    configs_added: int = 0
    configs_removed: int = 0
    configs_publishable: int = 0
    checkhost: dict = field(default_factory=dict)
    globalping: dict = field(default_factory=dict)
    tunnel: dict = field(default_factory=dict)
    iran: dict = field(default_factory=dict)
    generated: dict[str, int] = field(default_factory=dict)
    validation: dict = field(default_factory=dict)
    publish: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_s": round(self.duration_s, 2),
            "sources": {
                "total": self.sources_total,
                "ok": self.sources_ok,
                "error": self.sources_error,
                "new": self.sources_new,
            },
            "configs": {
                "discovered": self.configs_discovered,
                "added": self.configs_added,
                "removed": self.configs_removed,
                "publishable": self.configs_publishable,
            },
            "checkhost": self.checkhost,
            "globalping": self.globalping,
            "tunnel": self.tunnel,
            "iran": self.iran,
            "generated": self.generated,
            "validation": self.validation,
            "publish": self.publish,
            "errors": self.errors[:20],
        }


def _cycle_lock(state_dir: Path):
    """Simple file lock so two cycles never overlap."""
    lock_path = Path(state_dir) / "cycle.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    class _Lock:
        def __enter__(self_inner):
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                self_inner.acquired = True
            except FileExistsError:
                # Stale lock? Consider a lock older than 3h stale.
                try:
                    age = time.time() - lock_path.stat().st_mtime
                    if age > 3 * 3600:
                        lock_path.unlink()
                        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                        os.close(fd)
                        self_inner.acquired = True
                    else:
                        self_inner.acquired = False
                except OSError:
                    self_inner.acquired = False
            return self_inner

        def __exit__(self_inner, *exc):
            if getattr(self_inner, "acquired", False):
                try:
                    lock_path.unlink()
                except OSError:
                    pass

    return _Lock()


def run_cycle(settings, store: Store | None = None, max_probe_batch: int = 60) -> CycleStats:
    """Run one full cycle. Returns :class:`CycleStats`."""
    started = time.time()
    stats = CycleStats()
    store = store or Store(settings.state_dir)

    with _cycle_lock(settings.state_dir) as lock:
        if not lock.acquired:
            stats.errors.append("another cycle is already running; skipping")
            stats.finished_at = iso(utcnow())
            stats.duration_s = time.time() - started
            log.warning("cycle skipped: lock held")
            return stats

        # ------------------------------------------------------- load state
        configs = store.load_configs()
        sources = store.load_sources()
        before_fingerprints = set(configs.keys())
        before_publishable = {fp for fp, c in configs.items() if quality.is_publishable(c)}

        # ---------------------------------------------------- 1. discovery
        for seed in discovery.load_seed_sources(settings.seed_sources):
            if discovery.register(sources, seed):
                stats.sources_new += 1

        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        # Expand repository sources into concrete raw files.
        repo_sources = [s for s in list(sources.values()) if s.kind == "github_repo" and s.enabled]
        for src in repo_sources[:20]:
            discovery.discover_from_repo(src.url, sources, token, settings.user_agent)

        # ------------------------------------------------ 2. retrieval + 3/4
        active_sources = [s for s in sources.values() if s.enabled and s.kind != "github_repo"]
        active_sources.sort(key=lambda s: (s.consecutive_failures, s.last_checked_at or ""))
        active_sources = active_sources[: settings.max_sources_per_run]
        stats.sources_total = len(sources)

        discovered: list[Config] = []
        for src in active_sources:
            src.total_runs += 1
            src.last_checked_at = iso(utcnow())
            result = fetch(
                src.url,
                user_agent=settings.user_agent,
                timeout=settings.http_timeout,
                max_bytes=settings.max_download_bytes,
                source=src,
                token=token,
            )
            src.last_status = result.status
            if result.status == "not_modified":
                stats.sources_ok += 1
                continue
            if not result.ok or result.body is None:
                src.consecutive_failures += 1
                src.last_error = result.error
                if result.status == "blocked":
                    src.enabled = False  # respect access restrictions permanently
                stats.sources_error += 1
                continue

            src.consecutive_failures = 0
            src.last_error = None
            src.last_etag = result.etag or src.last_etag
            src.last_modified = result.last_modified or src.last_modified
            changed = src.content_hash != result.content_hash
            src.content_hash = result.content_hash
            stats.sources_ok += 1

            # Recursive discovery from README-like payloads.
            if changed and src.kind in ("github_raw", "web") and "http" in (result.body[:2000].lower()):
                new = discovery.discover_from_payload(result.body, sources)
                stats.sources_new += len(new)

            if not changed and src.last_status == "ok":
                continue  # unchanged content: skip re-extraction

            extracted, estats = extract.extract_configs(
                result.body,
                source_id=src.url,
                source_url=src.url,
                limit=settings.max_configs_per_source,
            )
            stats.tokens_seen += estats["tokens"]
            src.configs_last_seen = len(extracted)
            discovered.extend(extracted)

        stats.configs_discovered = len(discovered)

        # ------------------------------------------------- 5. de-duplication
        unique, duplicates = dedupe.dedupe(discovered)
        merged, added = dedupe.merge_with_store(unique, configs)
        configs = {c.fingerprint: c for c in merged}
        for dup in duplicates:
            configs.setdefault(dup.fingerprint, dup)
        stats.configs_added = added

        # --------------------------------------- 6a. Check-Host diagnostics
        # Iranian Check-Host nodes can only report reachability, never a working
        # tunnel. This runs before the real Iran test, records diagnostics, and
        # deliberately does not touch configuration status.
        stats.checkhost = checkhost.run_checkhost_round(configs, settings, store)

        # --------------------------------------- 6b. Globalping diagnostics
        # Globalping runs a real HTTP/TLS client on Iranian ISP probes, so it
        # can observe a genuine TLS handshake from Iran — stronger than a bare
        # TCP check, but still not a tunnel. It likewise never touches status.
        stats.globalping = globalping.run_globalping_round(configs, settings, store)

        # --------------------------------------- 6c. Global tunnel verification
        # Real tunnel tests (sing-box) run from this host — which is NOT inside
        # Iran. Passing configurations go to the *candidate* pool only and are
        # never promoted to the Iran-verified files. Rounds accumulate until the
        # per-protocol target is reached, no untested configs remain, or the time
        # budget is exhausted.
        stats.tunnel = tunnel_verify.run_tunnel_rounds(
            configs,
            settings,
            store,
            min_batch=int(getattr(settings, "tunnel_batch", cfg.MIN_TUNNEL_BATCH)),
            max_batch=int(getattr(settings, "tunnel_max_batch", 800)),
        )

        # ------------------------------------------------ 6/7. Iran testing
        iran_report: IranTestReport = run_iran_tests(configs, settings, max_batch=max_probe_batch)
        stats.iran = iran_report.to_dict()

        # --------------------------------------------------- 8. failure policy
        # Already handled inside apply_success/apply_failure; count removals.
        after_publishable = {fp for fp, c in configs.items() if quality.is_publishable(c)}
        removed = before_publishable - after_publishable
        stats.configs_removed = len(removed)

        # ------------------------------------------------- 10. generation
        generated_files = generate.build_files(configs, settings.sub_dir)
        candidate_files = generate.build_candidate_files(configs, settings.sub_dir)
        priority_files = generate.build_priority_files(configs, settings.sub_dir)
        stats.generated = {gen.name: gen.count for gen in generated_files}
        stats.generated.update({gen.name: gen.count for gen in candidate_files})
        stats.generated.update({gen.name: gen.count for gen in priority_files})
        stats.configs_publishable = sum(1 for c in configs.values() if quality.is_publishable(c))

        # --------------------------------------------------- 11. validation
        val_report = validate.validate_files(generated_files, previous_dir=settings.sub_dir)
        stats.validation = val_report.to_dict()
        if not val_report.ok:
            stats.errors.append("generated subscription files failed validation; not publishing")
            log.error("validation failed", extra={"context": stats.validation})
            _finalize(stats, started, store, settings, configs, sources, iran_report, None)
            return stats

        # Candidate files are validated structurally only: they may legitimately
        # start empty, and they must never block publication of the Iran files.
        candidate_validation = validate.validate_files(candidate_files)
        if not candidate_validation.ok:
            stats.errors.append("candidate subscription files failed validation; dropping candidates this cycle")
            log.error("candidate validation failed", extra={"context": candidate_validation.to_dict()})
            candidate_files = []

        # Iran-priority files: same structural-only rule. A regression guard is
        # still applied against the previously published copy so a healthy
        # priority file is never replaced by an empty one.
        priority_validation = validate.validate_files(
            priority_files, previous_dir=settings.sub_dir / "iran-priority"
        )
        if not priority_validation.ok:
            stats.errors.append("iran-priority files failed validation; dropping priority tier this cycle")
            log.error("priority validation failed", extra={"context": priority_validation.to_dict()})
            priority_files = []

        generate.write_files(generated_files)
        if candidate_files:
            generate.write_files(candidate_files)
        if priority_files:
            generate.write_files(priority_files)
        index_path = settings.status_dir / "subscriptions.json"
        generate.write_index(generated_files + candidate_files + priority_files, index_path, settings)

        # ---------------------------------------------------- 13. reporting
        # Build and write reports *before* publishing so status/summary.json
        # reflects this cycle (publish reads it from disk to include it in the
        # commit). The summary is rewritten afterwards with the publish outcome.
        summary = _build_summary(
            stats, started, store, settings, configs, sources, iran_report, None
        )
        report_mod.write_reports(settings, summary, stats.to_dict())

        # --------------------------------------------------- 12. publishing
        publish_result_dict = {"ok": None, "note": "publishing disabled"}
        if settings.publish_enabled and not settings.dry_run:
            publish_result = _publish(
                settings, generated_files, candidate_files, priority_files, index_path, stats, token
            )
            publish_result_dict = publish_result.to_dict()
            publish_result_dict["published_at"] = iso(utcnow())
        elif settings.dry_run:
            publish_result_dict = {"ok": None, "note": "dry run"}
        stats.publish = publish_result_dict

        # Rewrite the summary with the publish outcome, then record the run.
        summary["publish"] = publish_result_dict
        report_mod.write_reports(settings, summary, stats.to_dict())
        store.append_run(stats.to_dict())
        log.info("cycle complete", extra={"context": stats.to_dict()})
        return stats


def _publish(
    settings,
    generated_files,
    candidate_files,
    priority_files,
    index_path,
    stats: CycleStats,
    token: str | None,
):
    if not token:
        from .publish import PublishResult

        result = PublishResult(ok=False, errors=["no GITHUB_TOKEN available for publishing"])
        stats.errors.append(result.errors[0])
        return result

    publisher = publish_mod.publisher_from_settings(settings, token=token)
    files: dict[str, str] = {}
    for gen in list(generated_files) + list(candidate_files) + list(priority_files):
        files[f"subscriptions/{gen.name}"] = gen.content
        files[f"subscriptions/{gen.name}.b64"] = gen.b64_content + "\n"

    # Status reports carry a per-run timestamp, so publishing them on every cycle
    # would create a commit every 2 hours even when nothing changed. Only publish
    # status alongside a real subscription change.
    subscription_changed = publisher.any_changed(
        {path: content for path, content in files.items() if path.startswith("subscriptions/")}
    )
    if subscription_changed:
        try:
            files["status/subscriptions.json"] = index_path.read_text(encoding="utf-8")
        except OSError:
            pass
        try:
            files["status/summary.json"] = (settings.status_dir / "summary.json").read_text(encoding="utf-8")
        except OSError:
            pass
    else:
        log.info("no subscription change; skipping status publish to avoid an empty commit")

    message = (
        f"chore(cycle): update subscriptions "
        f"({stats.configs_publishable} iran-verified, "
        f"{stats.generated.get('candidates/all', 0)} candidates, "
        f"{stats.generated.get('iran-priority/all', 0)} iran-priority, "
        f"+{stats.configs_added}/-{stats.configs_removed})"
    )
    result = publisher.publish_files(files, message=message, dry_run=False)

    if result.ok and result.changed:
        # Verify the raw URLs now serve the expected content. The ``all`` files
        # are large and are covered by their per-protocol files, so skip them.
        for gen in list(generated_files) + list(candidate_files) + list(priority_files):
            if gen.name in ("all", "candidates/all", "iran-priority/all"):
                continue
            result.verified_urls[gen.name] = publisher.verify_raw(gen.name, gen.content)
    return result


def _build_summary(
    stats: CycleStats,
    started: float,
    store: Store,
    settings,
    configs: dict,
    sources: dict,
    iran_report: IranTestReport,
    publish_result: dict | None,
) -> dict:
    stats.finished_at = iso(utcnow())
    stats.duration_s = time.time() - started

    store.save_configs(configs)
    store.save_sources(sources)

    health = probe_health(configs, settings)
    store.save_probe_health({"checked_at": stats.finished_at, **health})

    return report_mod.build_summary(
        settings,
        configs,
        sources,
        health,
        publish_result,
        cycle_stats={
            "added": stats.configs_added,
            "removed": stats.configs_removed,
            "discovered": stats.configs_discovered,
        },
        runs=store.load_runs(),
    )


def _finalize(
    stats: CycleStats,
    started: float,
    store: Store,
    settings,
    configs: dict,
    sources: dict,
    iran_report: IranTestReport,
    publish_result: dict | None,
) -> None:
    summary = _build_summary(
        stats, started, store, settings, configs, sources, iran_report, publish_result
    )
    report_mod.write_reports(settings, summary, stats.to_dict())
    store.append_run(stats.to_dict())
    log.info("cycle complete", extra={"context": stats.to_dict()})
