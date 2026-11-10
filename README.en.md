<div align="center">

# 📡 Iran VPN Radar

**Free VPN subscriptions, tested from inside Iran — refreshed automatically every 2 hours**

[![Iran-verified](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.working&label=Iran-verified&color=brightgreen)](status/summary.json)
[![Updated](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.generated_at&label=Updated&color=blue)](status/summary.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**🌐 Languages:** [فارسی (primary)](README.md) · **English** · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

</div>

## 📥 Subscription links

Copy a link below and add it to your VPN client. That's it.

| Protocol | Subscription link | Active |
|----------|-------------------|--------|
| **All protocols** | [`subscriptions/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.working&label=%20&color=brightgreen) |
| VLESS | [`subscriptions/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.vless.publishable&label=%20&color=blue) |
| VMess | [`subscriptions/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.vmess.publishable&label=%20&color=blue) |
| Trojan | [`subscriptions/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.trojan.publishable&label=%20&color=blue) |
| Shadowsocks | [`subscriptions/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.shadowsocks.publishable&label=%20&color=blue) |
| Hysteria2 | [`subscriptions/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.hysteria2.publishable&label=%20&color=blue) |
| TUIC | [`subscriptions/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.tuic.publishable&label=%20&color=blue) |
| SOCKS | [`subscriptions/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/socks) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.socks.publishable&label=%20&color=blue) |
| HTTP | [`subscriptions/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/http) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.by_protocol.http.publishable&label=%20&color=blue) |

> A Base64 variant of each file is available with a `.b64` suffix. If your client wants a Base64 link, use that one. Example:
> `https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless.b64`

### How to use

1. Copy the link for the protocol you want from the table above.
2. In your client, choose **Add subscription**.
3. Paste the link and refresh.
4. Pick a server and connect.

## 📊 Status

* **Updates:** automatic, every 2 hours.
* **Active configurations:** shown in the "Active" column above.
* **Latest status:** [status/summary.json](status/summary.json)

> ⚠️ **Note:** only configurations that pass a real test from inside Iran are
> published. Until a configuration passes that test, the files stay empty. We
> never label an untested configuration as working.

## ⭐ Iran-priority candidates

Configurations whose **real tunnel** was established **and** that were reachable from an Iranian network vantage point. These are the best available options until a full tunnel test from inside Iran is performed.

| | |
|---|---|
| **All protocols** | [`subscriptions/iran-priority/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all) |
| VLESS | [`subscriptions/iran-priority/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) |
| VMess | [`subscriptions/iran-priority/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) |
| Trojan | [`subscriptions/iran-priority/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) |
| Shadowsocks | [`subscriptions/iran-priority/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) |
| Hysteria2 | [`subscriptions/iran-priority/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) |
| TUIC | [`subscriptions/iran-priority/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) |
| SOCKS | [`subscriptions/iran-priority/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) |
| HTTP | [`subscriptions/iran-priority/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) |

> These are **not verified from inside Iran** (the tunnel was established from our engine host), but they carry Iranian network reachability evidence and rank highest among candidates.

## 🧪 Candidate pool (not Iran-verified)

A second, clearly separated pool holds configurations whose tunnel was actually
established by a real client (sing-box) — but from our engine host, which is
**not** inside Iran. They are ranked so that entries an Iranian probe already
saw reachable come first.

* All candidates: [`subscriptions/candidates/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/all)
* Per protocol: `subscriptions/candidates/vless`, `.../vmess`, `.../trojan`,
  `.../shadowsocks`, `.../hysteria2`, `.../tuic`, `.../socks`, `.../http`

> These are **not** Iran-verified. They may be blocked inside Iran. Use them only
> as a fallback or starting point. The files above (without `/candidates/`) are
> the Iran-verified ones.

## 📱 Supported clients

| Client | Platform | Recommended format |
|--------|----------|--------------------|
| v2rayNG | Android | Base64 link (`.b64`) |
| v2rayN | Windows | Base64 link |
| sing-box | Cross-platform | Plain text |
| Hiddify / NekoBox | Cross-platform | Base64 link |
| Clash / Clash.Meta | Cross-platform | Protocol files |

## ❓ FAQ

**How often are the subscriptions updated?**
Every 2 hours, automatically.

**Why are the files empty?**
Because no configuration has passed the "verified from inside Iran" test yet.
This is deliberate, to avoid publishing broken configurations.

**How do I report a broken configuration?**
Open an [Issue](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues).
Please **never** post passwords, personal links or private information.

**Are these configurations safe?**
Configurations are **public** and may be unstable or owned by someone else.
Use them at your own risk. See [SECURITY.md](SECURITY.md).
