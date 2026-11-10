"""Automatic discovery of new public sources.

Two mechanisms work together:

1. **Seed sources** — a curated, human-reviewable list in
   ``sources/seed_sources.json``. Seeds are trusted to be public.
2. **Recursive discovery** — while retrieving GitHub *repository* sources we
   scan the repository tree and the ``README`` for other public raw config
   URLs. Those candidates are then fetched through the GitHub API (never
   blind-crawled) so discovery stays within the provider's documented API.

Everything discovered is registered in the source registry with URL, discovery
timestamp, protocol hint and retrieval status.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from .logging_setup import get_logger
from .models import Source, iso, utcnow
from .retrieval import fetch_github_api_json

log = get_logger("radar.discovery")

# Filenames that very frequently hold public subscription payloads.
_CONFIG_FILE_HINTS = (
    "sub",
    "config",
    "server",
    "vless",
    "vmess",
    "trojan",
    "ss",
    "shadowsocks",
    "hysteria",
    "tuic",
    "clash",
    "singbox",
    "sing-box",
    "all",
    "mix",
    "v2ray",
    "proxy",
)

_GITHUB_REPO_RE = re.compile(r"https?://github\.com/([^/\s]+)/([^/\s#?]+)")
_RAW_URL_RE = re.compile(r"https?://raw\.githubusercontent\.com/[^\s\"'<>)\]]+")


def _is_config_like(path: str) -> bool:
    lowered = path.lower()
    if not lowered.endswith((".txt", ".yaml", ".yml", ".json", ".conf", ".md")):
        return False
    return any(hint in lowered for hint in _CONFIG_FILE_HINTS)


def load_seed_sources(path: Path) -> list[Source]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("seed source load failed", extra={"context": {"err": str(exc)}})
        return []
    items = raw.get("sources", raw) if isinstance(raw, dict) else raw
    out: list[Source] = []
    for item in items:
        if isinstance(item, str):
            out.append(Source(url=item, kind=_guess_kind(item)))
        elif isinstance(item, dict) and item.get("url"):
            out.append(
                Source(
                    url=item["url"],
                    kind=item.get("kind") or _guess_kind(item["url"]),
                    protocol_hint=item.get("protocol_hint"),
                    enabled=item.get("enabled", True),
                )
            )
    return out


def _guess_kind(url: str) -> str:
    parsed = urlparse(url)
    if "github.com" in parsed.netloc and parsed.path.count("/") >= 2 and not parsed.path.endswith(
        (".txt", ".yaml", ".yml", ".json", ".conf")
    ):
        return "github_repo"
    if "github" in parsed.netloc:
        return "github_raw"
    return "web"


def register(sources: dict[str, Source], candidate: Source) -> bool:
    """Register *candidate* if new. Returns True when the registry changed."""
    if candidate.url in sources:
        return False
    candidate.discovered_at = iso(utcnow())
    sources[candidate.url] = candidate
    return True


def discover_from_repo(
    repo_url: str,
    sources: dict[str, Source],
    token: str | None,
    user_agent: str,
    default_branch: str | None = None,
    max_new: int = 25,
) -> list[Source]:
    """Expand a GitHub repository URL into concrete raw config file URLs."""
    match = _GITHUB_REPO_RE.match(repo_url)
    if not match:
        return []
    owner, repo = match.group(1), match.group(2).removesuffix(".git")
    new_sources: list[Source] = []

    branches = [default_branch] if default_branch else []
    if not branches:
        meta = fetch_github_api_json(
            f"https://api.github.com/repos/{owner}/{repo}", token or "", user_agent
        )
        branches = [meta.get("default_branch", "main")] if meta else ["main"]

    for branch in branches:
        tree = fetch_github_api_json(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
            token or "",
            user_agent,
        )
        if not tree or "tree" not in tree:
            continue
        for node in tree["tree"]:
            if len(new_sources) >= max_new:
                break
            if node.get("type") != "blob":
                continue
            path = node.get("path", "")
            if not _is_config_like(path):
                continue
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
            candidate = Source(url=raw_url, kind="github_raw", protocol_hint=_protocol_hint(path))
            if register(sources, candidate):
                new_sources.append(candidate)
    if new_sources:
        log.info("discovered raw sources from repo", extra={"context": {"repo": f"{owner}/{repo}", "n": len(new_sources)}})
    return new_sources


def discover_from_payload(payload: str, sources: dict[str, Source], max_new: int = 15) -> list[Source]:
    """Scan a payload (typically a README) for new public source URLs."""
    new_sources: list[Source] = []
    for match in _RAW_URL_RE.finditer(payload):
        if len(new_sources) >= max_new:
            break
        url = match.group(0).rstrip(".,;)")
        if not _is_config_like(url) and not url.lower().endswith((".txt", ".yaml", ".yml", ".json")):
            continue
        candidate = Source(url=url, kind="github_raw")
        if register(sources, candidate):
            new_sources.append(candidate)
    for match in _GITHUB_REPO_RE.finditer(payload):
        if len(new_sources) >= max_new:
            break
        repo_url = f"https://github.com/{match.group(1)}/{match.group(2).removesuffix('.git')}"
        if repo_url in sources:
            continue
        if register(sources, Source(url=repo_url, kind="github_repo")):
            new_sources.append(sources[repo_url])
    return new_sources


def _protocol_hint(path: str) -> str | None:
    lowered = path.lower()
    for proto in ("vless", "vmess", "trojan", "shadowsocks", "hysteria", "tuic", "socks"):
        if proto in lowered:
            return "hysteria2" if proto == "hysteria" else proto
    return None
