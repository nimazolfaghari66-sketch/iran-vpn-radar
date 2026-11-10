<div align="center">

# 📡 Iran VPN Radar

**Automatic discovery, testing and publication of free VPN subscriptions for users in Iran**

[![CI](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

**Languages:** [فارسی (primary)](README.md) · **English** · [العربية](README.ar.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Español](README.es.md)

---

## ⚠️ Important: Iranian testing status

This project has one non-negotiable rule: **a configuration is never published
as "Iran-verified" unless it was genuinely tested by a probe physically located
inside Iran.**

The Iran probe is a separate service that must run on a host inside Iran. Until
one is connected:

* every configuration stays in the `PENDING_IRAN_TEST` state;
* the published subscription files are intentionally **empty**;
* no foreign-location or synthetic result is ever presented as an Iranian test.

See [Iranian testing architecture](#-iranian-testing-architecture).

---

## What is Iran VPN Radar?

Iran VPN Radar is an automated, open-source system that:

1. **Discovers** public sources that publish free VPN configurations — automatically.
2. **Extracts**, normalises and **de-duplicates** configurations.
3. **Tests** them **from inside Iran** using real protocol clients.
4. **Removes** broken and duplicate configurations.
5. **Publishes** protocol-specific subscription files.
6. **Repeats** this cycle **every 2 hours**.

## Supported protocols

| Protocol | Subscription file | Status |
|----------|-------------------|--------|
| All | `subscriptions/all` | ✅ |
| VLESS | `subscriptions/vless` | ✅ |
| VMess | `subscriptions/vmess` | ✅ |
| Trojan | `subscriptions/trojan` | ✅ |
| Shadowsocks | `subscriptions/shadowsocks` | ✅ |
| Hysteria2 | `subscriptions/hysteria2` | ✅ |
| TUIC | `subscriptions/tuic` | ✅ |
| SOCKS | `subscriptions/socks` | ✅ |
| HTTP/HTTPS | `subscriptions/http` | ✅ |

## Subscription links

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/all
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vmess
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/trojan
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/shadowsocks
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/hysteria2
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/tuic
```

A Base64-encoded variant of each file is available with a `.b64` suffix, e.g.:

```
https://raw.githubusercontent.com/nimazolfaghari66-sketch/iran-vpn-radar/main/subscriptions/vless.b64
```

> **Note:** these files are empty until an Iran probe is connected. This is
> deliberate and matches the project policy.

## Client compatibility

| Client | Platform | Recommended format |
|--------|----------|--------------------|
| v2rayNG | Android | Base64 link (`.b64`) |
| v2rayN | Windows | Base64 link |
| sing-box | Cross-platform | Plain text |
| Clash / Clash.Meta | Cross-platform | Use the protocol files |
| NekoBox / Hiddify | Cross-platform | Base64 link |

## How it works

```
discover sources → retrieve → extract → normalise → de-duplicate
      → test from Iran → quality policy → generate files → validate → publish
```

A full cycle runs every 2 hours. If nothing changed, no new commit is created.

## Quality and removal policy

| State | Meaning |
|-------|---------|
| `DISCOVERED` | Found, not yet tested |
| `PENDING_IRAN_TEST` | Waiting for an Iran-based test |
| `TESTING` | Test in progress |
| `WORKING` | Iran-verified |
| `DEGRADED` | One consecutive failure (still published) |
| `FAILED` | Two consecutive failures (removed from output) |
| `EXPIRED` | Expired or invalid (removed from output) |
| `DUPLICATE` | Duplicate |

## Iranian testing architecture

Iranian testing is performed by a **separate probe agent** that must run inside
Iran:

```bash
# On a host inside Iran:
export IRAN_PROBE_TOKEN="a-strong-shared-secret"
python3 probe/probe_agent.py --port 8787
```

Then run the central engine with:

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="the-same-shared-secret"
```

Real tests cover: DNS resolution, server reachability, protocol handshake,
tunnel establishment, internet access through the tunnel, latency, a
size-limited download, and short-term stability.

If no probe is available, no Iranian result is ever fabricated.

### Iranian vantage-point diagnostics (Check-Host)

In addition to the tunnel-verifying probe, the project uses the public
[Check-Host](https://check-host.net) service to measure **reachability from
inside Iran** (Tehran, Isfahan, Shiraz, Qom). Check-Host nodes are remote
diagnostic probes: they can resolve a hostname or open a TCP/UDP socket, but we
cannot run a VPN client on them.

This means Check-Host can tell us that a server is *reachable* from Iran, but it
**cannot** tell us that a tunnel *works*. Its results are diagnostic only, are
never published, and can never move a configuration into the published set.
Only the Iran probe can do that. See [docs/CHECKHOST.md](docs/CHECKHOST.md).

### Iranian ISP probes via Globalping

The project also uses the free, public [Globalping](https://globalping.io)
network, which has volunteer probes on real Iranian ISP links — including
Tehran and a Tabriz probe on the Mobile Communication Company of Iran (MCI)
mobile network.

Globalping runs a **real HTTP client** on the probe, so we can observe a genuine
DNS lookup, TCP connect, **TLS handshake** and HTTP response from inside Iran.
For a TLS-terminating configuration this is stronger evidence than a bare port
check.

It still cannot run a VLESS/VMess/Trojan/Shadowsocks/Hysteria2/TUIC client, so
it can never prove the tunnel works, never observes the tunnel exit IP, and its
results are likewise diagnostic-only and never publishable. See
[docs/GLOBALPING.md](docs/GLOBALPING.md).

We investigated every avenue for Iranian vantage-point testing, including RIPE
Atlas, Iranian cloud platforms and volunteer measurement networks. The full
record — what each can do and the honest remaining path to a full tunnel test —
is in [docs/IRAN_VANTAGE_POINTS.md](docs/IRAN_VANTAGE_POINTS.md).

## Reporting a broken configuration

Use [Issues](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/issues).
Please **never** post private information, passwords or your personal
subscription link in an Issue.

## Contributing

* Suggest new public sources
* Report broken configurations
* Improve the code
* Translate the documentation

Full guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## Security and privacy

* All configurations are **public** and may be unsafe, unstable, or owned by
  someone else.
* This project never stores or publishes passwords, tokens or private keys.
* See [SECURITY.md](SECURITY.md) for details.

## License

[MIT](LICENSE)
