# Iran-based probe setup

Iranian testing is the core requirement of this project. A configuration may
only be published as "Iran-verified" when a probe **physically located inside
Iran** tested it with a real protocol client.

This document explains how to deploy that probe and connect it to the engine.

## Why a separate probe

Testing from Germany, Europe, the United States or any other foreign location
tells you nothing about whether a configuration works in Iran. Iran has its own
routing, filtering and ISP behaviour. The project therefore refuses to treat any
foreign test as an Iranian test.

## What the probe needs

* A host with a public address that is **inside Iran**.
* Python 3.10+.
* A VPN protocol client binary: `sing-box` (recommended) or `xray`/`v2ray`.
* Network access to the internet.
* A shared secret token.

## Installing the client binary

The probe uses `sing-box` by default. Install a release build and make sure it is
on `PATH`, or point the engine at it explicitly:

```bash
export IRAN_RADAR_SING_BOX_BIN=/opt/sing-box/sing-box
```

## Running the probe

```bash
export IRAN_PROBE_TOKEN="a-strong-shared-secret-at-least-16-chars"
python3 probe/probe_agent.py --port 8787
```

The probe auto-detects its country. If detection fails and the host really is
inside Iran, assert it explicitly:

```bash
export IRAN_PROBE_COUNTRY=IR
```

If the probe does **not** identify as Iran-based, it refuses to start and
refuses to serve test results. This is deliberate.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Probe identity (name, country, city, ASN, ISP, version) |
| GET | `/geo` | Re-run location detection |
| POST | `/test` | Run tests for a batch of configurations |

Every request must carry `Authorization: Bearer <IRAN_PROBE_TOKEN>`.

### POST /test

```json
{
  "protocol_version": "1",
  "request_id": "1699999999-ab12cd34ef56",
  "options": { "download_bytes": 1000000, "stability_seconds": 10 },
  "configs": [
    { "fingerprint": "…", "protocol": "vless", "uri": "vless://…", "host": "…", "port": 443 }
  ]
}
```

Response:

```json
{
  "protocol_version": "1",
  "probe": { "name": "iran-probe-1", "country": "IR", "city": "Tehran" },
  "tested_at": "2026-01-01T00:00:00Z",
  "results": [
    {
      "fingerprint": "…",
      "success": true,
      "probe_is_iran": true,
      "country": "IR",
      "latency_ms": 210.4,
      "download_kbps": 4200.0,
      "grade": "A",
      "stages": { "dns": true, "reachability": true, "handshake": true, "tunnel": true, "internet": true }
    }
  ]
}
```

## Connecting the engine

```bash
export IRAN_RADAR_PROBE_MODE=remote
export IRAN_PROBE_URL="https://probe.example.ir:8787"
export IRAN_PROBE_TOKEN="the-same-shared-secret"
```

Put these in the repository's Actions secrets when running in CI
(`IRAN_PROBE_URL`, `IRAN_PROBE_TOKEN`) and set the `IRAN_RADAR_PROBE_MODE`
variable to `remote`.

## Alternative: run the engine itself inside Iran

If the whole engine runs on a host inside Iran, use the local runner:

```bash
export IRAN_RADAR_PROBE_MODE=local_iran
export IRAN_RADAR_LOCAL_IS_IRAN=1
```

The explicit `IRAN_RADAR_LOCAL_IS_IRAN=1` flag is required: the engine refuses to
label local tests as Iranian without it.

## Verifying the probe

```bash
curl -s -H "Authorization: Bearer $IRAN_PROBE_TOKEN" \
  http://127.0.0.1:8787/health | python3 -m json.tool
```

The response must show `"country": "IR"`. Anything else means the probe will not
be trusted.

## Health monitoring

The engine records probe health in `data/probe_health.json` and reports it in the
status summary (`status/summary.json` exposes only `iran_testing.available` and
`verified_configs`).
