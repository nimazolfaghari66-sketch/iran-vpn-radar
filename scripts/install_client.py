#!/usr/bin/env python3
"""Install a VPN protocol client (sing-box) for real tunnel verification.

Downloads a pinned, official sing-box release for linux/amd64 or linux/arm64
into ``.bin/`` (git-ignored). The binary is used by the global tunnel
verification tier and by an Iran-based probe. It is never committed.

Usage:
    python scripts/install_client.py [--version 1.14.4] [--dir .bin]
"""

from __future__ import annotations

import argparse
import hashlib
import platform
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_VERSION = "1.14.4"
# sha256 of the official linux tarballs; verified before extraction.
KNOWN_SHA256: dict[str, str] = {
    "sing-box-1.14.4-linux-amd64-glibc.tar.gz": "231e57c18378f780a08de832844a1ca9716e17a7bcf82964b350844d243c03ac",
}


def _arch() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    if machine in ("aarch64", "arm64"):
        return "arm64"
    raise SystemExit(f"unsupported architecture: {machine}")


def _libc_flavor() -> str:
    # GitHub's ubuntu runners are glibc; prefer the glibc build there.
    import ctypes

    try:
        ctypes.CDLL("libc.so.6")
        return "glibc"
    except OSError:
        return "musl"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--dir", default=".bin")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    bin_dir = (root / args.dir) if not Path(args.dir).is_absolute() else Path(args.dir)
    bin_dir.mkdir(parents=True, exist_ok=True)
    target = bin_dir / "sing-box"
    if target.exists() and not args.force:
        print(f"sing-box already present at {target}")
        return 0

    arch = _arch()
    flavor = _libc_flavor()
    name = f"sing-box-{args.version}-linux-{arch}-{flavor}.tar.gz"
    url = f"https://github.com/SagerNet/sing-box/releases/download/v{args.version}/{name}"
    print(f"downloading {url}")

    with tempfile.TemporaryDirectory(prefix="singbox-") as tmp:
        tarball = Path(tmp) / name
        try:
            urllib.request.urlretrieve(url, tarball)
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"ERROR: download failed: {exc}", file=sys.stderr)
            return 1

        digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
        expected = KNOWN_SHA256.get(name)
        if expected and digest != expected:
            print(f"ERROR: checksum mismatch for {name}", file=sys.stderr)
            return 1
        print(f"sha256 {digest}")

        with tarfile.open(tarball, "r:gz") as tar:
            members = [m for m in tar.getmembers() if m.name.endswith("/sing-box")]
            if not members:
                print("ERROR: sing-box binary not found in archive", file=sys.stderr)
                return 1
            member = members[0]
            extracted = tar.extractfile(member)
            if extracted is None:
                print("ERROR: could not extract sing-box", file=sys.stderr)
                return 1
            target.write_bytes(extracted.read())

    target.chmod(0o755)
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
