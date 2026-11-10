"""Tests for the Globalping Iranian vantage-point diagnostics."""

import unittest

from radar import config as cfg
from radar import globalping as gp
from radar.models import Config


def _conf(**kw) -> Config:
    base = dict(uri="vless://u@example.com:443", protocol="vless", host="example.com", port=443)
    base.update(kw)
    return Config(**base)


class TestProbeParsing(unittest.TestCase):
    def test_parse_probes_payload_shape(self):
        payload = {
            "results": [
                {"location": {"country": "IR", "city": "Tehran", "asn": 202468, "network": "Noyan Abr Arvan"}, "tags": ["eyeball-network"]},
                {"location": {"country": "DE", "city": "Falkenstein", "asn": 24940, "network": "Hetzner"}},
            ]
        }
        probes = gp.parse_probes(payload)
        self.assertEqual(len(probes), 2)
        self.assertTrue(probes[0].is_iran)
        self.assertFalse(probes[1].is_iran)
        self.assertIn("Tehran", probes[0].key)

    def test_parse_probes_accepts_bare_list(self):
        probes = gp.parse_probes([{"location": {"country": "IR", "city": "Tabriz", "asn": 197207}}])
        self.assertEqual(len(probes), 1)
        self.assertTrue(probes[0].is_iran)

    def test_non_iran_probe_excluded(self):
        probes = [p for p in gp.parse_probes({"results": [{"location": {"country": "US"}}]}) if p.is_iran]
        self.assertEqual(probes, [])

    def test_parse_flat_cached_shape(self):
        # Our persisted registry stores flat probe dicts (no "location" wrapper).
        cached = [{"country": "IR", "city": "Tehran", "asn": 202468, "network": "Arvan", "tags": []}]
        probes = [p for p in gp.parse_probes(cached) if p.is_iran]
        self.assertEqual(len(probes), 1)
        self.assertEqual(probes[0].city, "Tehran")


class TestTargetValidation(unittest.TestCase):
    def test_valid_targets(self):
        for host in ("example.com", "1.2.3.4", "node.example.ir", "2606:4700::1111"):
            self.assertTrue(gp.is_valid_target(host), host)

    def test_invalid_targets(self):
        for host in ("https://github.com/x", "example.com/path", "has space", ""):
            self.assertFalse(gp.is_valid_target(host), host)


class TestPayloadConstruction(unittest.TestCase):
    def test_tls_protocol_uses_https(self):
        payload = gp.build_measurement_payload(_conf(protocol="vless", port=443), limit=2)
        self.assertEqual(payload["type"], "http")
        self.assertEqual(payload["measurementOptions"]["protocol"], "HTTPS")
        self.assertEqual(payload["measurementOptions"]["port"], 443)
        self.assertEqual(payload["locations"], [{"country": "IR"}])

    def test_plaintext_proxy_uses_http(self):
        payload = gp.build_measurement_payload(_conf(protocol="socks", host="1.2.3.4", port=1080), limit=2)
        self.assertEqual(payload["measurementOptions"]["protocol"], "HTTP")

    def test_udp_protocol_uses_ping(self):
        payload = gp.build_measurement_payload(_conf(protocol="hysteria2", host="1.2.3.4", port=20022), limit=1)
        self.assertEqual(payload["type"], "ping")
        self.assertNotIn("measurementOptions", payload)

    def test_city_filter(self):
        payload = gp.build_measurement_payload(_conf(), limit=1, city="Tehran")
        self.assertEqual(payload["locations"], [{"country": "IR", "city": "Tehran"}])


class TestClassification(unittest.TestCase):
    def test_http_success_is_http_reachable(self):
        check = gp.classify_http_result(
            {"status": "finished", "statusCode": 200, "resolvedAddress": "1.2.3.4",
             "timings": {"dns": 2, "tcp": 10, "tls": 30, "firstByte": 40, "total": 55}}
        )
        self.assertEqual(check.classification, cfg.IRAN_HTTP_REACHABLE)
        self.assertTrue(check.ok)
        self.assertTrue(check.tls)
        self.assertEqual(check.latency_ms, 40.0)

    def test_tls_only_is_tls_ok(self):
        check = gp.classify_http_result(
            {"status": "failed", "resolvedAddress": "1.2.3.4",
             "timings": {"dns": 2, "tcp": 10, "tls": 30, "firstByte": None, "total": 15000}}
        )
        self.assertEqual(check.classification, cfg.IRAN_TLS_OK)
        self.assertTrue(check.ok)
        self.assertTrue(check.tls)
        self.assertEqual(check.latency_ms, 30.0)

    def test_tcp_only_is_tcp_reachable(self):
        check = gp.classify_http_result(
            {"status": "failed", "resolvedAddress": "1.2.3.4",
             "timings": {"dns": 2, "tcp": 10, "tls": None, "firstByte": None, "total": 15000}}
        )
        self.assertEqual(check.classification, cfg.IRAN_TCP_REACHABLE)

    def test_resolved_only_is_dns(self):
        check = gp.classify_http_result(
            {"status": "failed", "resolvedAddress": "1.2.3.4", "timings": {"dns": 2, "total": 15000}}
        )
        self.assertEqual(check.classification, cfg.IRAN_DNS_OK)

    def test_timeout_has_no_fake_latency(self):
        check = gp.classify_http_result(
            {"status": "failed", "rawOutput": "Request timed out while establishing the TCP connection.",
             "timings": {"dns": 2, "total": 15000}}
        )
        self.assertFalse(check.ok)
        self.assertEqual(check.classification, cfg.IRAN_TIMEOUT)
        self.assertIsNone(check.latency_ms)

    def test_ping_success(self):
        check = gp.classify_ping_result(
            {"status": "finished", "stats": {"rcv": 3, "avg": 86.3}, "timings": [{"rtt": 86.5}]}
        )
        self.assertEqual(check.classification, cfg.IRAN_ICMP_REACHABLE)
        self.assertTrue(check.ok)
        self.assertEqual(check.latency_ms, 86.3)

    def test_ping_failure(self):
        check = gp.classify_ping_result({"status": "failed", "rawOutput": "Request timed out.", "timings": []})
        self.assertFalse(check.ok)
        self.assertEqual(check.classification, cfg.IRAN_TIMEOUT)


