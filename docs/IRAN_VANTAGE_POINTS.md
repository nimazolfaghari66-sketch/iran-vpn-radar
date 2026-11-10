# Iranian vantage points: what we investigated and what is actually possible

This document records every avenue the project investigated for testing VPN
configurations **from inside Iran**, what each one can and cannot do, and the
honest remaining path to a full tunnel test. It exists so the work is not
re-treaded and so no result is ever overstated.

## The objective

Test a configuration from an Iranian network vantage point and, ideally, prove
the *tunnel* works: handshake, traffic through the tunnel, exit IP, latency and
stability.

## The hard boundary

There are two fundamentally different capabilities:

1. **Reachability probing** — a remote agent opens a socket / runs an HTTP or
   ping client *from* an Iranian network towards the config server. This is
   cheap, automatic and widely available.
2. **Tunnel execution** — running a real VLESS/VMess/Trojan/Shadowsocks/
   Hysteria2/TUIC **client** on a host inside Iran, which is the only way to
   establish the tunnel and send traffic through it.

Reachability probing is not a substitute for tunnel execution. A server can be
perfectly reachable from Iran and the tunnel still be dead (wrong UUID, wrong
SNI, blocked transport, expired account, bad cipher). Only (2) can produce
`IRAN_FULL_TUNNEL_VERIFIED`.

**No free, automatic service performs (2).** We searched for one (GitHub
repository search across several queries, plus the networks below) and found
none. Tunnel execution fundamentally requires running our own code on a host
inside Iran — a host we either own there or that a volunteer runs there.

## What we investigated

| Method | Type | Automatic? | Iranian vantage point? | Verdict |
|--------|------|-----------|------------------------|---------|
| **Globalping** (globalping.io) | HTTP/DNS/ping/traceroute | yes, no auth | **yes** — Tehran + Tabriz probes on real ISP links (incl. MCI mobile) | **Integrated.** Real TLS handshake from Iran. Cannot run a VPN client. |
| **Check-Host** (check-host.net) | DNS/TCP/UDP/HTTP/ping | yes | yes — Tehran, Isfahan, Shiraz, Qom nodes | **Integrated.** Reachability only. |
| RIPE Atlas | ping/traceroute/DNS | yes | yes — hundreds of IR probes | **Rejected.** Only runs Atlas' own measurement types; cannot execute a VPN client or custom code. |
| Iranian PaaS / cloud (liara, ArvanCloud, Fandogh) | hosting | no | yes | **Not reachable** from the build sandbox (HTTP 000). Would also require a paid account and a deployed server. |
| Public Speedtest/measurement APIs | throughput | partial | some | No arbitrary-tunnel capability; not usable for tunnel verification. |
| Volunteer-run measurement networks | varies | varies | some | Same limitation as Globalping: no custom client execution. |
| GitHub-hosted Iranian test scripts | varies | no | n/a | None found that perform real tunnel tests from Iran. |

## What we have running automatically (and its ceiling)

Two Iranian vantage-point sources run on every two-hour cycle, with no server of
our own and no manual step:

* **Globalping** — `src/radar/globalping.py`, docs in `GLOBALPING.md`. Runs a
  real HTTP/TLS client on Iranian probes. Proves DNS + TCP + **TLS handshake**
  + HTTP from Iran. A TLS handshake from Iran is the strongest automatic signal
  available.
* **Check-Host** — `src/radar/checkhost.py`, docs in `CHECKHOST.md`. DNS + TCP +
  UDP reachability from multiple Iranian cities.

Both are **diagnostic only**. Neither can run a VPN client, so neither can
establish a tunnel, send traffic through it, or observe the exit IP. Neither is
publishable. This is enforced in code and covered by tests
(`tests/test_globalping.py`, `tests/test_iran_gate.py`).

## The remaining path: a lightweight probe on an ordinary Iranian connection

Because no automatic service can execute a tunnel, the only way to reach
`IRAN_FULL_TUNNEL_VERIFIED` is to run the probe agent
(`probe/probe_agent.py`, docs in `IRAN_PROBE.md`) on a host inside Iran.

The good news: this does **not** require buying a server. The agent is a small
Python service that runs a local `sing-box`/`xray` client. Any ordinary Iranian
internet connection — a home PC, a laptop, a phone via Termux, a spare machine —
can run it. The only requirement is that the host is genuinely inside Iran, so
its test result is a genuine Iranian test.

For a connection behind CGNAT (which is most Iranian home/mobile connections),
the recommended deployment is a **pull model**: the probe reaches out to a
rendezvous we control, polls for pending test jobs, runs them, and posts results
back. That way the probe needs no inbound port and works from any ordinary
connection. The rendezvous endpoint is configured through
`IRAN_RADAR_PROBE_URL` / `IRAN_PROBE_TOKEN`; the engine already speaks the wire
protocol in `src/radar/probe_protocol.py`.

Until such a probe is connected, every configuration stays `PENDING_IRAN_TEST`
and nothing is published as Iran-verified — exactly as required.

## The invariant

> A configuration is published as Iran-verified **only** when a real tunnel test
> executed on a host inside Iran succeeds. No foreign-location test, no
> reachability probe, and no synthetic result is ever published as an Iranian
> test.

This is not a guideline; it is enforced by `config.PUBLISHABLE_STATES`, by the
absence of `IRAN_FULL_TUNNEL_VERIFIED` from every diagnostic taxonomy, and by
the safety tests. The build host for the project runs in the United States
(Google Cloud, Council Bluffs) and its location is never treated as Iranian.
