# Public Boundary

WARDEN Sensorium publishes a reusable safety and provenance pattern. It does not
publish the private WARDEN core.

## Excluded

- `warden-ops` content.
- Credentials, tokens, `.env` values, private keys, or account data.
- Client names, customer records, signed documents, private engagement material,
  or private research corpus dumps.
- Live target tooling, exploit chains, credential acquisition workflows,
  persistence, stealth, or operational runbooks.

## Included

- Public-safe data models.
- Synthetic fixtures.
- Local-only sensors.
- Exception-layer policies.
- Provenance receipts.
- Human-gate semantics for authorship, authorization, and attestation.

## Release Rule

Every public claim must be supported by test evidence, fixture evidence,
documentation, or a release note. The package must pass:

```powershell
python -m pytest
python scripts/check_public_surface.py
python -m warden_sensorium scan fixtures/sample_project
```
