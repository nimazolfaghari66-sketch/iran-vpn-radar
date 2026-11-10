"""Polite retrieval of public source payloads.

Guarantees:

* honours ``robots.txt`` for non-GitHub hosts (GitHub raw endpoints are fetched
  through the GitHub API and are not robots-restricted);
* sends a descriptive ``User-Agent``;
* caps download size and timeout;
* supports conditional requests via ``ETag`` / ``Last-Modified``;
* backs off on repeated failures;
* never attempts to bypass authentication, paywalls or access controls.
"""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from .logging_setup import get_logger, redact
from .models import Source

log = get_logger("radar.retrieval")


@dataclass
class FetchResult:
    url: str
    status: str  # ok | not_modified | error | blocked | too_large
    body: str | None = None
    etag: str | None = None
    last_modified: str | None = None
    content_hash: str | None = None
    error: str | None = None
    http_status: int | None = None

    @property
    def ok(self) -> bool:
        return self.status in ("ok", "not_modified")


_robots_cache: dict[str, RobotFileParser | None] = {}


def _robots_allows(url: str, user_agent: str, timeout: float) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    base = f"{parsed.scheme}://{parsed.netloc}"
    if base not in _robots_cache:
        parser = RobotFileParser()
        robots_url = f"{base}/robots.txt"
        try:
            req = urllib.request.Request(robots_url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                parser.parse(resp.read(512 * 1024).decode("utf-8", "replace").splitlines())
            _robots_cache[base] = parser
        except urllib.error.HTTPError as exc:
            # 404 => no robots file => allowed. 401/403 => treat as disallowed.
            _robots_cache[base] = None if exc.code == 404 else _DenyAll()
        except Exception:
            _robots_cache[base] = None
    parser = _robots_cache[base]
    if parser is None:
        return True
    try:
        return parser.can_fetch(user_agent, url)
    except Exception:
        return True


class _DenyAll(RobotFileParser):
    def can_fetch(self, useragent: str, url: str) -> bool:  # noqa: D102
        return False


def fetch(
    url: str,
    user_agent: str,
    timeout: float = 25.0,
    max_bytes: int = 12 * 1024 * 1024,
    source: Source | None = None,
    respect_robots: bool = True,
    token: str | None = None,
) -> FetchResult:
    """Fetch *url* and return a :class:`FetchResult` (never raises)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return FetchResult(url=url, status="blocked", error="unsupported scheme")

    is_github = parsed.netloc.lower() in {"github.com", "raw.githubusercontent.com", "api.github.com", "objects.githubusercontent.com"}
    if respect_robots and not is_github and not _robots_allows(url, user_agent, timeout):
        return FetchResult(url=url, status="blocked", error="disallowed by robots.txt")

    headers = {"User-Agent": user_agent, "Accept": "*/*"}
    if source and source.last_etag:
        headers["If-None-Match"] = source.last_etag
    if source and source.last_modified:
        headers["If-Modified-Since"] = source.last_modified
    if token and parsed.netloc.lower() == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes + 1)
            if len(raw) > max_bytes:
                return FetchResult(url=url, status="too_large", error=f">{max_bytes} bytes")
            body = raw.decode("utf-8", "replace")
            return FetchResult(
                url=url,
                status="ok",
                body=body,
                etag=resp.headers.get("ETag"),
                last_modified=resp.headers.get("Last-Modified"),
                content_hash=hashlib.sha256(raw).hexdigest(),
                http_status=resp.status,
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return FetchResult(url=url, status="not_modified", http_status=304)
        if exc.code in (401, 403):
            return FetchResult(url=url, status="blocked", error=f"http {exc.code}", http_status=exc.code)
        return FetchResult(url=url, status="error", error=f"http {exc.code}", http_status=exc.code)
    except urllib.error.URLError as exc:
        return FetchResult(url=url, status="error", error=redact(str(exc.reason)), http_status=None)
    except Exception as exc:  # socket timeouts, ssl errors, etc.
        return FetchResult(url=url, status="error", error=redact(str(exc)), http_status=None)


def fetch_github_api_json(url: str, token: str, user_agent: str, timeout: float = 25.0) -> dict[str, Any] | None:
    result = fetch(url, user_agent=user_agent, timeout=timeout, token=token, respect_robots=False)
    if result.status != "ok" or not result.body:
        return None
    import json

    try:
        return json.loads(result.body)
    except json.JSONDecodeError:
        return None
