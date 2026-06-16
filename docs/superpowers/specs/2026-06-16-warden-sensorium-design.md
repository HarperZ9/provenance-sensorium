# WARDEN Sensorium Design

## Purpose

WARDEN Sensorium is a public-safe live-state awareness and provenance framework
for AI-assisted research and security work. It turns local observations into
structured evidence, evaluates them through explicit exception layers, and
preserves a chain of provenance that a human can inspect before any claim,
handoff, publication, or attestation.

The product is derived from the WARDEN/AGENTS/protected-research spine, but it is
not a publication of the private core. It models the useful architecture:
sensor organs, exception membranes, evidence receipts, and human gates.

## Source Concepts

- Protected research thesis: the recurring structure is the ownerless seam:
  "the exception is the sensor is the membrane."
- Straight-line layer: seams are witnesses, not foundations. The product should
  collect bounded evidence without laundering a private or human-only premise.
- Human-gate runbook: AI can prepare substrate and provenance, but ownership,
  authorship, and attestation stay human.
- WARDEN/AGENTS inventory: existing private pieces include release gates,
  provenance, evidence, records, response registries, probe engines, and safe IO
  controls. Sensorium extracts the public pattern, not private data.

## Product Shape

Sensorium ships as a Python package and CLI.

Core abstractions:

- `Observation`: a normalized live-state reading from a sensor.
- `Provenance`: the source path, command, digest, timestamp, and confidence for
  an observation.
- `Sensor`: a bounded component that reads one type of state.
- `ExceptionLayer`: a policy membrane that turns observations into pass, warn,
  block, needs-human, or unverified decisions.
- `Receipt`: a signed-by-content JSON record tying observations to decisions.
- `HumanGate`: an explicit marker that something cannot be truthfully delegated
  to an AI system.

Initial sensors:

- File sensor: hashes and summarizes allowed files.
- Git sensor: reports branch, commit, dirty count, and remote without dumping
  private diffs.
- Claim sensor: checks Markdown claims for evidence markers and maturity labels.
- Secret-shape sensor: detects token, credential, and private-contact patterns.
- Fixture sensor: validates synthetic sample projects used in public examples.

Initial exception layers:

- Secret guard: blocks secret-shaped values.
- Claim guard: flags claims that lack evidence or maturity labels.
- Boundary guard: blocks paths matching private-corpus, `.env`, `warden-ops`, or
  client-data patterns.
- Human gate: marks authorship, authorization, and attestation claims as
  `needs-human` unless an explicit human-gate receipt exists.

## CLI

Commands:

- `sensorium scan PATH`: run the default sensor and exception stack.
- `sensorium receipt PATH --output FILE`: write a JSON receipt.
- `sensorium explain RECEIPT`: render a human-readable Markdown summary.
- `sensorium init-fixture PATH`: create a synthetic demo project.

All commands must default to local-only operation. No network calls are needed
for v0.1.0.

## Public Boundary

The repository must not contain:

- `warden-ops` source, runbooks, access material, diagnostics, or recovery
  tooling.
- Private research corpus beyond short design summaries.
- Client names, customer data, signed documents, credentials, tokens, `.env`
  values, or live target details.
- Offensive automation, exploit code, credential acquisition tooling, or
  stealth/persistence workflows.

The repository may contain:

- Public-safe abstractions.
- Synthetic fixtures.
- Defensive release and claim gates.
- Provenance schemas.
- Documentation explaining the membrane/human-gate model in engineering terms.

## Architecture

The implementation is intentionally small but product-shaped:

- `models.py`: dataclasses and status enums.
- `sensors.py`: file, git, claim, secret-shape, and fixture sensors.
- `layers.py`: exception-layer policies and default stack.
- `receipts.py`: JSON serialization, digesting, and Markdown explanation.
- `cli.py`: command-line interface.
- `public_surface.py`: repo hygiene and secret-shape checks for release.

The CLI composes the library. Tests exercise the library first, then CLI
behavior through subprocess-free function calls where possible.

## Error Handling

- Sensors return structured `Observation` objects when a reading is possible.
- Unreadable paths become `unverified` observations with error context, not
  swallowed failures.
- Exception layers never mutate observations.
- Receipt writing fails closed if any blocking decision is present unless the
  caller passes an explicit `--allow-blocked` flag. v0.1.0 does not need this
  flag; blocked receipts can still be explained in memory.

## Testing

Required tests:

- Models serialize stable statuses and provenance.
- File sensor hashes fixture files.
- Git sensor handles non-git fixture paths without crashing.
- Claim guard warns on unevidenced claims and passes evidence-marked claims.
- Secret guard blocks token-shaped values.
- Boundary guard blocks `.env` and `warden-ops` paths.
- Human gate marks authorship/attestation claims as `needs-human`.
- CLI scan returns nonzero for blocked findings and zero for clean fixtures.
- Public-surface script rejects `.env`, private path strings, and secret-shaped
  patterns in public files.

## Release Criteria

- `python -m pytest` passes.
- `python scripts/check_public_surface.py` passes.
- `python -m warden_sensorium scan fixtures/sample_project` passes.
- Git status is clean except ignored local cache/runtime files.
- GitHub repository is public.
- GitHub release `v0.1.0` exists and points at `main`.
- Portfolio site links to WARDEN Sensorium as a large public product under
  WARDEN / AI safety / live-state awareness.
