"""Global tunnel verification tier tests.

These lock in the honesty guarantees of the candidate pool:

* a tunnel-verified result is labelled GLOBAL, never IRAN;
* the tier can never move a configuration into an Iran-publishable state;
* candidates never leak into the Iran-verified subscription files;
* ranking prefers Iranian reachability evidence.
"""

import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config as cfg  # noqa: E402
from radar import generate, quality, tunnel_verify  # noqa: E402
from radar.normalize import parse_uri  # noqa: E402


def _conf(uri):
    return parse_uri(uri)


class TestTunnelTier(unittest.TestCase):
    def test_tunnel_result_never_publishes_to_iran_files(self):
        conf = _conf("vless://u1@a.com:443?security=tls#a")
        conf.port = 443
        configs = {conf.fingerprint: conf}
        record = tunnel_verify.TunnelRecord(
            fingerprint=conf.fingerprint,
            protocol=conf.protocol,
            endpoint=conf.endpoint,
            success=True,
            location="GLOBAL",
            grade="A",
        )
        tunnel_verify._apply_tunnel_result(conf, True, record)
        # Tunnel tier set its own field...
        self.assertEqual(conf.tunnel_status, tunnel_verify.TUNNEL_VERIFIED)
        # ...but the Iran state machine is untouched.
        self.assertEqual(conf.status, cfg.DISCOVERED)
        self.assertFalse(quality.is_publishable(conf))

        files = generate.build_files(configs, Path("/tmp/iranfiles"))
        by_name = {f.name: f for f in files}
        self.assertEqual(by_name["all"].count, 0)
        self.assertEqual(by_name["vless"].count, 0)

    def test_candidate_files_include_tunnel_verified(self):
        conf = _conf("vless://u1@a.com:443?security=tls#a")
        conf.port = 443
        configs = {conf.fingerprint: conf}
        record = tunnel_verify.TunnelRecord(
            fingerprint=conf.fingerprint,
            protocol=conf.protocol,
            endpoint=conf.endpoint,
            success=True,
            grade="A",
        )
        tunnel_verify._apply_tunnel_result(conf, True, record)
        files = generate.build_candidate_files(configs, Path("/tmp/cand"))
        by_name = {f.name: f for f in files}
        self.assertEqual(by_name["candidates/all"].count, 1)
        self.assertEqual(by_name["candidates/vless"].count, 1)

    def test_location_is_never_iran(self):
        conf = _conf("trojan://pw@b.com:443#b")
        conf.port = 443
        record = tunnel_verify.TunnelRecord(
            fingerprint=conf.fingerprint,
            protocol=conf.protocol,
            endpoint=conf.endpoint,
            success=True,
        )
        self.assertEqual(record.location, "GLOBAL")
        self.assertNotEqual(record.location, "IRAN")

    def test_second_consecutive_failure_drops_candidate(self):
        conf = _conf("vless://u1@a.com:443?security=tls#a")
        conf.port = 443
        good = tunnel_verify.TunnelRecord(conf.fingerprint, conf.protocol, conf.endpoint, True, grade="B")
        tunnel_verify._apply_tunnel_result(conf, True, good)
        self.assertEqual(conf.tunnel_status, tunnel_verify.TUNNEL_VERIFIED)

        bad = tunnel_verify.TunnelRecord(conf.fingerprint, conf.protocol, conf.endpoint, False, error="x")
        tunnel_verify._apply_tunnel_result(conf, False, bad)
        self.assertEqual(conf.tunnel_status, tunnel_verify.TUNNEL_VERIFIED)  # one transient failure retained
        tunnel_verify._apply_tunnel_result(conf, False, bad)
        self.assertEqual(conf.tunnel_status, tunnel_verify.TUNNEL_FAILED)

    def test_ranking_prefers_iran_reachable(self):
        plain = _conf("vless://u1@a.com:443?security=tls#a")
        plain.port = 443
        reachable = _conf("vless://u2@b.com:443?security=tls#b")
        reachable.port = 443
        reachable.iran_reachability = "IRAN_TLS_OK"
        for conf in (plain, reachable):
            rec = tunnel_verify.TunnelRecord(conf.fingerprint, conf.protocol, conf.endpoint, True, grade="A")
            tunnel_verify._apply_tunnel_result(conf, True, rec)
        ranked = tunnel_verify.candidate_configs({plain.fingerprint: plain, reachable.fingerprint: reachable})
        self.assertEqual(ranked[0].fingerprint, reachable.fingerprint)

    def test_base64_roundtrip_for_candidates(self):
        conf = _conf("vless://u1@a.com:443?security=tls#a")
        conf.port = 443
        rec = tunnel_verify.TunnelRecord(conf.fingerprint, conf.protocol, conf.endpoint, True, grade="A")
        tunnel_verify._apply_tunnel_result(conf, True, rec)
        files = generate.build_candidate_files({conf.fingerprint: conf}, Path("/tmp/cand2"))
        gen = {f.name: f for f in files}["candidates/all"]
        self.assertEqual(base64.b64decode(gen.b64_content).decode(), gen.content)


if __name__ == "__main__":
    unittest.main()
