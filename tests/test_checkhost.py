"""Tests for the Check-Host Iranian vantage-point module.

The important property under test is that Check-Host is *diagnostic only*: it
classifies reachability, but can never produce ``IRAN_FULL_TUNNEL_VERIFIED`` and
can never move a configuration into a publishable state.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import checkhost as ch  # noqa: E402
from radar import config as cfg  # noqa: E402
from radar.models import Config  # noqa: E402


class TestNodeParsing(unittest.TestCase):
    def test_parse_node_from_registry_shape(self):
        node = ch.parse_node(
            "ir1.node.check-host.net",
            {"asn": "AS47430", "ip": "185.105.238.209", "location": ["ir", "Iran", "Tehran"]},
        )
        self.assertTrue(node.is_iran)
        self.assertEqual(node.city, "Tehran")
        self.assertEqual(node.asn, "AS47430")
        self.assertEqual(node.ip, "185.105.238.209")

    def test_non_iran_node_is_excluded(self):
        node = ch.parse_node("us1.node.check-host.net", {"location": ["us", "USA", "Los Angeles"]})
        self.assertFalse(node.is_iran)

    def test_historical_city_lookup(self):
        node = ch.parse_node("x", {"ip": "77.104.108.3", "location": ["ir", "Iran", "Shiraz"]})
        self.assertEqual(node.historical_city, "Shiraz")

    def test_compare_detects_missing_and_city_change(self):
        # One historic IP present with the right city, one present but moved,
        # one absent entirely.
        nodes = [
            ch.parse_node("a", {"ip": "185.105.238.209", "location": ["ir", "Iran", "Tehran"]}),
            ch.parse_node("b", {"ip": "77.104.108.3", "location": ["ir", "Iran", "Karaj"]}),
            ch.parse_node("c", {"ip": "10.0.0.1", "location": ["ir", "Iran", "Tabriz"]}),
        ]
        report = ch.compare_with_historical(nodes)
        active_ips = {e["ip"] for e in report["still_active"]}
        self.assertIn("185.105.238.209", active_ips)
        self.assertIn("77.104.108.3", active_ips)
        self.assertIn("195.182.38.164", {e["ip"] for e in report["missing"]})
        self.assertEqual(len(report["city_changed"]), 1)
        self.assertEqual(report["city_changed"][0]["current_city"], "Karaj")
        # The unknown node is reported as new, never as historic.
        self.assertIn("10.0.0.1", {n["ip"] for n in report["new_since_history"]})


class TestClassifiers(unittest.TestCase):
    def test_tcp_reachable(self):
        ok, cls, latency, _ = ch.classify_tcp([{"address": "1.2.3.4", "time": 0.081}])
        self.assertTrue(ok)
        self.assertEqual(cls, cfg.IRAN_TCP_REACHABLE)
        self.assertAlmostEqual(latency, 81.0, places=1)

    def test_tcp_timeout(self):
        ok, cls, _, detail = ch.classify_tcp([{"error": "Connection timed out"}])
        self.assertFalse(ok)
        self.assertEqual(cls, cfg.IRAN_TIMEOUT)
        self.assertIn("timed out", detail)

    def test_dns_ok(self):
        ok, cls, _, _ = ch.classify_dns([{"A": ["1.2.3.4"], "AAAA": [], "TTL": 20}])
        self.assertTrue(ok)
        self.assertEqual(cls, cfg.IRAN_DNS_OK)

    def test_dns_ip_literal_is_not_success(self):
        ok, cls, _, detail = ch.classify_dns([{"PTR": [], "TTL": None}])
        self.assertFalse(ok)
        self.assertEqual(cls, cfg.IRAN_UNREACHABLE)
        self.assertIn("IP literal", detail)

    def test_http_reachable(self):
        ok, cls, latency, _ = ch.classify_http([[1, 0.158, "OK", "200", "1.2.3.4"]])
        self.assertTrue(ok)
        self.assertEqual(cls, cfg.IRAN_HTTP_REACHABLE)
        self.assertAlmostEqual(latency, 158.0, places=1)

    def test_udp_timeout(self):
        ok, cls, _, _ = ch.classify_udp([{"address": "1.1.1.1", "timeout": 1}])
        self.assertFalse(ok)
        self.assertEqual(cls, cfg.IRAN_TIMEOUT)

    def test_no_result_defaults_unreachable(self):
        for fn in (ch.classify_tcp, ch.classify_dns, ch.classify_http, ch.classify_udp):
            ok, cls, _, _ = fn(None)
            self.assertFalse(ok)
            self.assertEqual(cls, cfg.IRAN_UNREACHABLE)


class TestSummarizeNeverVerifiesTunnel(unittest.TestCase):
    def _nodes(self):
        return [
            ch.NodeInfo("ir1", "185.105.238.209", "Iran", "Tehran", "AS47430", "ir"),
            ch.NodeInfo("ir2", "195.182.38.164", "Iran", "Isfahan", "AS209279", "ir"),
        ]

    def test_reachable_never_becomes_full_tunnel(self):
        conf = Config(uri="vless://u@example.com:443", protocol="vless", host="example.com", port=443)
        record = ch.CheckHostRecord(conf.fingerprint, conf.host, conf.port, conf.protocol)
        record.checks.append(ch.NodeCheck("ir1", "Tehran", "AS47430", "1.1.1.1", "tcp", True, cfg.IRAN_TCP_REACHABLE, 80.0))
        ch._summarize(record)
        self.assertEqual(record.summary, cfg.IRAN_TCP_REACHABLE)
        self.assertNotEqual(record.summary, cfg.IRAN_FULL_TUNNEL_VERIFIED)
        # IRAN_FULL_TUNNEL_VERIFIED exists as a concept but is deliberately not
        # part of any Check-Host classification set.
        self.assertNotIn(cfg.IRAN_FULL_TUNNEL_VERIFIED, cfg.CHECKHOST_CLASSIFICATIONS)
        self.assertNotIn(cfg.IRAN_FULL_TUNNEL_VERIFIED, cfg.CHECKHOST_REACHABLE)

    def test_no_checkhost_classification_is_publishable(self):
        for cls in cfg.CHECKHOST_CLASSIFICATIONS:
            self.assertNotIn(cls, cfg.PUBLISHABLE_STATES)

    def test_config_status_unchanged_by_checkhost(self):
        """A Check-Host round must not alter configuration status."""
        conf = Config(uri="vless://u@example.com:443", protocol="vless", host="example.com", port=443)
        self.assertEqual(conf.status, cfg.DISCOVERED)
        record = ch.CheckHostRecord(conf.fingerprint, conf.host, conf.port, conf.protocol)
        record.checks.append(ch.NodeCheck("ir1", "Tehran", "AS47430", "1.1.1.1", "tcp", True, cfg.IRAN_TCP_REACHABLE, 80.0))
        ch._summarize(record)
        # test_config / _summarize touch only the record, never the Config.
        self.assertEqual(conf.status, cfg.DISCOVERED)


class TestStorageHistory(unittest.TestCase):
    def test_results_retain_history_per_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            for i in range(8):
                rec = ch.CheckHostRecord(f"fp{i % 2}", "example.com", 443, "vless")
                ch.save_results(state, [rec], keep_per_fingerprint=3)
            records = ch.load_results(state)
            fps = [r["fingerprint"] for r in records]
            self.assertEqual(fps.count("fp0"), 3)
            self.assertEqual(fps.count("fp1"), 3)

    def test_summarize_records_by_city_and_protocol(self):
        records = [
            {
                "fingerprint": "a",
                "protocol": "vless",
                "checked_at": "2026-01-01T00:00:00Z",
                "summary": cfg.IRAN_TCP_REACHABLE,
                "cities_reachable": ["Tehran"],
                "cities_unreachable": ["Qom"],
            },
            {
                "fingerprint": "b",
                "protocol": "vmess",
                "checked_at": "2026-01-01T00:00:00Z",
                "summary": cfg.IRAN_TIMEOUT,
                "cities_reachable": [],
                "cities_unreachable": ["Tehran"],
            },
        ]
        out = ch.summarize_records(records)
        self.assertEqual(out["configs_tested"], 2)
        self.assertEqual(out["by_protocol"]["vless"]["reachable"], 1)
        self.assertEqual(out["by_protocol"]["vmess"]["reachable"], 0)
        self.assertEqual(out["by_city"]["Tehran"]["reachable"], 1)
        self.assertEqual(out["by_city"]["Tehran"]["unreachable"], 1)

    def test_latest_result_wins(self):
        records = [
            {"fingerprint": "a", "protocol": "vless", "checked_at": "2026-01-01T00:00:00Z", "summary": cfg.IRAN_TIMEOUT, "cities_reachable": [], "cities_unreachable": ["Tehran"]},
            {"fingerprint": "a", "protocol": "vless", "checked_at": "2026-01-02T00:00:00Z", "summary": cfg.IRAN_TCP_REACHABLE, "cities_reachable": ["Tehran"], "cities_unreachable": []},
        ]
        out = ch.summarize_records(records)
        self.assertEqual(out["configs_tested"], 1)
        self.assertEqual(out["by_summary"].get(cfg.IRAN_TCP_REACHABLE), 1)


class TestSampleSelection(unittest.TestCase):
    def test_sample_prefers_protocol_diversity(self):
        configs = {}
        for i, proto in enumerate(["vless", "vmess", "trojan", "vless", "vless"]):
            c = Config(uri=f"{proto}://u@h{i}.example.com:443", protocol=proto, host=f"h{i}.example.com", port=443)
            configs[c.fingerprint] = c
        sample = ch.select_sample(configs, 3)
        self.assertEqual(len(sample), 3)
        self.assertEqual(len({c.protocol for c in sample}), 3)

    def test_sample_skips_duplicates(self):
        a = Config(uri="vless://u@a.example.com:443", protocol="vless", host="a.example.com", port=443)
        b = Config(uri="vless://u@b.example.com:443", protocol="vless", host="b.example.com", port=443)
        b.status = cfg.DUPLICATE
        sample = ch.select_sample({a.fingerprint: a, b.fingerprint: b}, 5)
        self.assertEqual([c.host for c in sample], ["a.example.com"])


if __name__ == "__main__":
    unittest.main()
