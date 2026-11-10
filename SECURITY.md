# Security Policy

## Reporting a vulnerability

Please report security issues **privately** through GitHub's
[private vulnerability reporting](https://github.com/nimazolfaghari66-sketch/iran-vpn-radar/security/advisories/new)
rather than in a public Issue.

Never post credentials, tokens, private keys or personal subscription links in a
public Issue or pull request.

## Repository secrecy rules

This repository is **public**. Everything committed to it can be read, copied,
indexed and redistributed by anyone. The following must never be committed:

* API tokens, GitHub tokens, passwords, private keys, SSH credentials
* personal accounts or email credentials
* private subscription URLs or user-specific authentication data
* internal server addresses or sensitive infrastructure details
* environment variables or secret configuration files
* private diagnostic logs

Credentials are supplied only through environment variables or the platform's
secret store. A pre-commit secret scan (`scripts/scan_secrets.py`) and a CI
secret-scanning job enforce this.

## How the project protects secrets

* `src/radar/logging_setup.py` redacts tokens, credentials embedded in URLs,
  private keys and known sensitive environment variables from every log line.
* `src/radar/secrets_scan.py` detects provider tokens, private keys, URL
  credentials, private IP ranges and sensitive filenames.
* The GitHub publisher writes only to an allow-listed set of output paths
  (`subscriptions/`, `status/`, `sources/`) and never force-pushes.

## Iran probe security

The Iran-based probe is authenticated with a shared bearer token
(`IRAN_PROBE_TOKEN`) that is never committed. Traffic between the central engine
and the probe should be carried over TLS. A probe that does not positively
identify itself as being inside Iran has all of its results rejected.

## Data handling

* Internal state (configuration history, failure counters, source registry) is
  kept out of the public repository.
* Only safe aggregate statistics are published in `status/summary.json`.
* No private diagnostic logs are ever published.

## Threat model and limitations

* All published configurations come from **third parties** and are **not**
  audited for safety. They may be malicious, unstable or unlawful in your
  jurisdiction.
* Testing establishes reachability only; it does not guarantee that a
  configuration will not log or inspect your traffic.
* Use at your own risk and comply with applicable law.
