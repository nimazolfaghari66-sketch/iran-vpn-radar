<div align="center">

# 📡 Iran VPN Radar

**Free VPN subscriptions, tested from inside Iran — refreshed automatically every 2 hours**

[![Iran-verified](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.configs.working&label=Iran-verified&color=brightgreen)](status/summary.json)
[![Updated](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.generated_at&label=Updated&color=blue)](status/summary.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**🌐 Languages:** [فارسی (primary)](README.md) · **English** · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

</div>

<!-- radar:subscriptions:start -->
## 📥 Subscription links

Copy a link below and add it to your VPN client. That's it.

**All protocols (all):** [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all)

| Protocol | Subscription link | Active configs |
|---|---|---|
| **VLESS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) | 105 |
| **VMess** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) | 13 |
| **Trojan** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) | 72 |
| **Shadowsocks** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) | 69 |
| **Hysteria2** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) | 0 |
| **TUIC** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) | 0 |
| **SOCKS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) | 6 |
| **HTTP** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) | 3 |

> A Base64 variant of each file is available with a `.b64` suffix. Use it if your client expects a Base64 subscription.

> These links are the Iran-priority tier: a real tunnel was established and there is Iranian network reachability evidence, but they are not verified from inside Iran.
<!-- radar:subscriptions:end -->

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

## 📈 Per-protocol status

Counts refresh every 2 hours. **Healthy** means a real tunnel was established. The target is **100** healthy configurations per protocol, tracked separately — protocol counts are never summed.

| Protocol | Discovered | Tested | Successful | Healthy | Target | Shortage | Iran-priority | Subscription |
|---|---|---|---|---|---|---|---|---|
| **vless** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vless&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vless&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vless&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vless&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vless&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vless&color=yellowgreen) | [`subscriptions/candidates/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vless) |
| **vmess** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vmess&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vmess&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vmess&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vmess&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vmess&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vmess&color=yellowgreen) | [`subscriptions/candidates/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vmess) |
| **trojan** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.trojan&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.trojan&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.trojan&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.trojan&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.trojan&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.trojan&color=yellowgreen) | [`subscriptions/candidates/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/trojan) |
| **shadowsocks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.shadowsocks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.shadowsocks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.shadowsocks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.shadowsocks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.shadowsocks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.shadowsocks&color=yellowgreen) | [`subscriptions/candidates/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/shadowsocks) |
| **hysteria2** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.hysteria2&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.hysteria2&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.hysteria2&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.hysteria2&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.hysteria2&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.hysteria2&color=yellowgreen) | [`subscriptions/candidates/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/hysteria2) |
| **tuic** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.tuic&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.tuic&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.tuic&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.tuic&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.tuic&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.tuic&color=yellowgreen) | [`subscriptions/candidates/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/tuic) |
| **socks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.socks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.socks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.socks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.socks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.socks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.socks&color=yellowgreen) | [`subscriptions/candidates/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/socks) |
| **http** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.http&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.http&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.http&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.http&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.http&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.http&color=yellowgreen) | [`subscriptions/candidates/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/http) |

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
