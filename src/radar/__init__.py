"""Iran VPN Radar — public free VPN subscription discovery and testing system.

The package is organised as independent, single-responsibility components:

    config          runtime settings
    logging_setup   structured logs with secret redaction
    models          protocol configuration model + state constants
    normalize       URI <-> internal model, protocol classification
    extract         configuration extraction from many payload shapes
    dedupe          fingerprint based de-duplication
    storage         persistent state (configs, sources, runs)
    discovery       discovery of new public sources
    retrieval       polite, rate-limited, robots-aware source retrieval
    quality         failure policy / state machine
    probe_protocol  transport for talking to an Iran based probe
    iran_probe      Iran test orchestration (and PENDING_IRAN_TEST handling)
    generate        subscription file generation
    validate        subscription file validation
    publish         safe GitHub publishing
    report          machine-readable status reports
    secrets_scan    pre-commit secret scanning
    pipeline        the 2-hour cycle orchestration
"""

__version__ = "1.0.0"
