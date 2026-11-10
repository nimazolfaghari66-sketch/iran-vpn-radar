"""Runtime configuration.

Everything is driven by environment variables so that no credential or
environment specific value is ever written into the repository.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Protocols supported by the radar. Order matters: it is the order used in the
# generated subscription index and in reports.
PROTOCOLS: tuple[str, ...] = (
    "vless",
    "vmess",
    "trojan",
    "shadowsocks",
    "hysteria2",
    "tuic",
    "socks",
    "http",
)

# Public subscription files required by the project specification.
CORE_SUBSCRIPTION_FILES: tuple[str, ...] = (
    "all",
    "vless",
    "vmess",
    "trojan",
    "shadowsocks",
    "hysteria2",
    "tuic",
)

# URI scheme -> canonical protocol name.
SCHEME_TO_PROTOCOL: dict[str, str] = {
    "vless": "vless",
    "vmess": "vmess",
    "trojan": "trojan",
    "ss": "shadowsocks",
    "shadowsocks": "shadowsocks",
    "hysteria2": "hysteria2",
    "hy2": "hysteria2",
    "hysteria": "hysteria2",
    "tuic": "tuic",
    "socks": "socks",
    "socks5": "socks",
    "socks5h": "socks",
    "http": "http",
    "https": "http",
}

PROTOCOL_TO_SCHEME: dict[str, str] = {
    "vless": "vless",
    "vmess": "vmess",
    "trojan": "trojan",
    "shadowsocks": "ss",
    "hysteria2": "hysteria2",
    "tuic": "tuic",
    "socks": "socks",
    "http": "http",
}

# Configuration states (specification section 7).
DISCOVERED = "DISCOVERED"
PENDING_IRAN_TEST = "PENDING_IRAN_TEST"
TESTING = "TESTING"
WORKING = "WORKING"
DEGRADED = "DEGRADED"
FAILED = "FAILED"
EXPIRED = "EXPIRED"
DUPLICATE = "DUPLICATE"

ALL_STATES = (
    DISCOVERED,
    PENDING_IRAN_TEST,
    TESTING,
    WORKING,
    DEGRADED,
    FAILED,
    EXPIRED,
    DUPLICATE,
)

# States that may appear in the published "active" subscription files.
PUBLISHABLE_STATES = (WORKING, DEGRADED)

# ---------------------------------------------------------------- Check-Host
# Check-Host (check-host.net) is a public, third-party network diagnostic
# service. Its Iranian nodes are remote *diagnostic probes*: we may ask them to
# resolve a hostname or open a TCP/UDP socket, but we cannot install or run a
# VPN client on them. A reachable port therefore proves reachability only, not
# that a tunnel works.
#
# These classifications are recorded for diagnostics and reporting. NONE of
# them is publishable. Only the dedicated Iran probe agent (iran_probe.py),
# which runs a real VPN client inside Iran, may produce IRAN_FULL_TUNNEL_VERIFIED
# and move a configuration to WORKING.
IRAN_DNS_OK = "IRAN_DNS_OK"
IRAN_TCP_REACHABLE = "IRAN_TCP_REACHABLE"
IRAN_HTTP_REACHABLE = "IRAN_HTTP_REACHABLE"
IRAN_UDP_REACHABLE = "IRAN_UDP_REACHABLE"
IRAN_TIMEOUT = "IRAN_TIMEOUT"
IRAN_UNREACHABLE = "IRAN_UNREACHABLE"
IRAN_FULL_TUNNEL_VERIFIED = "IRAN_FULL_TUNNEL_VERIFIED"

CHECKHOST_CLASSIFICATIONS = (
    IRAN_DNS_OK,
    IRAN_TCP_REACHABLE,
    IRAN_HTTP_REACHABLE,
    IRAN_UDP_REACHABLE,
    IRAN_TIMEOUT,
    IRAN_UNREACHABLE,
)

# Reachability seen from an Iranian diagnostic node. Informational only.
CHECKHOST_REACHABLE = (IRAN_DNS_OK, IRAN_TCP_REACHABLE, IRAN_HTTP_REACHABLE, IRAN_UDP_REACHABLE)
CHECKHOST_UNREACHABLE = (IRAN_TIMEOUT, IRAN_UNREACHABLE)

DEFAULT_USER_AGENT = (
    "IranVPNRadar/1.0 (+https://github.com/{owner}/{repo}; public free-config aggregator)"
)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Resolved runtime settings."""

    root: Path
    state_dir: Path
    sub_dir: Path
    status_dir: Path
    seed_sources: Path

    owner: str
    repo: str
    branch: str

    user_agent: str
    http_timeout: float
    max_download_bytes: int
    max_sources_per_run: int
    max_configs_per_source: int

    probe_mode: str
    probe_url: str | None
    probe_token: str | None
    probe_timeout: float
    local_is_iran: bool
    allow_foreign_tests: bool

    checkhost_enabled: bool
    checkhost_batch: int
    checkhost_checks: tuple[str, ...]
    checkhost_min_interval: float

    publish_enabled: bool
    dry_run: bool
    extra: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ paths
    @property
    def configs_db(self) -> Path:
        return self.state_dir / "configs.json"

    @property
    def sources_db(self) -> Path:
        return self.state_dir / "sources.json"

    @property
    def runs_db(self) -> Path:
        return self.state_dir / "runs.json"

    @property
    def probe_health_db(self) -> Path:
        return self.state_dir / "probe_health.json"

    @property
    def summary_file(self) -> Path:
        return self.status_dir / "summary.json"

    @property
    def latest_cycle_file(self) -> Path:
        return self.status_dir / "latest-cycle.json"

    @property
    def raw_base(self) -> str:
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}"

    def subscription_url(self, name: str) -> str:
        return f"{self.raw_base}/subscriptions/{name}"

    def to_public_dict(self) -> dict:
        """Only non-sensitive, publishable fields."""
        return {
            "repository": f"{self.owner}/{self.repo}",
            "branch": self.branch,
            "raw_base": self.raw_base,
            "protocols": list(PROTOCOLS),
            "subscription_files": list(CORE_SUBSCRIPTION_FILES),
        }


