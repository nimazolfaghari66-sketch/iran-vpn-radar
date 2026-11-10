"""Extraction from base64 / JSON / YAML / Clash / sing-box payloads."""

import base64
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar.extract import extract_configs, extract_text  # noqa: E402

VLESS = "vless://uuid@example.com:443?security=tls&type=ws#a"
VMESS_JSON = {"v": "2", "add": "1.2.3.4", "port": "80", "id": "x", "net": "tcp"}
VMESS = "vmess://" + base64.b64encode(json.dumps(VMESS_JSON).encode()).decode()
TROJAN = "trojan://pw@trojan.example.com:443#t"


class TestExtract(unittest.TestCase):
    def test_plain_text(self):
        payload = f"{VLESS}\n{VMESS}\n{TROJAN}\n"
        configs, stats = extract_configs(payload)
        self.assertEqual(len(configs), 3)
        self.assertEqual({c.protocol for c in configs}, {"vless", "vmess", "trojan"})

    def test_base64_body(self):
        body = base64.b64encode(f"{VLESS}\n{TROJAN}".encode()).decode()
        configs, _ = extract_configs(body)
        self.assertEqual(len(configs), 2)

    def test_json_list(self):
        payload = json.dumps({"configs": [VLESS, TROJAN]})
        configs, _ = extract_configs(payload)
        self.assertEqual(len(configs), 2)

    def test_clash_yaml(self):
        payload = """
proxies:
  - name: n1
    type: vless
    server: 1.2.3.4
    port: 443
    uuid: abc
    tls: true
    servername: cdn.x.com
  - name: n2
    type: trojan
    server: 5.6.7.8
    port: 8443
    password: pw
    sni: t.example.com
"""
        configs, _ = extract_configs(payload)
        self.assertEqual(len(configs), 2)
        self.assertEqual({c.protocol for c in configs}, {"vless", "trojan"})

    def test_singbox_json(self):
        payload = json.dumps(
            {
                "outbounds": [
                    {"type": "vless", "tag": "a", "server": "9.9.9.9", "server_port": 443, "uuid": "u", "tls": {"server_name": "x"}},
                    {"type": "shadowsocks", "tag": "b", "server": "8.8.8.8", "server_port": 8388, "method": "aes-256-gcm", "password": "p"},
                ]
            }
        )
        configs, _ = extract_configs(payload)
        self.assertEqual(len(configs), 2)

    def test_dedupe_within_payload(self):
        payload = f"{VLESS}\n{VLESS}\n{VLESS}\n"
        configs, _ = extract_configs(payload)
        self.assertEqual(len(configs), 1)

    def test_noise_ignored(self):
        # `ftp://` and `garbage://` are unsupported schemes and must be dropped.
        payload = "hello world\nftp://example.com/x\ngarbage://x\n" + VLESS
        configs, _ = extract_configs(payload)
        self.assertEqual(len(configs), 1)

    def test_extract_text_limit(self):
        payload = "\n".join([VLESS] * 100)
        tokens = extract_text(payload, limit=10)
        self.assertLessEqual(len(tokens), 10)


if __name__ == "__main__":
    unittest.main()
