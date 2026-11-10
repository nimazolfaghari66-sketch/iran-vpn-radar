#!/usr/bin/env python3
"""Iran VPN Radar — Iran based probe agent.

Run this service on a host that is physically inside Iran. It exposes the wire
protocol defined in ``src/radar/probe_protocol.py`` and performs *real* tunnel
tests using a local ``sing-box``/``xray`` client.

    IRAN_PROBE_TOKEN=<shared-secret> python3 probe/probe_agent.py --port 8787

The agent refuses to start unless it can confirm (or the operator asserts) that
it is running inside Iran, because a result produced anywhere else must never be
reported as an Iranian test.

Endpoints
---------
GET  /health   -> probe identity (name, country, city, asn, isp, version)
POST /test     -> {"configs": [...]} -> {"results": [...]}
GET  /geo      -> best-effort location detection (no third-party dependency)

Authentication: ``Authorization: Bearer <IRAN_PROBE_TOKEN>`` on every request.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Make the shared radar package importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar.local_probe import find_client, test_config  # noqa: E402
from radar.logging_setup import get_logger, setup_logging  # noqa: E402
from radar.models import iso, utcnow  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402
from radar.probe_protocol import PROTOCOL_VERSION, ProbeInfo  # noqa: E402

log = get_logger("probe.agent")
VERSION = "1.0.0"


def detect_location() -> dict:
    """Best-effort location detection using only public, keyless endpoints."""
    import urllib.request

    for url in ("https://ipinfo.io/json", "https://ifconfig.co/json"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "IranVPNRadar-probe/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            country = (data.get("country") or data.get("country_iso") or "").upper()
            asn = data.get("asn")
            return {
                "country": country[:2] if country else "",
                "city": data.get("city"),
                "asn": str(asn.get("asn", "")) if isinstance(asn, dict) else asn,
                "isp": data.get("org") or data.get("asn_org") or data.get("isp"),
            }
        except Exception:
            continue
    return {"country": "", "city": None, "asn": None, "isp": None}


class ProbeState:
    """Probe identity and location.

    Location rules (these protect the project's core guarantee):

    * Detected location wins. If geo detection reports a country, that country
      is authoritative and an operator assertion can never override it.
    * An operator assertion (``IRAN_PROBE_COUNTRY=IR``) is only used to fill a
      gap when detection fails entirely. This allows a genuinely Iranian host
      whose geo lookup is blocked to still operate, without letting a host
      outside Iran masquerade as an Iranian probe.
    """

    def __init__(self, name: str, asserted_country: str, city: str | None, asn: str | None, isp: str | None):
        self.asserted_country = (asserted_country or "").upper()
        self.detected_country = ""
        self.info = ProbeInfo(
            name=name,
            country="",
            city=city,
            asn=asn,
            isp=isp,
            version=VERSION,
            checked_at=iso(utcnow()),
        )
        self.started_at = iso(utcnow())
        self.tests_run = 0
        self.lock = threading.Lock()

    def refresh(self) -> None:
        geo = detect_location()
        if geo.get("country"):
            self.detected_country = geo["country"]
        # Detected country is authoritative; the assertion only fills a gap.
        country = self.detected_country or self.asserted_country
        self.info.country = country
        self.info.city = geo.get("city") or self.info.city
        self.info.asn = geo.get("asn") or self.info.asn
        self.info.isp = geo.get("isp") or self.info.isp
        self.info.checked_at = iso(utcnow())

    @property
    def location_conflict(self) -> bool:
        """True when an assertion disagrees with a successful detection."""
        return bool(
            self.detected_country
            and self.asserted_country
            and self.detected_country.upper() != self.asserted_country.upper()
        )


class Handler(BaseHTTPRequestHandler):
    server_version = f"IranVPNRadar-Probe/{VERSION}"
    state: ProbeState
    token: str

    def log_message(self, fmt, *args):
        log.info("http", extra={"context": {"client": self.address_string(), "msg": fmt % args}})

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        return secrets.compare_digest(header[7:], self.token)

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send(401, {"error": "unauthorized"})
            return
        if self.path.startswith("/health"):
            self._send(
                200,
                {
                    "protocol_version": PROTOCOL_VERSION,
                    "status": "ok",
                    "probe": self.state.info.to_dict(),
                    "started_at": self.state.started_at,
                    "tests_run": self.state.tests_run,
                    "client": (find_client() or ("none", None))[0],
                },
            )
            return
        if self.path.startswith("/geo"):
            self.state.refresh()
            self._send(200, {"probe": self.state.info.to_dict()})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self.path.startswith("/test"):
            self._send(404, {"error": "not found"})
            return
        if not self._authorized():
            self._send(401, {"error": "unauthorized"})
            return
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > 8 * 1024 * 1024:
            self._send(400, {"error": "invalid body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8", "replace"))
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid json"})
            return

        self.state.refresh()
        if not self.state.info.is_iran:
            self._send(
                503,
                {
                    "error": "probe is not located in Iran",
                    "probe": self.state.info.to_dict(),
                    "hint": "Set IRAN_PROBE_COUNTRY=IR only if this host really is inside Iran.",
                },
            )
            return

        configs = payload.get("configs", [])
        options = payload.get("options", {})
        results = []
        for item in configs:
            uri = item.get("uri", "")
            conf = parse_uri(uri, source_id="probe", source_url="probe")
            if conf is None:
                results.append(
                    {"fingerprint": item.get("fingerprint", ""), "success": False, "error": "unparseable config"}
                )
                continue
            conf.fingerprint = item.get("fingerprint", conf.fingerprint)
            outcome = test_config(conf, self.state.info, options)
            results.append(
                {
                    "fingerprint": outcome.fingerprint,
                    "success": outcome.success,
                    "probe_is_iran": True,
                    "country": self.state.info.country,
                    "latency_ms": outcome.latency_ms,
                    "download_kbps": outcome.download_kbps,
                    "grade": outcome.grade,
                    "error": outcome.error,
                    "stages": outcome.stages,
                }
            )
            with self.state.lock:
                self.state.tests_run += 1

        self._send(
            200,
            {
                "protocol_version": PROTOCOL_VERSION,
                "probe": self.state.info.to_dict(),
                "tested_at": iso(utcnow()),
                "results": results,
            },
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Iran VPN Radar probe agent")
    parser.add_argument("--host", default=os.environ.get("IRAN_PROBE_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("IRAN_PROBE_PORT", "8787")))
    parser.add_argument("--name", default=os.environ.get("IRAN_PROBE_NAME", "iran-probe-1"))
    parser.add_argument("--country", default=os.environ.get("IRAN_PROBE_COUNTRY", ""))
    parser.add_argument("--city", default=os.environ.get("IRAN_PROBE_CITY"))
    parser.add_argument("--asn", default=os.environ.get("IRAN_PROBE_ASN"))
    parser.add_argument("--isp", default=os.environ.get("IRAN_PROBE_ISP"))
    args = parser.parse_args(argv)

    setup_logging()

    token = os.environ.get("IRAN_PROBE_TOKEN")
    if not token or len(token) < 16:
        print("ERROR: set IRAN_PROBE_TOKEN to a strong shared secret (>=16 chars).", file=sys.stderr)
        return 2

    state = ProbeState(args.name, args.country.upper(), args.city, args.asn, args.isp)
    state.refresh()

    if state.location_conflict:
        print(
            "ERROR: IRAN_PROBE_COUNTRY asserts "
            f"{state.asserted_country!r} but the host is detected as {state.detected_country!r}.\n"
            "       An assertion may never override a detected location. Refusing to start.",
            file=sys.stderr,
        )
        return 4

    if not state.info.is_iran:
        print(
            "ERROR: this probe does not appear to be located in Iran "
            f"(detected country={state.info.country!r}).\n"
            "       A probe outside Iran must never produce Iranian test results.\n"
            "       If this host really is inside Iran, set IRAN_PROBE_COUNTRY=IR.",
            file=sys.stderr,
        )
        return 3

    client_kind = (find_client() or ("none", None))[0]
    log.info(
        "probe starting",
        extra={"context": {"host": args.host, "port": args.port, "country": state.info.country, "client": client_kind}},
    )

    Handler.state = state
    Handler.token = token
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
