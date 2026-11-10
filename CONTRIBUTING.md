# Contributing to Iran VPN Radar

Thank you for helping improve Iran VPN Radar. This document explains how to
contribute safely and effectively.

> **Security first:** this repository is public. Never include tokens, passwords,
> private keys, personal subscription links, private IP addresses or internal
> infrastructure details in an Issue, pull request, commit or file.

## Ways to contribute

* **Suggest a new public source.** Open an Issue using the "New source
  suggestion" template. The source must be publicly reachable without
  authentication, paywall or access-control bypass.
* **Report a broken configuration.** Use the "Broken configuration" template.
  Include the protocol and the failing endpoint. Do not paste credentials.
* **Report a bug or request a feature.** Use the appropriate Issue template.
* **Improve the code.** Open a pull request.
* **Translate the documentation.** README files exist for Persian (primary),
  English, Arabic, Chinese, Russian and Spanish.

## Development setup

```bash
git clone https://github.com/nimazolfaghari66-sketch/iran-vpn-radar.git
cd iran-vpn-radar
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

All tests must pass and the secret scan must be clean before a pull request can
be merged:

```bash
python scripts/scan_secrets.py --allow-private-ips
```

## Coding standards

* Standard library first. Add a dependency only when it removes significant
  complexity, and justify it in the pull request.
* Keep modules single-purpose and aligned with the architecture described in the
  README (`src/radar/`).
* Never raise from the extraction or retrieval paths on hostile input; degrade
  gracefully.
* Redact anything sensitive through `radar.logging_setup` before logging.
* Make operations idempotent: repeated runs must not create duplicate records or
  corrupt output files.

## Adding a public source

Sources are registered in `sources/seed_sources.json`. Before adding one, verify:

1. It is publicly reachable without authentication or paywall.
2. It does not require bypassing access controls.
3. Its `robots.txt` (if any) permits automated retrieval.
4. It actually contains free, publicly published configurations.

The runtime also discovers new sources automatically, so seeds are only a
bootstrap.

## Pull request process

1. Create a branch with a descriptive name.
2. Make focused changes with clear commit messages.
3. Run the tests and the secret scan.
4. Open a pull request against `main` and describe what changed and why.

## What we will not accept

* Configurations or credentials that are stolen, leaked, private or paid.
* Any attempt to scan, exploit, brute-force or attack third-party servers.
* Changes that label a non-Iranian test as an Iranian test.
* Code that commits secrets or personal data.
* Artificial attempts to inflate stars, forks, watchers or contributors.
