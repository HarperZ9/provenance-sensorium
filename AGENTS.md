# AGENTS.md

Provenance Sensorium is a public-safe live-state awareness and provenance
framework for AI-assisted research and security work.

Rules:
- Do not commit `.env`, credentials, tokens, client data, private corpus, or
  signed materials.
- Keep examples synthetic and local-only.
- Treat human authorization, authorship, and attestation as explicit gates, not
  values inferred from model output.
- Run `python -m pytest`, `python scripts/check_public_surface.py`, and
  `python -m provenance_sensorium scan fixtures/sample_project` before release.
- Public claims must be supported by tests, fixtures, docs, or release notes.
