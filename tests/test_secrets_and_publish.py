"""Secret redaction, secret scanning and publishing allow-list tests."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar.logging_setup import redact, register_secret  # noqa: E402
from radar.publish import GitHubPublisher  # noqa: E402
from radar.secrets_scan import scan_text  # noqa: E402


class TestRedaction(unittest.TestCase):
    def test_github_token_redacted(self):
        text = "token is ghp_" + "A" * 36
        self.assertNotIn("ghp_" + "A" * 36, redact(text))

    def test_url_credentials_redacted(self):
        out = redact("clone https://user:s3cretpass@github.com/x/y.git")
        self.assertNotIn("s3cretpass", out)

    def test_registered_secret_redacted(self):
        register_secret("supersecretvalue123")
        self.assertNotIn("supersecretvalue123", redact("value=supersecretvalue123"))


class TestSecretScan(unittest.TestCase):
    def test_detects_github_token(self):
        findings = scan_text("README.md", "ghp_" + "Z" * 36)
        self.assertTrue(any(f.kind == "github_token" for f in findings))

    def test_detects_private_key(self):
        findings = scan_text("k.txt", "-----BEGIN RSA PRIVATE KEY-----")
        self.assertTrue(any(f.kind == "private_key_block" for f in findings))

    def test_placeholder_allowed(self):
        findings = scan_text("README.md", 'password: "your_password_here"')
        self.assertEqual([f for f in findings if f.kind == "assigned_secret"], [])

    def test_scanner_source_ignored(self):
        # the scanner's own patterns must not trigger on itself
        findings = scan_text("src/radar/secrets_scan.py", "ghp_" + "A" * 36)
        self.assertEqual(findings, [])

    def test_internal_state_ignored(self):
        # gitignored internal state is never committed, so it is out of scope
        findings = scan_text("data/configs.json", "ss://x:y@host:8388")
        self.assertEqual(findings, [])

    def test_subscription_payload_allows_public_uris(self):
        # public config URIs are the intended payload of published files
        findings = scan_text("subscriptions/vless", "vless://uuid:pw@example.com:443#tag")
        self.assertEqual(findings, [])

    def test_subscription_payload_still_catches_real_tokens(self):
        findings = scan_text("subscriptions/all", "ghp_" + "A" * 36)
        self.assertTrue(any(f.kind == "github_token" for f in findings))


class TestPublishAllowList(unittest.TestCase):
    def setUp(self):
        self.pub = GitHubPublisher("o", "r", "main", token="x")

    def test_allows_subscription_paths(self):
        self.assertTrue(self.pub._allowed("subscriptions/all"))
        self.assertTrue(self.pub._allowed("status/summary.json"))
        self.assertTrue(self.pub._allowed("sources/seed_sources.json"))

    def test_rejects_unrelated_paths(self):
        self.assertFalse(self.pub._allowed("src/radar/publish.py"))
        self.assertFalse(self.pub._allowed(".github/workflows/ci.yml"))
        self.assertFalse(self.pub._allowed("../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