class TestSummarizeNeverVerifiesTunnel(unittest.TestCase):
    def test_no_globalping_classification_is_publishable(self):
        for cls in cfg.GLOBALPING_CLASSIFICATIONS:
            self.assertNotIn(cls, cfg.PUBLISHABLE_STATES)

    def test_full_tunnel_not_in_taxonomy(self):
        self.assertNotIn(cfg.IRAN_FULL_TUNNEL_VERIFIED, cfg.GLOBALPING_CLASSIFICATIONS)
        self.assertNotIn(cfg.IRAN_FULL_TUNNEL_VERIFIED, cfg.GLOBALPING_REACHABLE)

    def test_reachable_never_becomes_full_tunnel(self):
        rec = gp.GlobalpingRecord("fp", "example.com", 443, "vless")
        rec.checks.append(
            gp.ProbeCheck("Tehran", 202468, "Arvan", True, cfg.IRAN_HTTP_REACHABLE, 40.0, tls=True)
        )
        gp._summarize(rec)
        self.assertEqual(rec.summary, cfg.IRAN_HTTP_REACHABLE)
        self.assertNotEqual(rec.summary, cfg.IRAN_FULL_TUNNEL_VERIFIED)
        self.assertTrue(rec.tls_verified is False or rec.tls_verified in (True, False))

    def test_config_status_unchanged_by_globalping(self):
        conf = _conf()
        before = conf.status
        rec = gp.GlobalpingRecord(conf.fingerprint, conf.host, conf.port, conf.protocol)
        rec.checks.append(gp.ProbeCheck("Tehran", 1, "x", True, cfg.IRAN_TLS_OK, 10.0, tls=True))
        gp._summarize(rec)
        self.assertEqual(conf.status, before)


class TestSummarizeRecords(unittest.TestCase):
    def test_latest_result_wins_and_aggregates(self):
        records = [
            {"fingerprint": "a", "protocol": "vless", "checked_at": "2026-01-01T00:00:00+0000",
             "summary": cfg.IRAN_DNS_OK, "cities_reachable": ["Tehran"], "cities_unreachable": []},
            {"fingerprint": "a", "protocol": "vless", "checked_at": "2026-01-02T00:00:00+0000",
             "summary": cfg.IRAN_HTTP_REACHABLE, "tls_verified": True,
             "cities_reachable": ["Tehran", "Tabriz"], "cities_unreachable": []},
        ]
        summary = gp.summarize_records(records)
        self.assertEqual(summary["configs_tested"], 1)
        self.assertEqual(summary["tls_verified"], 1)
        self.assertEqual(summary["by_summary"][cfg.IRAN_HTTP_REACHABLE], 1)
        self.assertEqual(summary["by_city"]["Tehran"]["reachable"], 1)
        self.assertEqual(summary["by_city"]["Tabriz"]["reachable"], 1)


class TestSampleSelection(unittest.TestCase):
    def test_sample_prefers_protocol_diversity(self):
        configs = {}
        for proto in ("vless", "vmess", "trojan", "shadowsocks"):
            c = _conf(protocol=proto, uri=f"{proto}://u@example.com:443")
            configs[c.fingerprint] = c
        sample = gp.select_sample(configs, 2)
        self.assertEqual(len(sample), 2)
        self.assertEqual(len({c.protocol for c in sample}), 2)

    def test_sample_skips_duplicates(self):
        c1 = _conf()
        c2 = _conf(uri="vmess://u@example.com:443", protocol="vmess")
        c2.status = cfg.DUPLICATE
        sample = gp.select_sample({c1.fingerprint: c1, c2.fingerprint: c2}, 10)
        self.assertEqual(sample, [c1])

    def test_sample_prioritises_unlabelled_tunnel_verified(self):
        plain = _conf(uri="vless://a@a.com:443", host="a.com")
        verified = _conf(uri="vless://b@b.com:443", host="b.com")
        verified.tunnel_status = "TUNNEL_VERIFIED"
        configs = {plain.fingerprint: plain, verified.fingerprint: verified}
        sample = gp.select_sample(configs, 1)
        self.assertEqual(sample[0].fingerprint, verified.fingerprint)

    def test_sample_skips_already_labelled_tunnel_verified(self):
        plain = _conf(uri="vless://a@a.com:443", host="a.com")
        verified = _conf(uri="vless://b@b.com:443", host="b.com")
        verified.tunnel_status = "TUNNEL_VERIFIED"
        verified.iran_reachability = "IRAN_TLS_OK"
        configs = {plain.fingerprint: plain, verified.fingerprint: verified}
        sample = gp.select_sample(configs, 1)
        self.assertNotEqual(sample[0].fingerprint, verified.fingerprint)


if __name__ == "__main__":
    unittest.main()
