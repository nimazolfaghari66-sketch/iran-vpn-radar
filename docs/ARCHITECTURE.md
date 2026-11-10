# Architecture

Iran VPN Radar is a modular pipeline. Each stage is an independent module under
`src/radar/` with a single responsibility.

```
                 ┌─────────────────────────────────────────────────────┐
                 │                  pipeline.run_cycle                 │
                 └─────────────────────────────────────────────────────┘
   1 discovery ──► 2 retrieval ──► 3 extract ──► 4 normalize ──► 5 dedupe
        │                                                              │
        ▼                                                              ▼
   sources.json                                                 configs.json
                                                                       │
   6 iran_probe  ◄──────────────── eligible configs ───────────────────┤
        │  (remote probe or local_iran runner; PENDING otherwise)      │
        ▼                                                              │
   7 quality (failure policy state machine) ──────────────────────────►│
        │                                                              │
        ▼                                                              ▼
   10 generate ──► 11 validate ──► 12 publish ──► 13 report
   subscriptions/    validate.py    publish.py     status/
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `config.py` | Environment-driven settings, protocol tables, state constants |
| `logging_setup.py` | Structured JSON logs with secret redaction |
| `models.py` | `Config` and `Source` data models, fingerprints, timestamps |
| `normalize.py` | Parse protocol URIs into `Config` (VLESS/VMess/Trojan/SS/Hysteria2/TUIC/SOCKS/HTTP) |
| `extract.py` | Extract URIs from text, base64, JSON, YAML, Clash and sing-box payloads |
| `dedupe.py` | Fingerprint-based de-duplication and store merge |
| `storage.py` | Atomic JSON persistence for configs, sources, runs, probe health |
| `discovery.py` | Seed loading, repository expansion, recursive source discovery |
| `retrieval.py` | Polite, robots-aware, conditional, size-capped HTTP retrieval |
| `quality.py` | Failure policy state machine and test selection |
| `probe_protocol.py` | Wire protocol + result validation shared with the probe |
| `checkhost.py` | Iranian Check-Host vantage-point diagnostics (reachability only; never publishable) |
| `globalping.py` | Iranian Globalping vantage-point diagnostics (real HTTP/TLS from Iran; never publishable) |
| `iran_probe.py` | Iran test orchestration; the only path to `WORKING` |
| `local_probe.py` | Real tunnel testing with sing-box/xray (used by the probe) |
| `foreign_probe.py` | Clearly-labelled foreign diagnostic (never published) |
| `generate.py` | Subscription file generation (plain + base64) |
| `validate.py` | Structural validation and regression protection |
| `publish.py` | Safe GitHub publishing via the Git Data API |
| `report.py` | Internal and public status reports |
| `secrets_scan.py` | Secret detection for pre-commit and CI |
| `pipeline.py` | Cycle orchestration, locking, crash safety |

## Data model

A configuration is identified by a **fingerprint**: a SHA-256 (truncated) over
protocol, endpoint, transport, security, SNI and credential material. Links that
differ only by their display fragment collapse to one configuration.

Each configuration stores: fingerprint, protocol, source, host, port, transport,
TLS info, discovery time, last successful test, last failed test, consecutive
failure count and current status.

## States

```
DISCOVERED → PENDING_IRAN_TEST → TESTING → WORKING
                                      ↘ DEGRADED → FAILED
                                      ↘ EXPIRED
DUPLICATE  (provenance only, never published)
```

Only `WORKING` and `DEGRADED` appear in published subscription files.

## Iran testing architecture

The central engine never performs an "Iran test". It sends eligible
configurations to a probe and accepts results only when the probe positively
identifies as being inside Iran (`country == IR`). The probe:

1. resolves DNS,
2. checks reachability,
3. performs the protocol handshake,
4. establishes a real tunnel with a real client binary,
5. fetches a URL through the tunnel,
6. measures latency,
7. runs a size-limited download,
8. runs a short stability check.

If no probe is available, eligible configurations are marked
`PENDING_IRAN_TEST` and nothing is published as verified.

## Crash safety and idempotency

* All state writes are atomic (temp file + `os.replace`).
* A cycle lock prevents overlapping executions (stale locks older than 3 hours
  are reclaimed).
* Publishing is a single commit built from the current branch head; a rejected
  ref update (concurrent writer) is retried.
* Generated files are compared against the published versions; an empty or
  regressed replacement is refused.
* Repeated runs do not create duplicate records or corrupt subscription files.

## Scheduling

* GitHub Actions: `.github/workflows/radar-cycle.yml`, `cron: 0 */2 * * *`,
  with a `concurrency` group so runs never overlap.
* Local: `scripts/scheduler.py` (default interval 7200 s).

Internal state is not committed to the public repository; in Actions it is
persisted through the Actions cache so the failure policy works across cycles.
