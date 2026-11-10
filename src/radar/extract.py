"""Extract configuration URIs from arbitrary public payload shapes.

Supported inputs:

* individual configuration links (one URI per line)
* base64 encoded subscription bodies (whole-payload or line-level)
* plain-text configuration lists
* supported JSON formats (flat lists, ``{"configs": [...]}``, v2ray-style)
* supported YAML formats
* Clash / Clash.Meta style proxy maps
* sing-box style ``outbounds`` documents

The extractor is intentionally lenient: it never raises on hostile input, it
just yields whatever valid links it can find.
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from typing import Any, Iterable

from .normalize import parse_uri, protocol_of

try:  # PyYAML is optional at runtime; JSON-only payloads still work without it.
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

# A permissive matcher for anything that looks like a supported URI.
_URI_TOKEN_RE = re.compile(
    r"(?:vless|vmess|trojan|ss|shadowsocks|hysteria2|hy2|hysteria|tuic|socks5h|socks5|socks|https?)"
    r"://[^\s\"'<>\\]+",
    re.I,
)

_SS_PLACEHOLDER = "ss://"
_PLAIN_TEXT_KEYS = ("configs", "links", "servers", "subscriptions", "proxies", "outbounds")


def _b64decode_any(data: str) -> str | None:
    cleaned = data.strip().replace("\n", "").replace("\r", "")
    if len(cleaned) < 8:
        return None
    cleaned = cleaned.replace("-", "+").replace("_", "/")
    cleaned += "=" * ((-len(cleaned)) % 4)
    try:
        raw = base64.b64decode(cleaned, validate=False)
    except (binascii.Error, ValueError):
        return None
    if not raw:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    # Only accept the decode when it actually looks like configuration data.
    if _URI_TOKEN_RE.search(text) or "://" in text:
        return text
    return None


def looks_like_uri(token: str) -> bool:
    return protocol_of(token) is not None


def _iter_tokens(text: str) -> Iterable[str]:
    for match in _URI_TOKEN_RE.finditer(text):
        yield match.group(0).rstrip(".,;)")


def _walk_json(node: Any, out: list[str], depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(node, str):
        if node.startswith("http://") or node.startswith("https://"):
            return
        out.extend(_iter_tokens(node))
    elif isinstance(node, list):
        for item in node:
            _walk_json(item, out, depth + 1)
    elif isinstance(node, dict):
        # Clash-style proxy object.
        if "server" in node and ("type" in node or "protocol" in node):
            uri = _clash_proxy_to_uri(node)
            if uri:
                out.append(uri)
        for key, value in node.items():
            if key in _PLAIN_TEXT_KEYS and isinstance(value, (list, dict, str)):
                _walk_json(value, out, depth + 1)
            else:
                _walk_json(value, out, depth + 1)


def _clash_proxy_to_uri(node: dict[str, Any]) -> str | None:
    """Convert a Clash proxy map into a canonical share link where possible."""
    ptype = str(node.get("type") or "").lower()
    server = str(node.get("server") or "")
    port = node.get("port")
    if not server or port is None:
        return None
    name = str(node.get("name") or "")
    if ptype == "vless":
        query = []
        for key in ("servername", "flow", "network", "tls", "skip-cert-verify"):
            if key in node and node[key] not in (None, ""):
                mapped = {"servername": "sni", "skip-cert-verify": "allowInsecure"}.get(key, key)
                query.append(f"{mapped}={node[key]}")
        if str(node.get("tls")) in {"true", "True"} and not any(q.startswith("security=") for q in query):
            query.append("security=tls")
        qs = ("?" + "&".join(query)) if query else ""
        frag = f"#{name}" if name else ""
        return f"vless://{node.get('uuid','')}@{server}:{port}{qs}{frag}"
    if ptype == "trojan":
        query = []
        if node.get("sni"):
            query.append(f"sni={node['sni']}")
        qs = ("?" + "&".join(query)) if query else ""
        frag = f"#{name}" if name else ""
        return f"trojan://{node.get('password','')}@{server}:{port}{qs}{frag}"
    if ptype in {"ss", "shadowsocks"}:
        method = node.get("cipher") or node.get("method") or ""
        password = node.get("password") or ""
        cred = base64.b64encode(f"{method}:{password}".encode()).decode()
        frag = f"#{name}" if name else ""
        return f"ss://{cred}@{server}:{port}{frag}"
    if ptype in {"hysteria2", "hysteria"}:
        frag = f"#{name}" if name else ""
        return f"hysteria2://{node.get('password','')}@{server}:{port}{frag}"
    if ptype == "tuic":
        frag = f"#{name}" if name else ""
        return f"tuic://{node.get('uuid','')}:{node.get('password','')}@{server}:{port}{frag}"
    if ptype in {"socks5", "socks"}:
        frag = f"#{name}" if name else ""
        return f"socks://{node.get('username','')}:{node.get('password','')}@{server}:{port}{frag}"
    if ptype in {"http", "https"}:
        frag = f"#{name}" if name else ""
        return f"http://{node.get('username','')}:{node.get('password','')}@{server}:{port}{frag}"
    return None


def _singbox_outbound_to_uri(node: dict[str, Any]) -> str | None:
    otype = str(node.get("type") or "").lower()
    server = str(node.get("server") or "")
    port = node.get("server_port") or node.get("port")
    if not server or port is None:
        return None
    tag = str(node.get("tag") or "")
    frag = f"#{tag}" if tag else ""
    tls = node.get("tls") or {}
    sni = tls.get("server_name") if isinstance(tls, dict) else None
    if otype == "vless":
        q = f"?sni={sni}" if sni else ""
        return f"vless://{node.get('uuid','')}@{server}:{port}{q}{frag}"
    if otype == "vmess":
        payload = {
            "v": "2",
            "ps": tag,
            "add": server,
            "port": str(port),
            "id": node.get("uuid", ""),
            "aid": str(node.get("alter_id", 0)),
            "net": "tcp",
            "type": "none",
            "host": sni or "",
            "tls": "tls" if tls else "",
        }
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        return f"vmess://{encoded}"
    if otype == "trojan":
        q = f"?sni={sni}" if sni else ""
        return f"trojan://{node.get('password','')}@{server}:{port}{q}{frag}"
    if otype == "shadowsocks":
        method = node.get("method") or ""
        password = node.get("password") or ""
        cred = base64.b64encode(f"{method}:{password}".encode()).decode()
        return f"ss://{cred}@{server}:{port}{frag}"
    if otype == "hysteria2":
        return f"hysteria2://{node.get('password','')}@{server}:{port}{frag}"
    if otype == "tuic":
        return f"tuic://{node.get('uuid','')}:{node.get('password','')}@{server}:{port}{frag}"
    return None


def _extract_from_clash_doc(doc: Any, out: list[str]) -> bool:
    if not isinstance(doc, dict):
        return False
    proxies = doc.get("proxies")
    if isinstance(proxies, list):
        found = False
        for proxy in proxies:
            if isinstance(proxy, dict):
                uri = _clash_proxy_to_uri(proxy)
                if uri:
                    out.append(uri)
                    found = True
        if found:
            return True
    return False


def _extract_from_singbox_doc(doc: Any, out: list[str]) -> bool:
    if not isinstance(doc, dict):
        return False
    outbounds = doc.get("outbounds")
    if isinstance(outbounds, list):
        found = False
        for ob in outbounds:
            if isinstance(ob, dict):
                uri = _singbox_outbound_to_uri(ob)
                if uri:
                    out.append(uri)
                    found = True
        if found:
            return True
    return False


def extract_text(text: str, limit: int = 20000) -> list[str]:
    """Return raw URI tokens found in *text* (no parsing, just extraction)."""
    found: list[str] = []
    seen: set[str] = set()

    def add_all(tokens: Iterable[str]) -> None:
        for token in tokens:
            token = token.strip()
            if token and token not in seen:
                seen.add(token)
                found.append(token)

    # 1. Direct URI tokens.
    add_all(_iter_tokens(text))

    # 2. JSON payloads.
    stripped = text.strip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            doc = json.loads(stripped)
            json_out: list[str] = []
            if not (_extract_from_clash_doc(doc, json_out) or _extract_from_singbox_doc(doc, json_out)):
                _walk_json(doc, json_out)
            add_all(json_out)
        except json.JSONDecodeError:
            pass

    # 3. YAML payloads (Clash / sing-box).
    if yaml is not None and ("proxies:" in text or "outbounds:" in text or text.lstrip().startswith("---")):
        try:
            doc = yaml.safe_load(text)
            yaml_out: list[str] = []
            if not (_extract_from_clash_doc(doc, yaml_out) or _extract_from_singbox_doc(doc, yaml_out)):
                _walk_json(doc, yaml_out)
            add_all(yaml_out)
        except Exception:
            pass

    # 4. Base64 body (whole payload or per line).
    if not found or len(found) < 3:
        decoded = _b64decode_any(text)
        if decoded:
            add_all(_iter_tokens(decoded))
    for line in text.splitlines():
        line = line.strip()
        if line and "://" not in line and len(line) > 24:
            decoded = _b64decode_any(line)
            if decoded:
                add_all(_iter_tokens(decoded))

    return found[:limit]


def extract_configs(payload: str, source_id: str = "", source_url: str = "", limit: int = 20000):
    """Extract and parse configurations from a raw payload.

    Returns ``(configs, stats)`` where ``stats`` counts raw tokens and drops.
    """
    tokens = extract_text(payload, limit=limit * 3)
    configs = []
    stats = {"tokens": len(tokens), "parsed": 0, "unsupported": 0, "invalid": 0}
    seen_fp: set[str] = set()
    for token in tokens:
        if len(configs) >= limit:
            break
        if protocol_of(token) is None:
            stats["unsupported"] += 1
            continue
        conf = parse_uri(token, source_id=source_id, source_url=source_url)
        if conf is None:
            stats["invalid"] += 1
            continue
        if conf.fingerprint in seen_fp:
            continue
        seen_fp.add(conf.fingerprint)
        configs.append(conf)
    stats["parsed"] = len(configs)
    return configs, stats
