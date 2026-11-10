#!/usr/bin/env python3
"""Local 2-hour scheduler.

Runs the update cycle every 2 hours. Intended for a persistent host (e.g. the
All Hands runtime or an always-on box). GitHub Actions provides the same cadence
in the cloud; this script is for environments where the cycle must run locally.

    python3 scripts/scheduler.py            # run forever, every 2 hours
    python3 scripts/scheduler.py --once     # run one cycle and exit
    python3 scripts/scheduler.py --interval 7200

The scheduler never overlaps executions: a cycle lock is held by the pipeline and
a failed run never overwrites the last valid published subscription files.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERVAL = 2 * 60 * 60


def run_once(extra: list[str]) -> int:
    cmd = [sys.executable, str(ROOT / "scripts" / "run_cycle.py"), *extra]
    print(f"[{datetime.now(timezone.utc).isoformat()}] running: {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Iran VPN Radar local scheduler")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="seconds between cycles")
    parser.add_argument("--once", action="store_true", help="run a single cycle and exit")
    parser.add_argument("--no-publish", action="store_true", help="skip GitHub publishing")
    args = parser.parse_args()

    extra = ["--no-publish"] if args.no_publish else []

    if args.once:
        return run_once(extra)

    while True:
        try:
            run_once(extra)
        except KeyboardInterrupt:
            print("scheduler stopped by user", file=sys.stderr)
            return 0
        except Exception as exc:  # keep the scheduler alive across failures
            print(f"cycle error: {exc}", file=sys.stderr)
        print(f"sleeping {args.interval}s until next cycle", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
