"""Foreign-location diagnostic testing.

This module exists to answer one narrow question: *is our test tooling
working?* It runs the same real tunnel tests as the Iran probe but from whatever
machine invokes it, and it labels every result as ``FOREIGN``.

It is deliberately isolated from the quality state machine:

* results are written to ``data/foreign_tests.json`` only;
* configuration status is never changed;
* results are never published;
* nothing here can ever make a configuration appear Iran-verified.

The specification forbids presenting a foreign-location test as an Iranian one.
Keeping this path separate and explicitly labelled is how we honour that while
still being able to prove the tunnel tooling functions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .local_probe import find_client, test_config
from .logging_setup import get_logger
from .models import Config, iso, utcnow
from .probe_protocol import ProbeInfo
from .storage import _atomic_write_json, read_json

log = get_logger("radar.foreign")


def _foreign_probe_info() -> ProbeInfo:
    return ProbeInfo(
        name="foreign-diagnostic",
        country="XX",  # deliberately not IR: results can never be mistaken for Iranian
        version="1.0.0",
        checked_at=iso(utcnow()),
    )


def run_foreign_diagnostic(configs: list[Config], options: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run real tunnel tests from the current (non-Iran) location.

    Returns labelled, non-publishable diagnostics. Config status is untouched.
    """
    probe = _foreign_probe_info()
    client = find_client()
    out: list[dict[str, Any]] = []
    if client is None:
        log.warning("no VPN client binary; foreign diagnostic cannot run tunnel tests")
        for conf in configs:
            out.append(
                {
                    "fingerprint": conf.fingerprint,
                    "protocol": conf.protocol,
                    "endpoint": conf.endpoint,
                    "success": None,
                    "location": "FOREIGN",
                    "note": "no VPN client binary installed",
                    "tested_at": iso(utcnow()),
                }
            )
        return out

    # A foreign probe must not be able to produce an "Iranian" outcome. We call
    # test_config with a non-IR probe, which makes it refuse; so for the
    # diagnostic we bypass the Iranian gate explicitly and record FOREIGN.
    from .local_probe import StageResult, _curl_through_proxy, _free_port, _tcp_reachable, _resolve, _wait_for_port, _write_config

    kind, binary = client
    for conf in configs:
        entry: dict[str, Any] = {
            "fingerprint": conf.fingerprint,
            "protocol": conf.protocol,
            "endpoint": conf.endpoint,
            "location": "FOREIGN",
            "tested_at": iso(utcnow()),
        }
        try:
            import subprocess
            import tempfile
            import time

            stages = StageResult()
            stages.dns = _resolve(conf.host)
            stages.reachability = _tcp_reachable(conf.host, conf.port)
            entry["dns"] = stages.dns
            entry["reachability"] = stages.reachability
            if stages.reachability:
                socks_port = _free_port()
                with tempfile.TemporaryDirectory(prefix="radar-foreign-") as tmp:
                    cfg_path = _write_config(kind, conf, socks_port, Path(tmp))
                    proc = subprocess.Popen(
                        [binary, "run", "-c", str(cfg_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    try:
                        if _wait_for_port(socks_port, timeout=10.0):
                            stages.handshake = True
                            ok, seconds, _size = _curl_through_proxy(socks_port, "http://cp.cloudflare.com/generate_204", timeout=12)
                            stages.tunnel = ok
                            stages.internet = ok
                            if ok:
                                entry["latency_ms"] = round(seconds * 1000, 1)
                        else:
                            entry["note"] = "tunnel client did not start"
                    finally:
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                        except Exception:
                            proc.kill()
            else:
                entry["note"] = "server unreachable"
            entry["tunnel_ok"] = stages.tunnel
        except Exception as exc:
            entry["note"] = f"diagnostic error: {exc}"
            entry["tunnel_ok"] = False
        out.append(entry)
    return out


def save_foreign_results(state_dir: Path, results: list[dict[str, Any]]) -> Path:
    path = Path(state_dir) / "foreign_tests.json"
    payload = {
        "note": "FOREIGN-LOCATION DIAGNOSTIC ONLY. Not Iranian tests. Never published.",
        "updated_at": iso(utcnow()),
        "count": len(results),
        "results": results,
    }
    _atomic_write_json(path, payload)
    return path


def load_foreign_results(state_dir: Path) -> list[dict[str, Any]]:
    return read_json(Path(state_dir) / "foreign_tests.json", {"results": []}).get("results", [])
