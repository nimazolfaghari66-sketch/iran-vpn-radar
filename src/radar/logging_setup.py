"""Structured JSON logging with secret redaction.

The radar runs in public CI, so every log line passes through a redactor that
removes tokens, credentials embedded in URLs and anything that looks like a
private key before it is emitted.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from typing import Any

REDACTED = "***REDACTED***"

# Environment variables whose *values* must never appear in logs.
SENSITIVE_ENV_VARS = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "IRAN_PROBE_TOKEN",
    "IRAN_RADAR_PUBLISH_TOKEN",
    "OPENHANDS_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "OH_GIT_CREDENTIAL_ACCESS_TOKEN_GITHUB",
)

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # GitHub tokens and generic provider prefixes.
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{16,}\b"), REDACTED),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), REDACTED),
    # Authorization headers.
    (re.compile(r"(?i)\b(bearer|token)\s+[A-Za-z0-9\-._~+/=]{12,}"), r"\1 " + REDACTED),
    # Credentials embedded in URLs (https://user:pass@host).
    (re.compile(r"(?i)(https?://)([^/\s:@]+):([^/\s@]+)@"), r"\1\2:" + REDACTED + "@"),
    # PEM private keys.
    (
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
        REDACTED,
    ),
    # Common secret-ish key/value pairs in text or JSON.
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|password|passwd|private[_-]?key|access[_-]?token|auth[_-]?token)\b"
            r"(\s*[:=]\s*)(\"?)([^\s,;\"}]{6,})"
        ),
        r"\1\2\3" + REDACTED,
    ),
]

_secret_values: set[str] = set()


def register_secret(value: str | None) -> None:
    """Register a literal secret value to be redacted verbatim."""
    if value and len(value) >= 8:
        _secret_values.add(value)


def _register_env_secrets() -> None:
    for name in SENSITIVE_ENV_VARS:
        register_secret(os.environ.get(name))


def redact(text: Any) -> str:
    """Return *text* with all known secrets replaced."""
    if text is None:
        return ""
    out = str(text)
    for value in sorted(_secret_values, key=len, reverse=True):
        if value and value in out:
            out = out.replace(value, REDACTED)
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def redact_mapping(mapping: dict) -> dict:
    """Redact keys that are clearly secret-bearing, then redact string values."""
    safe: dict = {}
    for key, value in mapping.items():
        if re.search(r"(?i)token|secret|password|passwd|credential|private[_-]?key", str(key)):
            safe[key] = REDACTED if value else value
        elif isinstance(value, str):
            safe[key] = redact(value)
        elif isinstance(value, dict):
            safe[key] = redact_mapping(value)
        elif isinstance(value, list):
            safe[key] = [redact(v) if isinstance(v, str) else v for v in value]
        else:
            safe[key] = value
    return safe


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact(record.getMessage()),
        }
        extra = getattr(record, "context", None)
        if isinstance(extra, dict):
            payload.update(redact_mapping(extra))
        if record.exc_info:
            payload["exc"] = redact(self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str | None = None, stream=None) -> None:
    """Configure root logging once, with redaction applied to every record."""
    _register_env_secrets()
    stream = stream or sys.stderr
    handler = logging.StreamHandler(stream)
    handler.setFormatter(_JsonFormatter())

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel((level or os.environ.get("IRAN_RADAR_LOG_LEVEL", "INFO")).upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log(logger: logging.Logger, level: int, message: str, **context) -> None:
    """Log *message* with structured, redacted context."""
    logger.log(level, message, extra={"context": redact_mapping(context)} if context else None)
