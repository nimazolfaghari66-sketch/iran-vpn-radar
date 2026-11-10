"""Failure policy, de-duplication and Iran-gating tests."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar import quality  # noqa: E402
from radar.dedupe import dedupe  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402


def mk(uri):
    return parse_uri(uri)


class TestFailurePolicy(unittest.TestCase):
    def test_first_failure_is_degraded_second_is_failed(self):
        conf = mk("vless://u@a.com:443?security=tls#a")
        quality.apply_failure(conf, "timeout")
        self.assertEqual(conf.status, cfg.DEGRADED)
        quality.apply_failure(conf, "timeout")
        self.assertEqual(conf.status, cfg.FAILED)

    def test_success_restores_to_working(self):
        conf = mk("vless://u@a.com:443?security=tls#a")
        quality.apply_failure(conf, "x")
        quality.apply_failure(conf, "x")
        self.assertEqual(conf.status, cfg.FAILED)
        quality.apply_success(conf, {"latency_ms": 120})
        self.assertEqual(conf.status, cfg.WORKING)
        self.assertEqual(conf.consecutive_failures, 0)

    def test_expired_is_removed(self):
        conf = mk("vless://u@a.com:443?security=tls#a")
        quality.apply_failure(conf, "expired", expired=True)
        self.assertEqual(conf.status, cfg.EXPIRED)

    def test_publishable_states(self):
        conf = mk("vless://u@a.com:443?security=tls#a")
        self.assertFalse(quality.is_publishable(conf))
        quality.apply_success(conf, {})
        self.assertTrue(quality.is_publishable(conf))
        quality.apply_failure(conf, "x")
        self.assertTrue(quality.is_publishable(conf))  # DEGRADED still published


class TestDedupe(unittest.TestCase):
    def test_duplicates_collapse(self):
        a = mk("vless://u@a.com:443?security=tls#one")
        b = mk("vless://u@a.com:443?security=tls#two")
        c = mk("vless://other@a.com:443?security=tls#three")
        unique, dups = dedupe([a, b, c])
        self.assertEqual(len(unique), 2)
        self.assertEqual(len(dups), 1)

    def test_verified_preferred_over_fresh(self):
        verified = mk("vless://u@a.com:443?security=tls#x")
        quality.apply_success(verified, {})
        fresh = mk("vless://u@a.com:443?security=tls#y")
        unique, _ = dedupe([fresh, verified])
        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0].status, cfg.WORKING)


class TestSelection(unittest.TestCase):
    def test_priority_fresh_then_retest_then_refresh(self):
        fresh = mk("vless://u@a.com:443?security=tls#1")
        retest = mk("vless://u@b.com:443?security=tls#2")
        quality.apply_failure(retest, "x")
        quality.apply_failure(retest, "x")  # FAILED
        working = mk("vless://u@c.com:443?security=tls#3")
        quality.apply_success(working, {})
        store = {c.fingerprint: c for c in (fresh, retest, working)}
        selected = quality.select_for_testing(store, max_batch=3)
        self.assertEqual(selected[0].fingerprint, fresh.fingerprint)
        self.assertIn(retest.fingerprint, [s.fingerprint for s in selected])


if __name__ == "__main__":
    unittest.main()
