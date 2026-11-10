"""Parse protocol URIs into :class:`~radar.models.Config` and back.

Supports VLESS, VMess, Trojan, Shadowsocks, Hysteria2, TUIC, SOCKS and
HTTP/HTTPS proxies. Parsing never performs network access and never mutates the
original link: the canonical URI that clients consume is preserved verbatim
(minus any purely cosmetic whitespace) so that publishing round-trips cleanly.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

from . import config as cfg
from .models import Config

_URI_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*)://(.+)$", re.S)
_SS_LIKE = {"shadowsocks", "ss"}


def _b64decode(data: str) -> bytes | None:
    """Decode base64 tolerating URL-safe alphabets and missing padding."""
    if not data:
        return None
    cleaned = data.strip().replace("\n", "").replace("\r", "")
    cleaned = cleaned.replace("-", "+").replace("_", "/")
    padding = (-len(cleaned)) % 4
    cleaned += "=" * padding
    try:
        return base64.b64decode(cleaned, validate=False)
    except (binascii.Error, ValueError):
        return None


def _first(params: dict[str, list[str]], *keys: str) -> str | None:
    for key in keys:
        values = params.get(key)
        if values and values[0] != "":
            return values[0]
    return None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _classify_transport(params: dict[str, list[str]], net: str | None) -> str:
    net = (net or _first(params, "type", "net", "network") or "tcp").lower()
    return net or "tcp"


def _classify_security(params: dict[str, list[str]], security: str | None) -> str:
    sec = (security or _first(params, "security", "tls") or "").lower()
    if sec in {"tls", "reality", "xtls"}:
        return sec
    if _first(params, "tls") in {"1", "true"}:
        return "tls"
    return "none"


def _host_from_uri(uri: str) -> tuple[str, int | None]:
    """Best-effort host/port extraction that also handles bracketed IPv6."""
    try:
        split = urlsplit(uri)
        host = split.hostname or ""
        port = split.port
        if host:
            return host, port
    except ValueError:
        pass
    # Fallback manual parse for malformed-but-common links.
    m = re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://[^@/]*@?\[?([^\]/:?#]+)\]?:?(\d+)?", uri)
    if m:
        return m.group(1), _to_int(m.group(2))
    return "", None


# --------------------------------------------------------------------- vless
def _parse_vless(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    params = parse_qs(split.query)
    security = _classify_security(params, split.query and None)
    return Config(
        uri=uri,
        protocol="vless",
        host=split.hostname,
        port=split.port,
        transport=_classify_transport(params, None),
        security=security,
        sni=_first(params, "sni", "peer", "host"),
        tag=unquote(split.fragment) or None,
    )


# --------------------------------------------------------------------- vmess
def _parse_vmess(uri: str) -> Config | None:
    payload = uri.split("://", 1)[1]
    if "#" in payload:
        payload = payload.split("#", 1)[0]
    raw = _b64decode(payload)
    if not raw:
        return None
    try:
        data: dict[str, Any] = json.loads(raw.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return None
    host = str(data.get("add") or "")
    if not host:
        return None
    tls = str(data.get("tls") or "").lower()
    security = "tls" if tls in {"tls", "reality"} else "none"
    return Config(
        uri=uri,
        protocol="vmess",
        host=host,
        port=_to_int(data.get("port")),
        transport=str(data.get("net") or "tcp").lower(),
        security=security,
        sni=(str(data.get("sni") or data.get("host") or "") or None),
        tag=str(data.get("ps") or "") or None,
    )


# -------------------------------------------------------------------- trojan
def _parse_trojan(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    params = parse_qs(split.query)
    return Config(
        uri=uri,
        protocol="trojan",
        host=split.hostname,
        port=split.port,
        transport=_classify_transport(params, None),
        security=_classify_security(params, "tls"),
        sni=_first(params, "sni", "peer", "host"),
        tag=unquote(split.fragment) or None,
    )


# --------------------------------------------------------------- shadowsocks
def _parse_shadowsocks(uri: str) -> Config | None:
    split = urlsplit(uri)
    params = parse_qs(split.query)
    host = split.hostname
    port = split.port
    if host is None:
        # sip002 style: ss://base64(method:password)@host:port
        payload = uri.split("://", 1)[1]
        payload = payload.split("#", 1)[0].split("?", 1)[0]
        if "@" in payload:
            head, tail = payload.rsplit("@", 1)
            decoded = _b64decode(head)
            if decoded and b":" in decoded:
                host, port = _host_from_uri("ss://" + tail)
        else:
            decoded = _b64decode(payload)
            if decoded:
                text = decoded.decode("utf-8", "replace")
                if "@" in text:
                    _, tail = text.rsplit("@", 1)
                    host, port = _host_from_uri("ss://" + tail)
    if not host:
        return None
    return Config(
        uri=uri,
        protocol="shadowsocks",
        host=host,
        port=port,
        transport="tcp",
        security="none",
        sni=_first(params, "sni", "peer"),
        tag=unquote(split.fragment) or None,
    )


# --------------------------------------------------------------- hysteria2
def _parse_hysteria2(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    params = parse_qs(split.query)
    return Config(
        uri=uri,
        protocol="hysteria2",
        host=split.hostname,
        port=split.port,
        transport="udp",
        security="tls",
        sni=_first(params, "sni", "peer"),
        tag=unquote(split.fragment) or None,
    )


# -------------------------------------------------------------------- tuic
def _parse_tuic(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    params = parse_qs(split.query)
    return Config(
        uri=uri,
        protocol="tuic",
        host=split.hostname,
        port=split.port,
        transport="udp",
        security="tls",
        sni=_first(params, "sni", "peer"),
        tag=unquote(split.fragment) or None,
    )


# ------------------------------------------------------------ socks / http
def _parse_socks(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    return Config(
        uri=uri,
        protocol="socks",
        host=split.hostname,
        port=split.port,
        transport="tcp",
        security="none",
        tag=unquote(split.fragment) or None,
    )


def _parse_http(uri: str) -> Config | None:
    split = urlsplit(uri)
    if not split.hostname:
        return None
    return Config(
        uri=uri,
        protocol="http",
        host=split.hostname,
        port=split.port,
        transport="tcp",
        security="tls" if split.scheme == "https" else "none",
        tag=unquote(split.fragment) or None,
    )


_PARSERS = {
    "vless": _parse_vless,
    "vmess": _parse_vmess,
    "trojan": _parse_trojan,
    "ss": _parse_shadowsocks,
    "shadowsocks": _parse_shadowsocks,
    "hysteria2": _parse_hysteria2,
    "hy2": _parse_hysteria2,
    "hysteria": _parse_hysteria2,
    "tuic": _parse_tuic,
    "socks": _parse_socks,
    "socks5": _parse_socks,
    "socks5h": _parse_socks,
    "http": _parse_http,
    "https": _parse_http,
}


def is_supported_scheme(scheme: str) -> bool:
    return scheme.lower() in _PARSERS


def parse_uri(uri: str, source_id: str = "", source_url: str = "") -> Config | None:
    """Parse one URI. Returns ``None`` when the link is unsupported or invalid."""
    if not uri:
        return None
    uri = uri.strip()
    match = _URI_RE.match(uri)
    if not match:
        return None
    scheme = match.group(1).lower()
    parser = _PARSERS.get(scheme)
    if parser is None:
        return None
    try:
        conf = parser(uri)
    except Exception:  # defensive: a single malformed link must never abort a run
        return None
    if conf is None or not conf.host:
        return None
    conf.source_id = source_id
    conf.source_url = source_url
    conf.fingerprint = conf.compute_fingerprint()
    return conf


def protocol_of(uri: str) -> str | None:
    match = _URI_RE.match(uri.strip()) if uri else None
    if not match:
        return None
    return cfg.SCHEME_TO_PROTOCOL.get(match.group(1).lower())
