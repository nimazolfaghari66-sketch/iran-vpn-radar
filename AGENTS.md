# AGENTS.md — repository notes for AI agents and contributors

## Project

`iran-vpn-radar` discovers public free VPN configurations, normalises and
de-duplicates them, tests them **from inside Iran**, and publishes
protocol-specific subscription files to this public repository every 2 hours.

## Hard rules (never violate)

1. **Never** publish a configuration as Iran-verified unless a probe physically
   inside Iran returned a real, successful tunnel test. No foreign or synthetic
   test may be labelled Iranian.
2. **Never** commit secrets: tokens, passwords, private keys, personal
   subscription links, private IPs or internal infrastructure details.
3. **Never** bypass authentication, paywalls, robots policies or access controls.
4. **Never** scan, exploit, brute-force or attack third-party servers.
5. **Never** fabricate test results, sources or counts.
6. Do not use paid APIs, servers, domains or VPN subscriptions.

## Build, test, run

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/scan_secrets.py --allow-private-ips
PYTHONPATH=src python -m radar --root . cycle          # full cycle
PYTHONPATH=src python -m radar --root . discover       # discovery only
PYTHONPATH=src python -m radar --root . status         # status report
PYTHONPATH=src python -m radar --root . validate       # validate subscriptions
```

## Layout

* `src/radar/` — the engine (see `docs/ARCHITECTURE.md`).
* `src/radar/checkhost.py` — Iranian Check-Host vantage-point diagnostics
  (reachability only; see `docs/CHECKHOST.md`). Never publishable.
* `src/radar/globalping.py` — Iranian Globalping vantage-point diagnostics with
  real HTTP/TLS observations from Iranian ISP probes (see `docs/GLOBALPING.md`).
  Never publishable.
* `probe/probe_agent.py` — the Iran-based probe service (the only tunnel verifier).
* `sources/seed_sources.json` — bootstrap list of public sources.
* `subscriptions/` — generated output (published).
* `status/` — safe public aggregate reports (published).
* `data/` — internal state (gitignored, never published).
* `tests/` — unit tests.

## Conventions

* Standard library first; PyYAML is the only runtime dependency.
* Atomic writes for all state (`storage._atomic_write_json`).
* Route all logging through `radar.logging_setup` so secrets are redacted.
* Degrade gracefully: extraction and retrieval must never raise on hostile input.
* Keep the pipeline idempotent; repeated runs must not duplicate records or
  corrupt output.
* Run the secret scan before every commit.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | Publishing (Actions provides it automatically) |
| `IRAN_RADAR_PROBE_MODE` | `remote`, `local_iran` or `unavailable` |
| `IRAN_PROBE_URL` | Iran probe base URL |
| `IRAN_PROBE_TOKEN` | Iran probe shared secret |
| `IRAN_RADAR_LOCAL_IS_IRAN` | `1` only when the runner really is inside Iran |
| `IRAN_RADAR_CHECKHOST` | `1` to run Iranian Check-Host diagnostics |
| `IRAN_RADAR_CHECKHOST_BATCH` | max configs per Check-Host round (default 12) |
| `IRAN_RADAR_CHECKHOST_CHECKS` | `dns,tcp` (also `http`, `udp`, `ping`) |
| `IRAN_RADAR_CHECKHOST_MIN_INTERVAL` | min seconds between Check-Host submissions |
| `IRAN_RADAR_GLOBALPING` | `1` to run Iranian Globalping diagnostics |
| `IRAN_RADAR_GLOBALPING_BATCH` | max configs per Globalping round (default 10) |
| `IRAN_RADAR_GLOBALPING_LIMIT` | probes per measurement (default 2) |
| `IRAN_RADAR_GLOBALPING_MIN_INTERVAL` | min seconds between Globalping submissions |
| `IRAN_RADAR_PUBLISH` | `1` to enable GitHub publishing |
| `IRAN_RADAR_DRY_RUN` | `1` for a no-write run |
