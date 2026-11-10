"""Wire protocol shared by the central engine and the Iran based probe.

The central engine never performs "Iran tests" itself. It only ever reports a
configuration as Iran-verified when a *probe agent running inside Iran* returns
a signed test result over this protocol. Everything else is recorded as
``PENDING_IRAN_TEST``.

Design:

* Transport: HTTPS POST of JSON.
* Auth: a shared bearer token (``IRAN_PROBE_TOKEN``), never committed.
* Request  ``POST /test``   -> ``{"request_id", "probe_location", "configs": [...]}``
* Response ``200``          -> ``{"request_id", "probe": {...}, "results": [...]}``
* Health   ``GET /health``  -> ``{"status": "ok", "probe": {...}}``

The probe MUST include a ``country`` of ``IR`` (or an explicit ``is_iran`` flag)
for results to be accepted as Iranian. Results without that evidence are
rejected by :func:`validate_result`.
"""

from __future__ import annotations

import json
import secrets
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .logging_setup import get_logger, redact

log = get_logger("radar.probe")

PROTOCOL_VERSION = "1"

# Test stages the probe performs, in order (specification section 6).
TEST_STAGES = (
    "dns",
    "reachability",
    "handshake",
    "tunnel",
    "internet",
    "latency",
    "download",
    "stability",
)


class ProbeUnavailable(RuntimeError):
    """Raised when no usable Iran probe is configured or reachable."""


@dataclass
class ProbeInfo:
    name: str
    country: str
    city: str | None = None
    asn: str | None = None
    isp: str | None = None
    version: str | None = None
    checked_at: str | None = None

    @property
    def is_iran(self) -> bool:
        return (self.country or "").upper() in {"IR", "IRN", "IRAN"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "asn": self.asn,
            "isp": self.isp,
            "version": self.version,
            "checked_at": self.checked_at,
        }


@dataclass
class TestOutcome:
    """Normalised result of testing one configuration."""

    fingerprint: str
    success: bool
    probe_is_iran: bool = False
    latency_ms: float | None = None
    download_kbps: float | None = None
    grade: str | None = None
    error: str | None = None
    stages: dict[str, bool] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestRequest:
    request_id: str
    configs: list[dict[str, Any]]
    options: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "request_id": self.request_id,
            "options": self.options,
            "configs": self.configs,
        }


def new_request_id() -> str:
    return f"{int(time.time())}-{secrets.token_hex(6)}"


def config_to_probe_item(conf) -> dict[str, Any]:
    """Minimal, non-secret descriptor of a config sent to the probe."""
    return {
        "fingerprint": conf.fingerprint,
        "protocol": conf.protocol,
        "uri": conf.uri,
        "host": conf.host,
        "port": conf.port,
        "transport": conf.transport,
        "security": conf.security,
        "sni": conf.sni,
    }


def validate_result(result: dict[str, Any], probe: ProbeInfo) -> tuple[bool, str]:
    """Decide whether a probe result may be trusted as an Iranian test.

    Returns ``(ok, reason)``. A result is rejected unless the probe has
    positively identified itself as being inside Iran.
    """
    if not probe.is_iran:
        return False, f"probe country {probe.country!r} is not Iran"
    if not result.get("probe_is_iran", True):
        return False, "result not marked as Iran based"
    if "fingerprint" not in result:
        return False, "result missing fingerprint"
    if "success" not in result:
        return False, "result missing success flag"
    return True, "ok"


class ProbeClient:
    """HTTP client for the Iran probe agent."""

    def __init__(
        self,
        base_url: str | None,
        token: str | None,
        timeout: float = 180.0,
        user_agent: str = "IranVPNRadar/1.0",
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.token = token
        self.timeout = timeout
        self.user_agent = user_agent

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.token)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self.configured:
            raise ProbeUnavailable("no Iran probe configured (IRAN_PROBE_URL / IRAN_PROBE_TOKEN)")
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            raise ProbeUnavailable(f"probe http {exc.code}") from exc
        except Exception as exc:
            raise ProbeUnavailable(redact(str(exc))) from exc

    def _get(self, path: str) -> dict[str, Any] | None:
        if not self.configured:
            raise ProbeUnavailable("no Iran probe configured")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {self.token}", "User-Agent": self.user_agent},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except Exception as exc:
            raise ProbeUnavailable(redact(str(exc))) from exc

    def health(self) -> ProbeInfo | None:
        data = self._get("/health")
        if not data:
            return None
        probe = data.get("probe", data)
        return ProbeInfo(
            name=str(probe.get("name", "iran-probe")),
            country=str(probe.get("country", "")),
            city=probe.get("city"),
            asn=probe.get("asn"),
            isp=probe.get("isp"),
            version=probe.get("version"),
            checked_at=probe.get("checked_at"),
        )

    def test(self, configs: list[dict[str, Any]], options: dict[str, Any] | None = None) -> dict[str, Any]:
        request = TestRequest(request_id=new_request_id(), configs=configs, options=options or {})
        response = self._post("/test", request.to_payload())
        if not response:
            raise ProbeUnavailable("empty probe response")
        return response


class NullProbe:
    """Explicit stand-in used when no Iran probe exists.

    It exists so the architecture is ready for a real probe without ever
    fabricating an Iranian test result.
    """

    configured = False

    def health(self) -> None:
        return None

    def test(self, configs, options=None):  # pragma: no cover - never used
        raise ProbeUnavailable("no Iran probe available")