def load_settings(root: Path | None = None, **overrides) -> Settings:
    """Build :class:`Settings` from the environment plus explicit overrides."""
    if root is None:
        root = Path(os.environ.get("IRAN_RADAR_ROOT", ".")).resolve()
    root = Path(root).resolve()

    owner = overrides.get("owner") or _env("IRAN_RADAR_OWNER", "nimazolfaghari66-sketch")
    repo = overrides.get("repo") or _env("IRAN_RADAR_REPO", "iran-vpn-radar")
    branch = overrides.get("branch") or _env("IRAN_RADAR_BRANCH", "main")

    user_agent = overrides.get("user_agent") or _env("IRAN_RADAR_USER_AGENT")
    if not user_agent:
        user_agent = DEFAULT_USER_AGENT.format(owner=owner, repo=repo)

    settings = Settings(
        root=root,
        state_dir=Path(overrides.get("state_dir") or root / "data"),
        sub_dir=Path(overrides.get("sub_dir") or root / "subscriptions"),
        status_dir=Path(overrides.get("status_dir") or root / "status"),
        seed_sources=Path(overrides.get("seed_sources") or root / "sources" / "seed_sources.json"),
        owner=owner,
        repo=repo,
        branch=branch,
        user_agent=user_agent,
        http_timeout=overrides.get("http_timeout", _env_float("IRAN_RADAR_HTTP_TIMEOUT", 25.0)),
        max_download_bytes=overrides.get(
            "max_download_bytes", _env_int("IRAN_RADAR_MAX_DOWNLOAD_BYTES", 12 * 1024 * 1024)
        ),
        max_sources_per_run=overrides.get(
            "max_sources_per_run", _env_int("IRAN_RADAR_MAX_SOURCES_PER_RUN", 120)
        ),
        max_configs_per_source=overrides.get(
            "max_configs_per_source", _env_int("IRAN_RADAR_MAX_CONFIGS_PER_SOURCE", 4000)
        ),
        probe_mode=(overrides.get("probe_mode") or _env("IRAN_RADAR_PROBE_MODE", "unavailable")).lower(),
        probe_url=overrides.get("probe_url") or _env("IRAN_PROBE_URL"),
        probe_token=overrides.get("probe_token") or _env("IRAN_PROBE_TOKEN"),
        probe_timeout=overrides.get("probe_timeout", _env_float("IRAN_RADAR_PROBE_TIMEOUT", 180.0)),
        local_is_iran=overrides.get("local_is_iran", _env_bool("IRAN_RADAR_LOCAL_IS_IRAN", False)),
        allow_foreign_tests=overrides.get(
            "allow_foreign_tests", _env_bool("IRAN_RADAR_ALLOW_FOREIGN_TESTS", False)
        ),
        checkhost_enabled=overrides.get(
            "checkhost_enabled", _env_bool("IRAN_RADAR_CHECKHOST", True)
        ),
        checkhost_batch=overrides.get(
            "checkhost_batch", _env_int("IRAN_RADAR_CHECKHOST_BATCH", 12)
        ),
        checkhost_checks=tuple(
            overrides.get("checkhost_checks")
            or (_env("IRAN_RADAR_CHECKHOST_CHECKS") or "dns,tcp").split(",")
        ),
        checkhost_min_interval=overrides.get(
            "checkhost_min_interval", _env_float("IRAN_RADAR_CHECKHOST_MIN_INTERVAL", 2.5)
        ),
        publish_enabled=overrides.get("publish_enabled", _env_bool("IRAN_RADAR_PUBLISH", False)),
        dry_run=overrides.get("dry_run", _env_bool("IRAN_RADAR_DRY_RUN", False)),
    )
    return settings
