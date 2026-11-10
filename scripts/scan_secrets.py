#!/usr/bin/env python3
"""Scan the repository (or the git index) for secrets.

Exit code 0 = clean, 1 = findings. Intended for local pre-commit use and CI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from radar.secrets_scan import scan_paths, scan_repository, summarize  # noqa: E402


def staged_files() -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return [ROOT / line.strip() for line in out.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="scan staged files only")
    parser.add_argument("--allow-private-ips", action="store_true")
    args = parser.parse_args()

    if args.staged:
        paths = staged_files()
        findings = scan_paths(paths, root=ROOT, include_private_ips=not args.allow_private_ips)
    else:
        findings = scan_repository(ROOT, include_private_ips=not args.allow_private_ips)

    summary = summarize(findings)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary["total"]:
        print(f"\nSECRET SCAN FAILED: {summary['total']} finding(s).", file=sys.stderr)
        return 1
    print("\nSecret scan clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
