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
* `docs/IRAN_VANTAGE_POINTS.md` — record of every Iranian vantage-point method
  investigated and the honest remaining path to a full tunnel test.
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
| `IRAN_RADAR_TUNNEL_VERIFY` | `1` to run global real-tunnel verification (default on) |
| `IRAN_RADAR_TUNNEL_BATCH` | max configs per tunnel round (default 40; CI uses 800) |
| `IRAN_RADAR_TUNNEL_WORKERS` | parallel sing-box workers (default 8; CI uses 16) |
| `IRAN_RADAR_TUNNEL_DOWNLOAD_BYTES` | bytes downloaded per tunnel download stage |
| `IRAN_RADAR_TUNNEL_STABILITY_SECONDS` | seconds of stability sampling per config |
| `IRAN_RADAR_SING_BOX_BIN` | explicit sing-box path (else `.bin/sing-box`, then `PATH`) |
| `IRAN_RADAR_PUBLISH` | `1` to enable GitHub publishing |
| `IRAN_RADAR_DRY_RUN` | `1` for a no-write run |

## Verification tiers (do not conflate)

| Tier | Runs where | Can publish? | Where output goes |
|------|-----------|--------------|-------------------|
| Check-Host / Globalping | Iranian nodes/probes (reachability only) | No | diagnostics only |
| Global tunnel verification (`tunnel_verify.py`) | engine host / CI runner (NOT Iran) | No | `subscriptions/candidates/*` |
| Iran-priority candidates (`tunnel_verify.py`) | engine host tunnel + Iranian reachability | Yes (weaker label) | `subscriptions/iran-priority/*` |
| Iran probe (`iran_probe.py`) | a real host inside Iran | Yes (strongest label) | `subscriptions/*` |

Evidence levels, weakest to strongest (`cfg.EVIDENCE_LEVELS`):

* `GLOBAL_TUNNEL_TESTED` — a real tunnel was established from the engine host
  (NOT Iran). Published to `subscriptions/candidates/*`.
* `IRAN_NETWORK_REACHABLE` — reached from ≥1 Iranian vantage point.
* `IRAN_PRIORITY_CANDIDATE` — global tunnel **and** positive Iranian
  reachability (a TCP-handshake-or-better observation, `cfg.IRAN_PRIORITY_REACHABLE`).
  Published to `subscriptions/iran-priority/*`. This is the strongest tier the
  system can publish without a probe inside Iran, and it is explicitly **not**
  `IRAN_FULL_TUNNEL_VERIFIED`.
* `IRAN_FULL_TUNNEL_VERIFIED` — a real tunnel from inside Iran. The only level
  allowed in `subscriptions/*`, and only the Iran probe can produce it.

The Iran gate is the only path to `subscriptions/*`. The global tunnel tier
stores its result in `Config.tunnel_status` (separate from `Config.status`) and
labels records `GLOBAL`, so it can never promote a config to `WORKING`.
`scripts/install_client.py` installs a pinned, checksum-verified sing-box into
`.bin/` (git-ignored).

## Healthy-pool targets and accumulating tunnel rounds

Real tunnel verification works toward a **per-protocol** healthy target, never a
combined total:

* `cfg.TARGET_PER_PROTOCOL` (default `100`) — healthy configs wanted for *each*
  protocol. 100 VLESS + 100 Trojan + … = 8 × 100, not 100 overall.
* `cfg.MIN_TUNNEL_BATCH` (default `200`) — the *minimum* real tunnel tests per
  cycle, not a maximum. `tunnel_verify.run_tunnel_rounds()` runs at least this
  many, then keeps adding batches while any protocol is below target, stopping
  when all targets are met, no untested configs remain, or the time budget
  (`IRAN_RADAR_TUNNEL_TIME_BUDGET_S`, default 2400s) runs out.
* `select_candidates()` round-robins across protocols, most-short first, so one
  batch samples every protocol below target instead of exhausting one.
* Successes **accumulate**; a later batch never replaces earlier healthy configs.
  Partial progress is persisted, so a truncated cycle resumes next time.

`tunnel_verify.build_dashboard()` / `dashboard_maps()` expose per-protocol
discovered / tested / successful / healthy / target / shortage / iran-priority
counts. `status/summary.json` publishes them as flat maps
(`candidates.healthy.<proto>`, `candidates.shortage_by_protocol.<proto>`, …),
which the READMEs read via dynamic badges.
