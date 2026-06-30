# Changelog

## 2026-06-29 - Forward Delivery Contract

- Added `project-docs/specs/SPEC-provenance-sensorium-forward-delivery.md` as
  the implementation receipt for the delivery pass.
- Updated GitHub Actions to current checkout/setup-python action majors.
- Added package repository, issues, and homepage metadata.
- Normalized forward-facing punctuation for public-surface scanner
  compatibility.
- Kept sensors, receipt models, CLI behavior, fixtures, and public-boundary
  checks unchanged.

## Current Status

- Runtime: Python 3.9+ with local-only sensors and zero runtime dependencies.
- Surfaces: Python library, CLI, synthetic fixtures, receipt models, public
  boundary checker, and usage guide.
- Verification: pytest suite plus `scripts/check_public_surface.py`.
