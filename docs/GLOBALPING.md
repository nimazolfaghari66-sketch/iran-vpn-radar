# Iranian vantage-point testing via Globalping

[Globalping](https://globalping.io) is a free, public, volunteer-run network of
network-measurement probes. Unlike Check-Host, whose Iranian nodes only expose a
bare TCP socket, a Globalping probe runs a **real HTTP client**. That means we
can observe, from inside Iran, a genuine DNS lookup, TCP connect, **TLS
handshake** and HTTP response against a configuration's server.

## Why Globalping is stronger than Check-Host

| Signal | Check-Host | Globalping |
|--------|-----------|-----------|
| DNS resolution from Iran | yes | yes |
| TCP connect from Iran | yes | yes |
| ICMP ping from Iran | yes | yes |
| **Real TLS handshake from Iran** | no | **yes** |
| Real HTTP response from Iran | partial | yes |
| Runs a VPN client | no | no |

For a TLS-terminating configuration (VLESS/VMess/Trojan with TLS, or any server
that speaks TLS on its port), a successful Globalping HTTPS measurement proves
the server completes a **real TLS handshake from an Iranian ISP**. That is
strictly stronger evidence than a TCP port check.

## What Globalping still cannot prove

A Globalping probe cannot run a VLESS/VMess/Trojan/Shadowsocks/Hysteria2/TUIC
client, so it can never establish the *tunnel*, send traffic *through* it, or
observe the tunnel exit IP. Therefore — exactly like Check-Host — every result
is **diagnostic only and never publishable**. Globalping can never move a
configuration to `WORKING`. Only the dedicated Iran probe agent
(`probe/probe_agent.py`) may produce `IRAN_FULL_TUNNEL_VERIFIED`.

## Iranian probes

Probes are discovered dynamically from `GET /v1/probes` on every cycle; we never
hard-code a probe, because the network is volunteer-run and its Iranian members
change. At the time of writing, 8 probes were live on Iranian networks:

| City | ASN | Network | Type |
|------|-----|---------|------|
| Tehran | AS202468 | Noyan Abr Arvan / AbrArvan CDN and IaaS | datacenter |
| Tehran | AS48551 | Sindad Network Technology | datacenter |
| Tehran | AS48715 | Sefroyek Pardaz Engineering | eyeball |
| Tehran | AS59441 | Hostiran Network | datacenter |
| Tehran | AS59580 | Batterflyai Media | datacenter |
| Tehran | AS34918 | Pishgaman Toseeh Ertebattat | eyeball |
| Tabriz | AS197207 | **Mobile Communication Company of Iran** | eyeball |

The Tabriz probe sits on MCI's mobile network — a genuine consumer mobile link,
which is exactly the vantage point an Iranian end user has.

## Measurement types and how we map them

| Config protocol | Globalping measurement | Observed signal |
|-----------------|------------------------|-----------------|
| VLESS / VMess / Trojan / Shadowsocks | `http` with `protocol: HTTPS`, `port` | DNS → TCP → TLS → HTTP |
| SOCKS / HTTP proxy | `http` with `protocol: HTTP`, `port` | DNS → TCP → HTTP |
| Hysteria2 / TUIC (UDP) | `ping` (ICMP) | DNS → ICMP |

A configuration whose host is not a valid measurement target (for example a URL
mistakenly stored as a host) is skipped with a note rather than sent as a bad
request.

## Classification taxonomy

Results reuse the shared Iranian reachability taxonomy. The strongest stage any
probe reached becomes the configuration's summary:

| Label | Meaning |
|-------|---------|
| `IRAN_DNS_OK` | The probe's resolver returned an address. |
| `IRAN_ICMP_REACHABLE` | ICMP echo was answered. |
| `IRAN_TCP_REACHABLE` | TCP connect succeeded. |
| `IRAN_TLS_OK` | TLS handshake completed (but no HTTP response). |
| `IRAN_HTTP_REACHABLE` | A full HTTP response was received. |
| `IRAN_TIMEOUT` | Timed out. |
| `IRAN_UNREACHABLE` | Refused / reset / no result. |

None of these is publishable. `IRAN_FULL_TUNNEL_VERIFIED` is deliberately absent
from the Globalping taxonomy and can only come from the Iran probe.

## Running diagnostics

```bash
# Discover current Iranian probes
python -m radar --root . globalping-probes

# Test a protocol-diverse sample from Iranian probes
python -m radar --root . globalping-test --batch 10 --limit 2

# Restrict to a city
python -m radar --root . globalping-test --city Tehran

# Show the aggregated summary
python -m radar --root . globalping-status
```

Results are written to `data/globalping_results.json` (internal, gitignored).
The command never modifies configuration status.

## Rate limits and politeness

Globalping allows roughly 250 measurement requests per hour per IP. We space
submissions at least `IRAN_RADAR_GLOBALPING_MIN_INTERVAL` seconds apart (default
1.5s), send a descriptive `User-Agent`, and poll with a bounded budget. Keep the
per-cycle batch modest so the two-hour schedule stays well inside the limit.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `IRAN_RADAR_GLOBALPING` | `1` | Enable/disable the diagnostic round |
| `IRAN_RADAR_GLOBALPING_BATCH` | `10` | Max configurations per round |
| `IRAN_RADAR_GLOBALPING_LIMIT` | `2` | Probes per measurement |
| `IRAN_RADAR_GLOBALPING_MIN_INTERVAL` | `1.5` | Min seconds between submissions |
| `IRAN_RADAR_GLOBALPING_TIMEOUT` | `60` | HTTP timeout for the API |

## Reporting

The internal report (`data/summary.internal.json`) contains the full aggregate,
including a `tls_verified` count. The public report (`status/summary.json`)
contains **aggregate counts only** under the `globalping` key — no hostnames, no
IPs, no per-configuration rows.

## Terms

Globalping is a public measurement service. We use it only for its intended
purpose: running standard ping/HTTP measurements from its public probes. We do
not attempt to execute arbitrary code on probes, and we keep request rates low.
