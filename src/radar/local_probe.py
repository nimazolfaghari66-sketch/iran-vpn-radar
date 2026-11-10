"""Real connection testing using actual VPN protocol clients.

This module performs *real* tunnel tests — it launches a genuine protocol client
(``sing-box`` or ``xray``) that establishes the VPN/proxy tunnel, then measures
DNS resolution, reachability, handshake, tunnel establishment, internet access
through the tunnel, latency, controlled download throughput and short-term
stability.

It deliberately does **not** treat a bare TCP connect as a passing test: a
configuration only passes when traffic actually flows through the tunnel.

If no protocol client binary is installed the result is an explicit failure
("client binary missing"), never a fabricated success. This module is used both
by the standalone Iran probe agent and by ``IRAN_RADAR_PROBE_MODE=local_iran``.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .logging_setup import get_logger
from .models import Config
from .probe_protocol import ProbeInfo, TestOutcome

log = get_logger("radar.local_probe")

# Connectivity target used to prove the tunnel carries real traffic.
DEFAULT_CHECK_URL = "http://cp.cloudflare.com/generate_204"
DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes={bytes}"
DNS_CHECK_HOST = "example.com"


def detect_country(timeout: float = 8.0) -> str:
    """Best-effort 2-letter country code for this host, or "" if unknown.

    Used to keep ``local_iran`` mode honest: a host may only label its tests as
    Iranian when it positively detects that it is in Iran. An environment flag
    alone is never sufficient evidence.
    """
    import urllib.request

    for url in ("https://ipinfo.io/json", "https://ifconfig.co/json"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "IranVPNRadar/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            country = (data.get("country") or data.get("country_iso") or "").upper()
            if country:
                return country[:2]
        except Exception:
            continue
    return ""


def find_client() -> tuple[str, str] | None:
    """Return ``(kind, path)`` for an available client, or ``None``."""
    for kind, names in (("sing-box", ("sing-box",)), ("xray", ("xray",)), ("v2ray", ("v2ray",))):
        for name in names:
            path = shutil.which(name)
            if path:
                return kind, path
        # Allow explicit override via env pointing at a binary.
        override = os.environ.get(f"IRAN_RADAR_{kind.upper().replace('-', '_')}_BIN")
        if override and Path(override).exists():
            return kind, override
    return None


@dataclass
class StageResult:
    dns: bool = False
    reachability: bool = False
    handshake: bool = False
    tunnel: bool = False
    internet: bool = False
    latency: bool = False
    download: bool = False
    stability: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {
            "dns": self.dns,
            "reachability": self.reachability,
            "handshake": self.handshake,
            "tunnel": self.tunnel,
            "internet": self.internet,
            "latency": self.latency,
            "download": self.download,
            "stability": self.stability,
        }

    @property
    def all_critical(self) -> bool:
        # tunnel + internet are the load-bearing stages; others are informative.
        return self.dns and self.reachability and self.tunnel and self.internet


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _resolve(host: str, timeout: float = 5.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.gethostbyname(host)
        return True
    except OSError:
        return False
    finally:
        socket.setdefaulttimeout(None)


def _tcp_reachable(host: str, port: int | None, timeout: float = 5.0) -> bool:
    if not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


# --------------------------------------------------------------- config build
def parse_params(conf: Config) -> dict[str, Any]:
    """Extract the full parameter set needed to build a real client config."""
    from urllib.parse import parse_qs, unquote, urlsplit

    params: dict[str, Any] = {
        "uuid": "",
        "password": "",
        "method": "aes-256-gcm",
        "security": conf.security,
        "sni": conf.sni or "",
        "network": conf.transport or "tcp",
        "path": "/",
        "host": conf.sni or "",
        "flow": "",
        "allow_insecure": False,
        "alpn": [],
        "service_name": "",
        "pbk": "",
        "sid": "",
        "fp": "",
        "early_data": None,
    }

    if conf.protocol == "vmess":
        import base64

        payload = conf.uri.split("://", 1)[1].split("#", 1)[0]
        payload += "=" * ((-len(payload)) % 4)
        try:
            data = json.loads(base64.b64decode(payload).decode("utf-8", "replace"))
        except Exception:
            data = {}
        params["uuid"] = str(data.get("id", ""))
        params["network"] = str(data.get("net") or "tcp")
        params["path"] = str(data.get("path") or "/")
        params["host"] = str(data.get("host") or "")
        params["sni"] = str(data.get("sni") or data.get("host") or "")
        tls = str(data.get("tls") or "").lower()
        params["security"] = "tls" if tls in ("tls", "reality") else "none"
        if str(data.get("tls")) == "tls":
            params["security"] = "tls"
        return params

    split = urlsplit(conf.uri)
    q = parse_qs(split.query)

    def first(*keys, default=""):
        for k in keys:
            v = q.get(k)
            if v and v[0]:
                return v[0]
        return default

    userinfo = ""
    if split.username:
        userinfo = unquote(split.username)
        if split.password:
            userinfo += ":" + unquote(split.password)

    if conf.protocol in ("vless", "tuic"):
        params["uuid"] = userinfo.split(":", 1)[0]
    if conf.protocol in ("trojan", "hysteria2"):
        params["password"] = userinfo
    if conf.protocol == "tuic":
        params["password"] = userinfo.split(":", 1)[1] if ":" in userinfo else ""
    if conf.protocol == "shadowsocks":
        # sip002: ss://base64(method:password)@host:port
        if userinfo and ":" not in userinfo:
            import base64

            head = userinfo + "=" * ((-len(userinfo)) % 4)
            try:
                decoded = base64.b64decode(head).decode("utf-8", "replace")
                if ":" in decoded:
                    params["method"], params["password"] = decoded.split(":", 1)
            except Exception:
                pass
        elif ":" in userinfo:
            params["method"], params["password"] = userinfo.split(":", 1)

    params["network"] = first("type", "net", default=conf.transport or "tcp")
    params["path"] = first("path", default="/")
    params["host"] = first("host", "peer", default="")
    params["sni"] = first("sni", "peer", "host", default=conf.sni or "")
    params["flow"] = first("flow", default="")
    params["service_name"] = first("serviceName", "service_name", default="")
    params["pbk"] = first("pbk", "publicKey", default="")
    params["sid"] = first("sid", "shortId", default="")
    params["fp"] = first("fp", "fingerprint", default="")
    insecure = first("allowInsecure", "insecure", "skip-cert-verify", default="")
    params["allow_insecure"] = str(insecure).lower() in ("1", "true")
    alpn = first("alpn", default="")
    params["alpn"] = [a for a in alpn.split(",") if a]
    if params["network"] in ("ws", "http", "h2") and not params["host"]:
        params["host"] = params["sni"]
    return params


def _tls_block(params: dict[str, Any]) -> dict[str, Any] | None:
    if params["security"] not in ("tls", "reality"):
        return None
    tls: dict[str, Any] = {"enabled": True, "insecure": bool(params["allow_insecure"])}
    if params["sni"]:
        tls["server_name"] = params["sni"]
    if params["alpn"]:
        tls["alpn"] = params["alpn"]
    if params["fp"]:
        tls["utls"] = {"enabled": True, "fingerprint": params["fp"]}
    if params["security"] == "reality":
        tls["reality"] = {
            "enabled": True,
            "public_key": params["pbk"],
            "short_id": params["sid"],
        }
    return tls


def _transport_block(params: dict[str, Any]) -> dict[str, Any] | None:
    network = (params["network"] or "tcp").lower()
    if network == "ws":
        headers = {"Host": params["host"]} if params["host"] else {}
        return {"type": "ws", "path": params["path"] or "/", "headers": headers}
    if network in ("grpc",):
        return {"type": "grpc", "service_name": params["service_name"]}
    if network in ("http", "h2"):
        return {"type": "http", "host": [params["host"]] if params["host"] else []}
    if network == "httpupgrade":
        return {"type": "httpupgrade", "path": params["path"] or "/", "host": params["host"]}
    return None


def _singbox_config(conf: Config, socks_port: int) -> dict[str, Any]:
    params = parse_params(conf)
    proto = conf.protocol
    outbound: dict[str, Any] = {
        "tag": "proxy",
        "server": conf.host,
        "server_port": conf.port,
    }
    if proto == "shadowsocks":
        outbound.update(
            {"type": "shadowsocks", "method": params["method"], "password": params["password"]}
        )
    elif proto == "vless":
        outbound.update({"type": "vless", "uuid": params["uuid"]})
        if params["flow"]:
            outbound["flow"] = params["flow"]
    elif proto == "vmess":
        outbound.update({"type": "vmess", "uuid": params["uuid"], "alter_id": 0})
    elif proto == "trojan":
        outbound.update({"type": "trojan", "password": params["password"]})
    elif proto == "hysteria2":
        outbound.update({"type": "hysteria2", "password": params["password"]})
    elif proto == "tuic":
        outbound.update({"type": "tuic", "uuid": params["uuid"], "password": params["password"]})
    elif proto == "socks":
        outbound.update({"type": "socks", "version": "5"})
        if params["uuid"]:
            outbound["username"] = params["uuid"]
            outbound["password"] = params["password"]
    elif proto == "http":
        outbound.update({"type": "http"})
    else:
        outbound.update({"type": proto})

    tls = _tls_block(params)
    if tls:
        outbound["tls"] = tls
    if proto in ("vless", "vmess", "trojan"):
        transport = _transport_block(params)
        if transport:
            outbound["transport"] = transport

    return {
        "log": {"level": "error"},
        "inbounds": [
            {"type": "socks", "tag": "in", "listen": "127.0.0.1", "listen_port": socks_port}
        ],
        "outbounds": [outbound],
    }


def _xray_config(conf: Config, socks_port: int) -> dict[str, Any]:
    params = parse_params(conf)
    outbound: dict[str, Any] = {"tag": "proxy", "protocol": conf.protocol, "settings": {}}
    stream: dict[str, Any] = {"network": params["network"] or "tcp"}
    if params["security"] in ("tls", "reality"):
        stream["security"] = params["security"]
        tls_settings: dict[str, Any] = {"serverName": params["sni"] or conf.host}
        if params["allow_insecure"]:
            tls_settings["allowInsecure"] = True
        if params["fp"]:
            tls_settings["fingerprint"] = params["fp"]
        if params["alpn"]:
            tls_settings["alpn"] = params["alpn"]
        stream["tlsSettings"] = tls_settings
        if params["security"] == "reality":
            stream["realitySettings"] = {
                "serverName": params["sni"] or conf.host,
                "publicKey": params["pbk"],
                "shortId": params["sid"],
                "fingerprint": params["fp"] or "chrome",
            }
    network = (params["network"] or "tcp").lower()
    if network == "ws":
        stream["wsSettings"] = {"path": params["path"] or "/", "headers": {"Host": params["host"]} if params["host"] else {}}
    elif network == "grpc":
        stream["grpcSettings"] = {"serviceName": params["service_name"]}
    outbound["streamSettings"] = stream

    if conf.protocol == "vless":
        user = {"id": params["uuid"], "encryption": "none"}
        if params["flow"]:
            user["flow"] = params["flow"]
        outbound["settings"] = {"vnext": [{"address": conf.host, "port": conf.port, "users": [user]}]}
    elif conf.protocol == "vmess":
        outbound["settings"] = {
            "vnext": [
                {"address": conf.host, "port": conf.port, "users": [{"id": params["uuid"], "alterId": 0, "security": "auto"}]}
            ]
        }
    elif conf.protocol == "trojan":
        outbound["settings"] = {"servers": [{"address": conf.host, "port": conf.port, "password": params["password"]}]}
    elif conf.protocol == "shadowsocks":
        outbound["settings"] = {
            "servers": [
                {
                    "address": conf.host,
                    "port": conf.port,
                    "method": params["method"],
                    "password": params["password"],
                }
            ]
        }
    elif conf.protocol == "socks":
        outbound["settings"] = {"servers": [{"address": conf.host, "port": conf.port}]}
    elif conf.protocol == "http":
        outbound["settings"] = {"servers": [{"address": conf.host, "port": conf.port}]}
    else:
        outbound["settings"] = {"servers": [{"address": conf.host, "port": conf.port}]}
    return {
        "log": {"loglevel": "error"},
        "inbounds": [
            {"tag": "in", "listen": "127.0.0.1", "port": socks_port, "protocol": "socks", "settings": {"udp": True}}
        ],
        "outbounds": [outbound],
    }


def _write_config(kind: str, conf: Config, socks_port: int, workdir: Path) -> Path:
    path = workdir / "config.json"
    payload = _singbox_config(conf, socks_port) if kind == "sing-box" else _xray_config(conf, socks_port)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _wait_for_port(port: int, timeout: float = 8.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _curl_through_proxy(socks_port: int, url: str, timeout: float = 15.0, max_bytes: int = 0) -> tuple[bool, float, int]:
    """Use curl with a SOCKS5 proxy (curl is universally available)."""
    cmd = [
        "curl",
        "-s",
        "-o",
        "/dev/null" if not max_bytes else "-",
        "--socks5-hostname",
        f"127.0.0.1:{socks_port}",
        "--max-time",
        str(int(timeout)),
        "-w",
        "%{time_total} %{size_download} %{http_code}",
        url,
    ]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    except subprocess.TimeoutExpired:
        return False, timeout, 0
    elapsed = time.time() - start
    if proc.returncode != 0:
        return False, elapsed, 0
    parts = proc.stdout.strip().split()
    if len(parts) < 3:
        return False, elapsed, 0
    try:
        http_code = int(parts[2])
    except ValueError:
        http_code = 0
    size = int(float(parts[1])) if parts[1].replace(".", "", 1).isdigit() else 0
    ok = http_code in (200, 204) or (http_code == 0 and size > 0)
    return ok, elapsed, size


def test_config(conf: Config, probe: ProbeInfo, options: dict[str, Any] | None = None) -> TestOutcome:
    """Run the full staged test for a single configuration."""
    options = options or {}
    stages = StageResult()
    result: dict[str, Any] = {
        "fingerprint": conf.fingerprint,
        "protocol": conf.protocol,
        "success": False,
        "probe_is_iran": probe.is_iran,
        "country": probe.country,
        "stages": {},
    }
    if not probe.is_iran:
        result["error"] = "probe is not located in Iran; refusing to produce an Iranian result"
        return TestOutcome(
            fingerprint=conf.fingerprint,
            success=False,
            probe_is_iran=False,
            error=result["error"],
            stages=stages.to_dict(),
            raw=result,
        )

    # Stage 1: DNS
    stages.dns = _resolve(conf.host)
    # Stage 2: reachability
    stages.reachability = _tcp_reachable(conf.host, conf.port)
    if not stages.reachability:
        result["stages"] = stages.to_dict()
        result["error"] = "server unreachable (tcp)"
        return TestOutcome(conf.fingerprint, False, True, error=result["error"], stages=stages.to_dict(), raw=result)

    client = find_client()
    if client is None:
        result["stages"] = stages.to_dict()
        result["error"] = (
            "no VPN protocol client installed (sing-box/xray/v2ray). "
            "Tunnel tests cannot be performed; configuration not verified."
        )
        return TestOutcome(conf.fingerprint, False, True, error=result["error"], stages=stages.to_dict(), raw=result)

    kind, binary = client
    socks_port = _free_port()
    with tempfile.TemporaryDirectory(prefix="radar-probe-") as tmp:
        workdir = Path(tmp)
        cfg_path = _write_config(kind, conf, socks_port, workdir)
        proc = subprocess.Popen(
            [binary, "run", "-c", str(cfg_path)] if kind in ("sing-box", "xray", "v2ray") else [binary, "-c", str(cfg_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            if not _wait_for_port(socks_port, timeout=10.0):
                err = ""
                if proc.stderr:
                    try:
                        err = proc.stderr.read(400).decode("utf-8", "replace")
                    except Exception:
                        err = ""
                result["stages"] = stages.to_dict()
                result["error"] = f"tunnel client did not start ({kind}): {err.strip()[:200]}"
                return TestOutcome(conf.fingerprint, False, True, error=result["error"], stages=stages.to_dict(), raw=result)

            stages.handshake = True
            # Stage 4/5: tunnel + internet through the tunnel.
            ok, seconds, size = _curl_through_proxy(socks_port, DEFAULT_CHECK_URL, timeout=12)
            stages.tunnel = ok
            stages.internet = ok
            if ok:
                stages.latency = True
                result["latency_ms"] = round(seconds * 1000, 1)
                # Stage 7: controlled download.
                dl_bytes = int(options.get("download_bytes", 1_000_000))
                dl_ok, dl_seconds, dl_size = _curl_through_proxy(
                    socks_port, DOWNLOAD_URL.format(bytes=dl_bytes), timeout=25
                )
                if dl_ok and dl_seconds > 0:
                    stages.download = True
                    result["download_kbps"] = round((dl_size * 8) / dl_seconds / 1000, 1)
                # Stage 8: short stability check.
                stability_seconds = float(options.get("stability_seconds", 8))
                successes = 0
                attempts = 3
                for _ in range(attempts):
                    s_ok, _, _ = _curl_through_proxy(socks_port, DEFAULT_CHECK_URL, timeout=8)
                    successes += 1 if s_ok else 0
                    time.sleep(max(0.0, stability_seconds / attempts - 1))
                stages.stability = successes >= max(1, attempts - 1)
                result["stability_successes"] = successes
                result["stability_attempts"] = attempts
            else:
                result["error"] = "tunnel established but no internet through the tunnel"
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    success = stages.all_critical and stages.tunnel
    result["success"] = success
    result["stages"] = stages.to_dict()
    if success:
        result["grade"] = _grade(stages, result.get("latency_ms"), result.get("download_kbps"))
    elif "error" not in result:
        result["error"] = "tunnel test failed"
    return TestOutcome(
        fingerprint=conf.fingerprint,
        success=success,
        probe_is_iran=True,
        latency_ms=result.get("latency_ms"),
        download_kbps=result.get("download_kbps"),
        grade=result.get("grade"),
        error=result.get("error"),
        stages=stages.to_dict(),
        raw=result,
    )


def _grade(stages: StageResult, latency_ms: float | None, download_kbps: float | None) -> str:
    score = 0
    score += 1 if stages.tunnel else 0
    score += 1 if stages.internet else 0
    score += 1 if stages.download else 0
    score += 1 if stages.stability else 0
    if score >= 4 and latency_ms and latency_ms < 800:
        return "A"
    if score >= 3:
        return "B"
    if score >= 2:
        return "C"
    return "D"


def run_local_tests(configs: list[Config], probe: ProbeInfo, options: dict[str, Any] | None = None) -> list[TestOutcome]:
    """Test a batch of configs sequentially (kept low-volume on purpose)."""
    outcomes: list[TestOutcome] = []
    for conf in configs:
        try:
            outcomes.append(test_config(conf, probe, options))
        except Exception as exc:  # never let one bad config abort the batch
            outcomes.append(
                TestOutcome(
                    fingerprint=conf.fingerprint,
                    success=False,
                    probe_is_iran=probe.is_iran,
                    error=f"internal error: {exc}",
                )
            )
    return outcomes
