"""Validation of generated subscription files.

The rule from the specification is strict: never publish an empty or broken
replacement if a previous valid output exists. Validation therefore compares the
new file against the currently published file and refuses the swap when the new
output regresses (empty, malformed, or a large drop in count).
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from pathlib import Path

from . import config as cfg
from .generate import GeneratedFile
from .normalize import parse_uri


@dataclass
class ValidationIssue:
    file: str
    severity: str  # error | warning
    message: str


@dataclass
class ValidationReport:
    ok: bool
    issues: list[ValidationIssue]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": [i.message for i in self.issues if i.severity == "error"],
            "warnings": [i.message for i in self.issues if i.severity == "warning"],
        }


def _lines(content: str) -> list[str]:
    return [ln.strip() for ln in content.splitlines() if ln.strip()]


def validate_content(gen: GeneratedFile) -> list[ValidationIssue]:
    """Structural validation of a single generated file."""
    issues: list[ValidationIssue] = []
    lines = _lines(gen.content)

    if gen.content and not gen.content.endswith("\n"):
        issues.append(ValidationIssue(gen.name, "warning", "file does not end with a newline"))
    if "\r" in gen.content:
        issues.append(ValidationIssue(gen.name, "error", "file contains CR characters (expected LF only)"))

    seen: set[str] = set()
    for line in lines:
        conf = parse_uri(line)
        if conf is None:
            issues.append(ValidationIssue(gen.name, "error", f"unparseable line: {line[:40]}"))
            continue
        if conf.fingerprint in seen:
            issues.append(ValidationIssue(gen.name, "error", f"duplicate link: {line[:40]}"))
        seen.add(conf.fingerprint)
        if gen.protocol and conf.protocol != gen.protocol:
            issues.append(
                ValidationIssue(gen.name, "error", f"protocol mismatch: {conf.protocol} in {gen.name}")
            )

    if gen.count != len(lines):
        issues.append(
            ValidationIssue(gen.name, "error", f"count mismatch: declared {gen.count}, found {len(lines)}")
        )
    return issues


def _b64_valid(content: str) -> bool:
    if not content.strip():
        return True
    try:
        base64.b64decode(content.strip().replace("\n", ""), validate=True)
        return True
    except (binascii.Error, ValueError):
        return False


def validate_files(
    files: list[GeneratedFile],
    previous_dir: Path | None = None,
    max_drop_ratio: float = 0.6,
) -> ValidationReport:
    """Validate all generated files, optionally against the previously published set."""
    issues: list[ValidationIssue] = []
    for gen in files:
        issues.extend(validate_content(gen))
        if not _b64_valid(gen.b64_content):
            issues.append(ValidationIssue(gen.name, "error", "generated base64 body is invalid"))

        if previous_dir is not None:
            prev_path = Path(previous_dir) / gen.name
            if prev_path.exists():
                try:
                    prev_content = prev_path.read_text(encoding="utf-8")
                except OSError:
                    prev_content = ""
                prev_lines = _lines(prev_content)
                new_lines = _lines(gen.content)
                if prev_lines and not new_lines:
                    issues.append(
                        ValidationIssue(
                            gen.name,
                            "error",
                            f"regression: previous file had {len(prev_lines)} entries, new file is empty",
                        )
                    )
                elif prev_lines and len(new_lines) < len(prev_lines) * max_drop_ratio:
                    issues.append(
                        ValidationIssue(
                            gen.name,
                            "warning",
                            f"large drop: {len(prev_lines)} -> {len(new_lines)} entries",
                        )
                    )
    ok = not any(i.severity == "error" for i in issues)
    return ValidationReport(ok=ok, issues=issues)


def safe_to_replace(files: list[GeneratedFile], previous_dir: Path | None) -> tuple[bool, list[str]]:
    """Return ``(safe, reasons)`` — whether the new output may replace the old."""
    report = validate_files(files, previous_dir=previous_dir)
    errors = [i.message for i in report.issues if i.severity == "error"]
    return report.ok, errors


def validate_against_github(files: list[GeneratedFile], fetch_fn) -> ValidationReport:
    """Validate that the published raw URLs will return the expected content.

    ``fetch_fn(name, expected_content) -> bool`` is supplied by the publisher.
    """
    issues: list[ValidationIssue] = []
    for gen in files:
        ok = fetch_fn(gen.name, gen.content)
        if not ok:
            issues.append(ValidationIssue(gen.name, "warning", "published raw URL did not match expected content"))
    return ValidationReport(ok=True, issues=issues)
