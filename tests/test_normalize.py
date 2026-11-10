"""Protocol parsing and classification tests."""

import base64
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar.normalize import parse_uri, protocol_of  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_vless(self):
        uri = "vless://11111111-2222-3333-4444-555555555555@example.com:443?security=tls&type=ws&sni=cdn.example.com#tag"
        conf = parse_uri(uri)
        self.assertIsNotNone(conf)
        self.assertEqual(conf.protocol, "vless")
        self.assertEqual(conf.host, "example.com")
        self.assertEqual(conf.port, 443)
        self.assertEqual(conf.transport, "ws")
        self.assertEqual(conf.security, "tls")
        self.assertEqual(conf.sni, "cdn.example.com")

    def test_vmess(self):
        payload = {"v": "2", "ps": "t", "add": "1.2.3.4", "port": "8080", "id": "abc", "net": "ws", "tls": "tls"}
        uri = "vmess://" + base64.b64encode(json.dumps(payload).encode()).decode()
        conf = parse_uri(uri)
        self.assertEqual(conf.protocol, "vmess")
        self.assertEqual(conf.host, "1.2.3.4")
        self.assertEqual(conf.port, 8080)
        self.assertEqual(conf.security, "tls")

    def test_trojan(self):
        conf = parse_uri("trojan://pass@example.org:443?sni=x.example.org#n")
        self.assertEqual(conf.protocol, "trojan")
        self.assertEqual(conf.port, 443)
        self.assertEqual(conf.security, "tls")

    def test_shadowsocks_sip002(self):
        cred = base64.b64encode(b"aes-256-gcm:secretpass").decode()
        conf = parse_uri(f"ss://{cred}@example.net:8388#ss1")
        self.assertEqual(conf.protocol, "shadowsocks")
        self.assertEqual(conf.host, "example.net")
        self.assertEqual(conf.port, 8388)

    def test_hysteria2_and_tuic(self):
        h = parse_uri("hysteria2://pw@h.example.com:443?sni=h.example.com#h")
        self.assertEqual(h.protocol, "hysteria2")
        self.assertEqual(h.transport, "udp")
        t = parse_uri("tuic://uuid:pw@t.example.com:443#t")
        self.assertEqual(t.protocol, "tuic")

    def test_socks_http(self):
        self.assertEqual(parse_uri("socks5://1.2.3.4:1080").protocol, "socks")
        self.assertEqual(parse_uri("http://1.2.3.4:8080").protocol, "http")
        self.assertEqual(parse_uri("https://1.2.3.4:8443").security, "tls")

    def test_ipv6(self):
        conf = parse_uri("vless://uuid@[2001:db8::1]:443?security=tls#v6")
        self.assertEqual(conf.host, "2001:db8::1")
        self.assertEqual(conf.host_kind, "ipv6")

    def test_invalid(self):
        self.assertIsNone(parse_uri("not-a-uri"))
        self.assertIsNone(parse_uri("ftp://example.com/x"))
        self.assertIsNone(parse_uri(""))

    def test_protocol_of(self):
        self.assertEqual(protocol_of("ss://x@h:1"), "shadowsocks")
        self.assertIsNone(protocol_of("garbage"))

    def test_fingerprint_stable_and_distinct(self):
        a = parse_uri("vless://uuid1@example.com:443?security=tls#one")
        b = parse_uri("vless://uuid1@example.com:443?security=tls#two")  # differs only by tag
        c = parse_uri("vless://uuid2@example.com:443?security=tls#one")
        self.assertEqual(a.fingerprint, b.fingerprint)
        self.assertNotEqual(a.fingerprint, c.fingerprint)


if __name__ == "__main__":
    unittest.main()
