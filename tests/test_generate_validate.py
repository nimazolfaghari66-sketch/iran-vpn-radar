"""Subscription generation and validation tests."""

import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar import quality  # noqa: E402
from radar.generate import build_files, write_files  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402
from radar.validate import validate_files  # noqa: E402


def working(uri):
    conf = parse_uri(uri)
    quality.apply_success(conf, {})
    return conf


class TestGeneration(unittest.TestCase):
    def setUp(self):
        self.configs = {}
        for uri in (
            "vless://u1@a.com:443?security=tls#a",
            "vless://u2@b.com:443?security=tls#b",
            "trojan://pw@c.com:443#c",
            "ss://" + base64.b64encode(b"aes-256-gcm:pw").decode() + "@d.com:8388#d",
        ):
            conf = working(uri)
            self.configs[conf.fingerprint] = conf

    def test_all_and_protocol_files(self):
        files = build_files(self.configs, Path("/tmp/x"))
        by_name = {f.name: f for f in files}
        self.assertEqual(by_name["all"].count, 4)
        self.assertEqual(by_name["vless"].count, 2)
        self.assertEqual(by_name["trojan"].count, 1)
        self.assertEqual(by_name["shadowsocks"].count, 1)
        self.assertEqual(by_name["vmess"].count, 0)

    def test_only_publishable_included(self):
        pending = parse_uri("vless://pending@z.com:443?security=tls#z")
        self.configs[pending.fingerprint] = pending
        files = build_files(self.configs, Path("/tmp/x"))
        by_name = {f.name: f for f in files}
        self.assertEqual(by_name["all"].count, 4)

    def test_lf_newlines_and_trailing_newline(self):
        files = build_files(self.configs, Path("/tmp/x"))
        for gen in files:
            if gen.content:
                self.assertTrue(gen.content.endswith("\n"))
                self.assertNotIn("\r", gen.content)

    def test_base64_roundtrip(self):
        files = build_files(self.configs, Path("/tmp/x"))
        gen = {f.name: f for f in files}["all"]
        decoded = base64.b64decode(gen.b64_content).decode()
        self.assertEqual(decoded, gen.content)

    def test_validation_passes(self):
        files = build_files(self.configs, Path("/tmp/x"))
        report = validate_files(files)
        self.assertTrue(report.ok, report.to_dict())

    def test_write_and_validate_against_previous(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = build_files(self.configs, Path(tmp))
            write_files(files)
            report = validate_files(files, previous_dir=Path(tmp))
            self.assertTrue(report.ok)

    def test_regression_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            prev = Path(tmp) / "all"
            prev.write_text("vless://u1@a.com:443?security=tls#a\n", encoding="utf-8")
            empty = build_files({}, Path(tmp))
            report = validate_files(empty, previous_dir=Path(tmp))
            self.assertFalse(report.ok)


if __name__ == "__main__":
    unittest.main()
