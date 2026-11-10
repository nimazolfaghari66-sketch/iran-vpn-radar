<div align="center">

# 📡 伊朗 VPN 雷达

**免费 VPN 订阅，从伊朗境内实测 — 每 2 小时自动更新**

</div>

**语言：** [فارسی（主要）](README.md) · [English](README.en.md) · [العربية](README.ar.md) · **中文** · [Русский](README.ru.md) · [Español](README.es.md)

> ⚠️ **翻译文件。** 项目的主要语言是波斯语（[README.md](README.md)）。

<!-- radar:subscriptions:start -->
## 📥 订阅链接

复制下面的链接，添加到你的 VPN 客户端即可。

**所有协议（all）:** [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/all)

| 协议 | 订阅链接 | 有效配置数 |
|---|---|---|
| **VLESS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vless) | 83 |
| **VMess** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/vmess) | 1 |
| **Trojan** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/trojan) | 72 |
| **Shadowsocks** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/shadowsocks) | 20 |
| **Hysteria2** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/hysteria2) | 0 |
| **TUIC** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/tuic) | 0 |
| **SOCKS** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/socks) | 3 |
| **HTTP** | [https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/iran-priority/http) | 2 |

> 每个文件的 Base64 版本带有 `.b64` 后缀。

> 这些链接属于「伊朗优先」层级：已建立真实隧道并有伊朗网络可达性证据，但未在伊朗境内验证。
<!-- radar:subscriptions:end -->

### 使用方法

1. 从上表复制你需要的协议链接。
2. 在客户端中选择 **添加订阅（Add subscription）**。
3. 粘贴链接并刷新。
4. 选择服务器并连接。

## 📊 状态

* **更新：** 自动，每 2 小时一次。
* **最新状态：** [status/summary.json](status/summary.json)

> ⚠️ **注意：** 只有通过伊朗境内真实测试的配置才会发布。在配置通过该测试之前，文件保持为空。我们绝不把未测试的配置标为「可用」。

## 📈 各协议状态

计数每 2 小时刷新一次。**健康** 表示已建立真实隧道。每个协议的目标是 **100** 个健康配置，分别统计，绝不合并计数。

| 协议 | 已发现 | 已测试 | 成功隧道 | 健康 | 目标 | 缺口 | 伊朗优先 | 订阅 |
|---|---|---|---|---|---|---|---|---|
| **vless** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vless&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vless&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vless&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vless&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vless&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vless&color=yellowgreen) | [`subscriptions/candidates/vless`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vless) |
| **vmess** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.vmess&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.vmess&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.vmess&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.vmess&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.vmess&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.vmess&color=yellowgreen) | [`subscriptions/candidates/vmess`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/vmess) |
| **trojan** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.trojan&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.trojan&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.trojan&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.trojan&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.trojan&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.trojan&color=yellowgreen) | [`subscriptions/candidates/trojan`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/trojan) |
| **shadowsocks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.shadowsocks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.shadowsocks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.shadowsocks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.shadowsocks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.shadowsocks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.shadowsocks&color=yellowgreen) | [`subscriptions/candidates/shadowsocks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/shadowsocks) |
| **hysteria2** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.hysteria2&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.hysteria2&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.hysteria2&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.hysteria2&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.hysteria2&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.hysteria2&color=yellowgreen) | [`subscriptions/candidates/hysteria2`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/hysteria2) |
| **tuic** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.tuic&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.tuic&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.tuic&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.tuic&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.tuic&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.tuic&color=yellowgreen) | [`subscriptions/candidates/tuic`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/tuic) |
| **socks** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.socks&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.socks&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.socks&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.socks&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.socks&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.socks&color=yellowgreen) | [`subscriptions/candidates/socks`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/socks) |
| **http** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.discovered_by_protocol.http&color=blue) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.tested_by_protocol.http&color=blueviolet) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.successful_by_protocol.http&color=brightgreen) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.healthy.http&color=success) | **100** | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.shortage_by_protocol.http&color=orange) | ![](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnimazolfaghari66-sketch%2Firan-vpn-radar%2Fmain%2Fstatus%2Fsummary.json&query=%24.candidates.priority_by_protocol_map.http&color=yellowgreen) | [`subscriptions/candidates/http`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/http) |

## 🧪 候选池（非伊朗验证）

另有一个明确分开的候选池，其中的配置隧道由真实客户端（sing-box）实际建立——
但来自我们的引擎主机，该主机**不在伊朗境内**。这些配置按顺序排列，
伊朗探测点已观测到可访问的条目排在最前。

* 全部候选： [`subscriptions/candidates/all`](https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/candidates/all)
* 按协议： `subscriptions/candidates/vless`、`.../vmess`、`.../trojan`、
  `.../shadowsocks`、`.../hysteria2`、`.../tuic`、`.../socks`、`.../http`

> 这些**并非**伊朗验证。它们在伊朗境内可能被封锁。仅作为备用或起点使用。
> 上面的文件（不带 `/candidates/`）才是伊朗验证文件。

## 📱 支持的客户端

v2rayNG · v2rayN · sing-box · Hiddify / NekoBox · Clash / Clash.Meta

## ❓ 常见问题

**订阅多久更新一次？** 每 2 小时自动更新。

**为什么文件是空的？** 因为还没有配置通过「伊朗境内验证」测试。这是刻意的，以避免发布失效配置。

**如何报告失效配置？** 通过 [Issues](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues)。请**绝不**发布密码、个人链接或隐私信息。

**这些配置安全吗？** 配置是**公开的**，可能不稳定或属于他人。请自行承担风险。参见 [SECURITY.md](SECURITY.md)。
