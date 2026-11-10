"""The central safety property: only genuine Iran results may verify a config.

These tests prove that a non-Iranian probe can never move a configuration into
a publishable state, and that with no probe configured everything stays
PENDING_IRAN_TEST.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar.iran_probe import run_iran_tests  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402
from radar.probe_protocol import ProbeInfo, TestOutcome, validate_result  # noqa: E402


class FakeSettings:
    probe_mode = "unavailable"
    probe_url = None
    probe_token = None
    probe_timeout = 10
    local_is_iran = False


class TestIranGate(unittest.TestCase):
    def _configs(self, n=3):
        out = {}
        for i in range(n):
            conf = parse_uri(f"vless://u{i}@host{i}.com:443?security=tls#c{i}")
            out[conf.fingerprint] = conf
        return out

    def test_no_probe_marks_pending_and_never_publishes(self):
        configs = self._configs()
        report = run_iran_tests(configs, FakeSettings(), max_batch=10)
        self.assertEqual(report.status, "unavailable")
        for conf in configs.values():
            self.assertEqual(conf.status, cfg.PENDING_IRAN_TEST)
        self.assertFalse(any(c.status in cfg.PUBLISHABLE_STATES for c in configs.values()))

    def test_foreign_probe_results_are_rejected(self):
        foreign = ProbeInfo(name="de", country="DE")
        result = {"fingerprint": "abc", "success": True, "probe_is_iran": True}
        ok, reason = validate_result(result, foreign)
        self.assertFalse(ok)
        self.assertIn("not Iran", reason)

    def test_iran_probe_results_accepted(self):
        iran = ProbeInfo(name="ir", country="IR")
        ok, _ = validate_result({"fingerprint": "abc", "success": True}, iran)
        self.assertTrue(ok)

    def test_result_without_fingerprint_rejected(self):
        iran = ProbeInfo(name="ir", country="IR")
        ok, reason = validate_result({"success": True}, iran)
        self.assertFalse(ok)

    def test_local_iran_requires_explicit_flag(self):
        class S(FakeSettings):
            probe_mode = "local_iran"
            local_is_iran = False

        configs = self._configs()
        report = run_iran_tests(configs, S(), max_batch=10)
        self.assertEqual(report.status, "unavailable")
        for conf in configs.values():
            self.assertEqual(conf.status, cfg.PENDING_IRAN_TEST)


if __name__ == "__main__":
    unittest.main()
