#!/usr/bin/env python3
"""Run one full Iran VPN Radar cycle (used by the 2-hour scheduler)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from radar.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["--root", str(ROOT), "cycle", *sys.argv[1:]]))
