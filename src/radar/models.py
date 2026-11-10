"""Internal representation of a discovered configuration.

The internal model is deliberately protocol-aware but shallow: we keep the
original canonical URI (which is what subscription clients consume) next to a
small set of metadata fields needed for de-duplication, reporting and testing.
"""

from __future__ import annotations

import hashlib
import ipaddress
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

from . import config as cfg


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def host_kind(host: str) -> str:
    """Classify a hostname as ``ipv4``, ``ipv6``, ``domain`` or ``unknown``."""
    if not host:
        return "unknown"
    candidate = host.strip("[]")
    try:
        addr = ipaddress.ip_address(candidate)
        return "ipv4" if addr.version == 4 else "ipv6"
    except ValueError:
        pass
    if "." in candidate:
        return "domain"
    return "unknown"


def _canonical_host_port(host: str, port: int | None) -> str:
    return f"{host.lower()}:{port if port is not None else ''}"


@dataclass
class Config:
    """A single VPN/proxy configuration discovered from a public source."""

    uri: str
    protocol: str
    host: str
    port: int | None
    transport: str = "tcp"
    security: str = "none"
    sni: str | None = None
    source_id: str = ""
    source_url: str = ""
    tag: str | None = None

    fingerprint: str = ""
    status: str = cfg.DISCOVERED

    discovered_at: str = field(default_factory=lambda: iso(utcnow()))
    first_seen_at: str = field(default_factory=lambda: iso(utcnow()))
    last_seen_at: str = field(default_factory=lambda: iso(utcnow()))
    last_success_at: str | None = None
    last_failure_at: str | None = None
    last_test_at: str | None = None
    consecutive_failures: int = 0
    test_count: int = 0
    success_count: int = 0

    last_latency_ms: float | None = None
    last_download_kbps: float | None = None
    last_grade: str | None = None
    last_error: str | None = None

    # Global real-tunnel verification (non-Iranian). Kept separate from the Iran
    # state machine so this tier can never promote a configuration to WORKING.
    tunnel_status: str | None = None
    tunnel_verified_at: str | None = None
    last_tunnel_test_at: str | None = None
    tunnel_test_count: int = 0
    tunnel_consecutive_failures: int = 0
    tunnel_latency_ms: float | None = None
    tunnel_download_kbps: float | None = None
    tunnel_grade: str | None = None
    tunnel_last_error: str | None = None
    # Best Iranian reachability classification observed (Globalping), ranking only.
    iran_reachability: str | None = None
    iran_reachability_at: str | None = None

    def __post_init__(self) -> None:
        if not self.fingerprint:
            self.fingerprint = self.compute_fingerprint()
        if self.protocol not in cfg.PROTOCOLS:
            self.protocol = cfg.SCHEME_TO_PROTOCOL.get(self.protocol, self.protocol)

    # ------------------------------------------------------------- fingerprint
    def compute_fingerprint(self) -> str:
        """Stable identity: protocol + endpoint + transport/security + credential core.

        Two links that differ only in the display fragment (``#tag``) collapse to
        the same configuration, which is what we want for de-duplication.
        """
        parts = [
            self.protocol,
            _canonical_host_port(self.host, self.port),
            (self.transport or "").lower(),
            (self.security or "").lower(),
            (self.sni or "").lower(),
        ]
        # Credential material (uuid / password) is folded in so that different
        # accounts on the same endpoint remain distinct configurations.
        parts.append(self._credential_core())
        digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
        return digest[:32]

    def _credential_core(self) -> str:
        try:
            split = urlsplit(self.uri)
        except ValueError:
            return ""
        userinfo = ""
        if split.username:
            userinfo = split.username
            if split.password:
                userinfo += ":" + split.password
        return userinfo.lower()

    # ---------------------------------------------------------------- helpers
    @property
    def endpoint(self) -> str:
        return _canonical_host_port(self.host, self.port)

    @property
    def host_kind(self) -> str:
        return host_kind(self.host)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)

    def mark_seen(self, when: datetime | None = None) -> None:
        self.last_seen_at = iso(when or utcnow())


@dataclass
class Source:
    """A publicly reachable location that may publish free configurations."""

    url: str
    kind: str = "github"
    protocol_hint: str | None = None
    discovered_at: str = field(default_factory=lambda: iso(utcnow()))
    last_checked_at: str | None = None
    last_status: str = "unknown"  # ok | error | skipped | blocked
    last_error: str | None = None
    last_etag: str | None = None
    last_modified: str | None = None
    content_hash: str | None = None
    consecutive_failures: int = 0
    total_runs: int = 0
    configs_last_seen: int = 0
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Source":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})
