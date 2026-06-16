# AGENTS.md

WARDEN Sensorium is a public-safe product extraction from private WARDEN,
AGENTS, and protected research work.

Rules:
- Do not commit `.env`, credentials, tokens, client data, private corpus, signed
  materials, or `warden-ops` content.
- Keep examples synthetic and local-only.
- Treat human authorization, authorship, and attestation as explicit gates, not
  values inferred from model output.
- Run `python -m pytest`, `python scripts/check_public_surface.py`, and
  `python -m warden_sensorium scan fixtures/sample_project` before release.
- Public claims must be supported by tests, fixtures, docs, or release notes.
