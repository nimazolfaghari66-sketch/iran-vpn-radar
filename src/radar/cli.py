"""Command line interface for the radar.

    python -m radar cycle          run one full 2-hour cycle
    python -m radar discover       discovery + retrieval only, no testing/publishing
    python -m radar test-iran      run the Iran testing round only
    python -m radar generate       regenerate subscription files from stored state
    python -m radar status         print the current status report
    python -m radar validate       validate the current subscription files
    python -m radar scan-secrets   scan the repository for secrets
    python -m radar probe-health   print Iran probe health
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config as cfg
from . import generate, quality, validate
from .iran_probe import probe_health, run_iran_tests
from .logging_setup import get_logger, setup_logging
from .models import iso, utcnow
from .pipeline import run_cycle
from .storage import Store

log = get_logger("radar.cli")


def _root(args) -> Path:
    return Path(args.root).resolve()


def cmd_cycle(args) -> int:
    settings = cfg.load_settings(_root(args), publish_enabled=not args.no_publish)
    stats = run_cycle(settings)
    print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2))
    return 0 if not stats.errors else 1


def cmd_discover(args) -> int:
    settings = cfg.load_settings(_root(args))
    settings.publish_enabled = False
    settings.dry_run = True
    stats = run_cycle(settings)
    print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_test_iran(args) -> int:
    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    report = run_iran_tests(configs, settings, max_batch=args.batch)
    store.save_configs(configs)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_generate(args) -> int:
    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    files = generate.build_files(configs, settings.sub_dir)
    report = validate.validate_files(files, previous_dir=settings.sub_dir)
    if not report.ok:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 1
    generate.write_files(files)
    generate.write_index(files, settings.status_dir / "subscriptions.json", settings)
    print(json.dumps({gen.name: gen.count for gen in files}, ensure_ascii=False, indent=2))
    return 0


def cmd_validate(args) -> int:
    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    files = generate.build_files(configs, settings.sub_dir)
    report = validate.validate_files(files, previous_dir=settings.sub_dir)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


def cmd_status(args) -> int:
    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    sources = store.load_sources()
    health = probe_health(configs, settings)
    from .report import build_summary

    summary = build_summary(
        settings, configs, sources, health, None, {"added": 0, "removed": 0, "discovered": 0}, store.load_runs()
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_foreign_test(args) -> int:
    """Run a clearly-labelled FOREIGN-location diagnostic (never published)."""
    from .foreign_probe import run_foreign_diagnostic, save_foreign_results

    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    chosen = list(configs.values())[: args.batch]
    results = run_foreign_diagnostic(chosen)
    path = save_foreign_results(settings.state_dir, results)
    ok = sum(1 for r in results if r.get("tunnel_ok"))
    print(
        json.dumps(
            {
                "location": "FOREIGN (not Iran; diagnostic only; never published)",
                "tested": len(results),
                "tunnel_ok": ok,
                "results_file": str(path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_probe_health(args) -> int:
    settings = cfg.load_settings(_root(args))
    store = Store(settings.state_dir)
    configs = store.load_configs()
    print(json.dumps(probe_health(configs, settings), ensure_ascii=False, indent=2))
    return 0


def cmd_scan_secrets(args) -> int:
    from .secrets_scan import scan_repository, summarize

    root = _root(args)
    findings = scan_repository(root, include_private_ips=not args.allow_private_ips)
    summary = summarize(findings)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["total"] == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="radar", description="Iran VPN Radar engine")
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--log-level", default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("cycle", help="run one full cycle")
    p.add_argument("--no-publish", action="store_true", help="skip GitHub publishing")
    p.set_defaults(func=cmd_cycle)

    sub.add_parser("discover", help="discovery + retrieval only").set_defaults(func=cmd_discover)

    p = sub.add_parser("test-iran", help="run the Iran testing round")
    p.add_argument("--batch", type=int, default=60)
    p.set_defaults(func=cmd_test_iran)

    sub.add_parser("generate", help="regenerate subscription files").set_defaults(func=cmd_generate)
    sub.add_parser("validate", help="validate subscription files").set_defaults(func=cmd_validate)
    p = sub.add_parser("foreign-test", help="run a FOREIGN-location diagnostic (never published)")
    p.add_argument("--batch", type=int, default=5)
    p.set_defaults(func=cmd_foreign_test)

    sub.add_parser("status", help="print status report").set_defaults(func=cmd_status)
    sub.add_parser("probe-health", help="print Iran probe health").set_defaults(func=cmd_probe_health)

    p = sub.add_parser("scan-secrets", help="scan for secrets")
    p.add_argument("--allow-private-ips", action="store_true")
    p.set_defaults(func=cmd_scan_secrets)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.log_level)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
