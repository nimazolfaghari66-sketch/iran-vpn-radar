# Check-Host Iranian vantage-point testing

[Check-Host](https://check-host.net) runs a network-diagnostics service with
nodes in many countries, including several **inside Iran**. Iran VPN Radar uses
those Iranian nodes as an additional, *diagnostic* vantage point.

## What Check-Host is — and is not

Check-Host nodes are **remote diagnostic probes**. We can ask a node to:

* resolve a hostname (`dns`),
* open a TCP socket to a host:port (`tcp`),
* make an HTTP/HTTPS request (`http`),
* send a UDP probe (`udp`),
* ping an address (`ping`).

We **cannot** install software on them, and we **cannot** run a VPN client on
them. Therefore a reachable port is **not** a working tunnel.

This distinction is enforced in code. Check-Host can never mark a configuration
as `WORKING` and can never publish anything. Only the dedicated Iran probe agent
(`probe/probe_agent.py`, see [IRAN_PROBE.md](IRAN_PROBE.md)) can verify a tunnel,
because it runs a real protocol client on a host inside Iran.

## Classification taxonomy

Every Check-Host observation is recorded with one of these labels:

| Label | Meaning |
|-------|---------|
| `IRAN_DNS_OK` | The node's resolver returned an A/AAAA record for the hostname. |
| `IRAN_TCP_REACHABLE` | A TCP connection to host:port succeeded. |
| `IRAN_HTTP_REACHABLE` | An HTTP/HTTPS request succeeded. |
| `IRAN_UDP_REACHABLE` | A UDP probe was answered. |
| `IRAN_TIMEOUT` | The node timed out. |
| `IRAN_UNREACHABLE` | Connection refused, reset, or no result. |
| `IRAN_FULL_TUNNEL_VERIFIED` | **Reserved.** Only the Iran probe can produce this. Check-Host never does. |

Only the first four are "reachable" signals, and all four are **informational
only**. None of them is a publishable state.

## Node discovery

Nodes are discovered dynamically from the live registry
(`https://check-host.net/nodes/hosts`) on every cycle. Node identity is the
registry identifier (e.g. `ir1.node.check-host.net`), never a hard-coded IP: a
node can be reassigned and an IP can change hands.

A small historical list of Iranian node IPs is kept **for comparison only** so
the report can show which previously seen nodes are still present:

```bash
python -m radar --root . checkhost-nodes
```

This prints the current Iranian nodes (country, city, identifier, IP, ASN) and a
comparison against the historical list, including any city change.

## Running diagnostics

```bash
# Test a protocol-diverse sample from all Iranian nodes
python -m radar --root . checkhost-test --batch 12 --checks dns tcp

# Restrict to specific cities
python -m radar --root . checkhost-test --city Tehran --city Isfahan

# Show the aggregated summary
python -m radar --root . checkhost-status
```

The `checkhost-test` command never modifies configuration status. It writes
timestamped results to `data/checkhost_results.json` (internal, gitignored) and
prints a summary.

## Rate limiting

The client spaces submissions at least `IRAN_RADAR_CHECKHOST_MIN_INTERVAL`
seconds apart (default 2.5s) and polls results with a bounded budget. We send a
descriptive `User-Agent`. Please keep rates modest and respect the service.

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `IRAN_RADAR_CHECKHOST` | `1` | Enable/disable the diagnostic round |
| `IRAN_RADAR_CHECKHOST_BATCH` | `12` | Max configurations per round |
| `IRAN_RADAR_CHECKHOST_CHECKS` | `dns,tcp` | Comma-separated checks |
| `IRAN_RADAR_CHECKHOST_MIN_INTERVAL` | `2.5` | Min seconds between submissions |

## Reporting

The internal report (`data/summary.internal.json`) contains the full Check-Host
aggregate. The public report (`status/summary.json`) contains **aggregate counts
only** — no hostnames, no IPs, no per-configuration rows — under the
`checkhost` key.

## What this proves and what it cannot prove

**Proves:** whether a configuration's server resolves and its port is reachable
*from Iranian networks*, per city, at a given time.

**Cannot prove:** that the VPN tunnel works, that the credentials are valid,
that the protocol handshake succeeds, or that a user in Iran could actually
browse through it. Those require the Iran probe.

A configuration reachable from Iran but never tunnel-tested stays
`PENDING_IRAN_TEST` and is **not** published.
