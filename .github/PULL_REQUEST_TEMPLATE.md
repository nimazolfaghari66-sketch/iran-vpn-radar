<!--
Thanks for contributing. Please read CONTRIBUTING.md and SECURITY.md first.
Never include secrets, tokens, personal links or private infrastructure details.
-->

## What changed

<!-- A short description of the change and why it is needed. -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Translation
- [ ] New public source
- [ ] Refactor / cleanup

## Checklist

- [ ] Tests pass: `PYTHONPATH=src python -m unittest discover -s tests -v`
- [ ] Secret scan is clean: `python scripts/scan_secrets.py --allow-private-ips`
- [ ] No secrets, tokens, private keys or personal data are included
- [ ] The change does not label a non-Iranian test as an Iranian test
- [ ] The change does not add paid services or bypass access controls
- [ ] Generated subscription files (if touched) still validate
