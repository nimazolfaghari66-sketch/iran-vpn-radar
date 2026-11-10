"""Pre-commit secret scanning.

Scans staged/committed content for anything that must never enter a public
repository. Used by ``scripts/scan_secrets.py`` and by the CI workflow.

Detects:

* provider tokens (GitHub, GitLab, Slack, AWS, Google, Stripe, OpenAI, Telegram)
* PEM private keys
* credentials embedded in URLs
* private keys / passwords / api keys in assignment form
* private IPv4 ranges (RFC1918) and link-local addresses
* known sensitive filenames (.env, id_rsa, *.pem, credentials.json, ...)
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path

# High-confidence patterns: a match here is always an error.
TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("gitlab_token", re.compile(r"\bglpat-[A-Za-z0-9_\-]{18,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("stripe_key", re.compile(r"\b(sk|rk)_(live|test)_[0-9A-Za-z]{16,}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("url_credentials", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
]

# Assignment-form secrets: lower confidence, still an error unless allow-listed.
ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|"
    r"private[_-]?key|password|passwd)\b\s*[:=]\s*['\"]?([^\s'\"]{12,})"
)

# Values that look like secrets but are obviously placeholders/examples.
PLACEHOLDER_HINTS = (
    "your_", "example", "changeme", "placeholder", "xxxx", "<", "${", "$(", "redacted",
    "dummy", "sample", "test_", "todo", "user:pass", "user:password", "username:password",
)

# Template/code markers: a "credential" containing these is generated code, not a
# literal secret (e.g. f"http://{user}:{password}@host").
TEMPLATE_MARKERS = ("{", "}", "%s", "%(", "$", "\\")

SENSITIVE_FILENAMES = (
    ".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json", ".netrc",
    ".npmrc", ".pypirc",
)
SENSITIVE_SUFFIXES = (".pem", ".key", ".pfx", ".p12")

# Files/dirs that legitimately contain pattern-like sample data, or that are
# never committed. Internal state lives under data/ and is gitignored.
IGNORE_PATHS = (
    "src/radar/secrets_scan.py",
    "tests/",
    ".github/workflows/",
    "data/",
    "logs/",
)

# Paths whose intended content is public configuration URIs. The URI-shaped
# heuristics (url_credentials, assigned_secret) are expected there and are
# suppressed, but high-confidence provider tokens and private keys are still
# reported so a genuinely leaked secret is never missed.
URI_PAYLOAD_PREFIXES = ("subscriptions/",)
URI_PAYLOAD_SUPPRESSED_KINDS = {"url_credentials", "assigned_secret"}

PRIVATE_NET_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    snippet: str

    def to_dict(self) -> dict:
        return {"path": self.path, "line": self.line, "kind": self.kind, "snippet": self.snippet}


def _redact_snippet(line: str) -> str:
    return re.sub(r"([A-Za-z0-9_\-]{6})[A-Za-z0-9_\-]{10,}", r"\1...REDACTED", line.strip())[:120]


def _is_placeholder(value: str) -> bool:
    lowered = value.lower()
    if any(hint in lowered for hint in PLACEHOLDER_HINTS):
        return True
    return any(marker in value for marker in TEMPLATE_MARKERS)


def _ignored(path: str) -> bool:
    return any(path.startswith(p) or f"/{p}" in path for p in IGNORE_PATHS)


def _is_uri_payload(path: str) -> bool:
    normalized = path.lstrip("/")
    return any(normalized.startswith(prefix) for prefix in URI_PAYLOAD_PREFIXES)


def scan_text(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if _ignored(path):
        return findings
    uri_payload = _is_uri_payload(path)
    for lineno, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in TOKEN_PATTERNS:
            if uri_payload and kind in URI_PAYLOAD_SUPPRESSED_KINDS:
                continue
            for match in pattern.finditer(line):
                if kind == "url_credentials" and _is_placeholder(match.group(0)):
                    continue
                findings.append(Finding(path, lineno, kind, _redact_snippet(line)))
                break
        if uri_payload:
            continue
        for match in ASSIGNMENT_PATTERN.finditer(line):
            if _is_placeholder(match.group(2)):
                continue
            findings.append(Finding(path, lineno, "assigned_secret", _redact_snippet(line)))
            break
    return findings


def _private_ips(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if _ignored(path):
        return findings
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in PRIVATE_NET_PATTERN.finditer(line):
            try:
                addr = ipaddress.ip_address(match.group(0))
            except ValueError:
                continue
            if addr.is_private or addr.is_loopback or addr.is_link_local:
                findings.append(Finding(path, lineno, "private_ip", _redact_snippet(line)))
                break
    return findings


def scan_paths(paths: list[Path], root: Path | None = None, include_private_ips: bool = True) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        rel = str(path.relative_to(root)) if root and path.is_relative_to(root) else str(path)
        name = path.name
        if name in SENSITIVE_FILENAMES or name.endswith(SENSITIVE_SUFFIXES):
            findings.append(Finding(rel, 0, "sensitive_filename", name))
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(scan_text(rel, text))
        if include_private_ips:
            findings.extend(_private_ips(rel, text))
    return findings


def _git_visible_files(root: Path) -> list[Path] | None:
    """Tracked + untracked-but-not-ignored files, or None when git is unavailable.

    Scanning only what git would commit is what actually matters for a public
    repository, and it keeps gitignored internal state (data/) out of scope.
    """
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    files = [root / line for line in proc.stdout.splitlines() if line.strip()]
    return [p for p in files if p.is_file()]


def scan_repository(root: Path, include_private_ips: bool = True) -> list[Finding]:
    root = Path(root)
    candidates = _git_visible_files(root)
    if candidates is None:
        candidates = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue
            if any(part in {"node_modules", "__pycache__", ".venv", "venv"} for part in path.parts):
                continue
            candidates.append(path)
    return scan_paths(candidates, root=root, include_private_ips=include_private_ips)


def summarize(findings: list[Finding]) -> dict:
    by_kind: dict[str, int] = {}
    for finding in findings:
        by_kind[finding.kind] = by_kind.get(finding.kind, 0) + 1
    return {"total": len(findings), "by_kind": by_kind, "findings": [f.to_dict() for f in findings]}
