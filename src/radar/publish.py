"""Safe GitHub publishing.

Uses the GitHub *Contents API* so publishing is a single, reviewable commit per
cycle. Safety properties:

* only project-owned output paths are ever touched (an allow-list);
* no force-push, no branch deletion;
* commits only when content actually changed (blob SHA comparison);
* tokens are read from the environment and never logged;
* the resulting commit and raw URLs are verified after publishing;
* on any failure the previous published files are left untouched.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .logging_setup import get_logger, redact
from .models import iso, utcnow

log = get_logger("radar.publish")

API = "https://api.github.com"


@dataclass
class PublishResult:
    ok: bool
    commit_sha: str | None = None
    commit_url: str | None = None
    changed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verified_urls: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "commit_sha": self.commit_sha,
            "commit_url": self.commit_url,
            "changed": self.changed,
            "skipped": self.skipped,
            "errors": self.errors,
            "verified_urls": self.verified_urls,
        }


class GitHubPublisher:
    def __init__(
        self,
        owner: str,
        repo: str,
        branch: str,
        token: str,
        user_agent: str = "IranVPNRadar/1.0",
        allow_prefixes: tuple[str, ...] = ("subscriptions/", "status/", "sources/", "README"),
    ):
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.token = token
        self.user_agent = user_agent
        self.allow_prefixes = allow_prefixes

    # ------------------------------------------------------------------ utils
    def _request(self, method: str, path: str, payload: dict | None = None) -> tuple[int, Any]:
        url = f"{API}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": self.user_agent,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
                return resp.status, (json.loads(body) if body else None)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"message": body[:200]}
            return exc.code, parsed
        except Exception as exc:
            return 0, {"message": redact(str(exc))}

    def _allowed(self, path: str) -> bool:
        normalized = path.lstrip("/")
        return any(normalized.startswith(prefix) for prefix in self.allow_prefixes)

    def _get_sha(self, path: str) -> str | None:
        status, data = self._request("GET", f"/repos/{self.owner}/{self.repo}/contents/{path}?ref={self.branch}")
        if status == 200 and isinstance(data, dict):
            return data.get("sha")
        return None

    def any_changed(self, files: dict[str, str]) -> bool:
        """True when at least one file differs from what the branch serves."""
        for path, content in files.items():
            if not self._allowed(path):
                continue
            current = self._get_content(path)
            if current is None or current != content:
                return True
        return False

    def _get_content(self, path: str) -> str | None:
        status, data = self._request("GET", f"/repos/{self.owner}/{self.repo}/contents/{path}?ref={self.branch}")
        if status == 200 and isinstance(data, dict) and data.get("content"):
            try:
                return base64.b64decode(data["content"]).decode("utf-8", "replace")
            except Exception:
                return None
        return None

    # -------------------------------------------------------------- publishing
    def publish_files(
        self,
        files: dict[str, str],
        message: str,
        dry_run: bool = False,
        retries: int = 3,
    ) -> PublishResult:
        """Publish ``{repo_path: content}`` in a single commit.

        Files whose content already matches the branch are skipped, so a cycle
        that changes nothing produces no commit.
        """
        result = PublishResult(ok=True)
        changed: list[tuple[str, str, str | None]] = []  # path, content, sha

        for path, content in files.items():
            if not self._allowed(path):
                result.errors.append(f"refusing to write disallowed path: {path}")
                result.ok = False
                continue
            current = self._get_content(path)
            if current is not None and current == content:
                result.skipped.append(path)
                continue
            sha = self._get_sha(path)
            changed.append((path, content, sha))

        if not changed:
            log.info("nothing to publish; all files unchanged")
            return result

        if dry_run:
            result.changed = [p for p, _, _ in changed]
            log.info("dry run: would publish", extra={"context": {"files": result.changed}})
            return result

        # Build a single commit via the Git Data API (tree + commit + ref).
        for attempt in range(retries):
            status, ref = self._request("GET", f"/repos/{self.owner}/{self.repo}/git/ref/heads/{self.branch}")
            if status != 200 or not isinstance(ref, dict):
                result.errors.append(f"could not read branch ref: {ref}")
                return _fail(result)
            base_commit = ref["object"]["sha"]

            status, commit = self._request(
                "GET", f"/repos/{self.owner}/{self.repo}/git/commits/{base_commit}"
            )
            if status != 200 or not isinstance(commit, dict):
                result.errors.append("could not read base commit")
                return _fail(result)
            base_tree = commit["tree"]["sha"]

            entries = []
            for path, content, _sha in changed:
                status, blob = self._request(
                    "POST",
                    f"/repos/{self.owner}/{self.repo}/git/blobs",
                    {"content": content, "encoding": "utf-8"},
                )
                if status not in (200, 201) or not isinstance(blob, dict):
                    result.errors.append(f"blob create failed for {path}: {blob}")
                    return _fail(result)
                entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})

            status, tree = self._request(
                "POST",
                f"/repos/{self.owner}/{self.repo}/git/trees",
                {"base_tree": base_tree, "tree": entries},
            )
            if status not in (200, 201) or not isinstance(tree, dict):
                result.errors.append(f"tree create failed: {tree}")
                return _fail(result)

            status, new_commit = self._request(
                "POST",
                f"/repos/{self.owner}/{self.repo}/git/commits",
                {"message": message, "tree": tree["sha"], "parents": [base_commit]},
            )
            if status not in (200, 201) or not isinstance(new_commit, dict):
                result.errors.append(f"commit create failed: {new_commit}")
                return _fail(result)

            status, updated = self._request(
                "PATCH",
                f"/repos/{self.owner}/{self.repo}/git/refs/heads/{self.branch}",
                {"sha": new_commit["sha"], "force": False},
            )
            if status in (200, 201):
                result.commit_sha = new_commit["sha"]
                result.commit_url = f"https://github.com/{self.owner}/{self.repo}/commit/{new_commit['sha']}"
                result.changed = [p for p, _, _ in changed]
                log.info(
                    "published commit",
                    extra={"context": {"sha": result.commit_sha, "files": len(result.changed)}},
                )
                return result
            # 422 usually means the ref moved (concurrent writer) — retry.
            if status == 422 and attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            result.errors.append(f"ref update failed: {updated}")
            return _fail(result)

        result.errors.append("exhausted retries")
        return _fail(result)

    # --------------------------------------------------------------- verifying
    def verify_raw(self, name: str, expected_content: str, attempts: int = 5) -> bool:
        """Verify the raw subscription URL returns the expected content."""
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/subscriptions/{name}"
        for attempt in range(attempts):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Cache-Control": "no-cache"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    body = resp.read().decode("utf-8", "replace")
                if body == expected_content:
                    return True
            except Exception:
                pass
            time.sleep(1.5 * (attempt + 1))
        return False


def _fail(result: PublishResult) -> PublishResult:
    result.ok = False
    return result


def publisher_from_settings(settings, token: str | None = None) -> GitHubPublisher:
    token = token or ""
    return GitHubPublisher(
        owner=settings.owner,
        repo=settings.repo,
        branch=settings.branch,
        token=token,
        user_agent=settings.user_agent,
    )
