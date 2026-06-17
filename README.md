# Provenance Sensorium

Live-state awareness and provenance for AI-assisted research and security work.

Provenance Sensorium turns local project state into structured observations, passes
those observations through explicit exception layers, and emits receipts that a
human can inspect before making claims, handoffs, publications, or attestations.

It publishes a small, reusable pattern for safer research workflows. Everything in
this repository is public-safe: synthetic fixtures, local-only sensors, and
public abstractions.

## Core Idea

AI systems need better live-state awareness, but awareness is not authority.
Sensorium separates four things:

- **Sensor organs** read bounded local state.
- **Exception layers** classify what the sensors found.
- **Provenance receipts** preserve source, digest, timestamp, and confidence.
- **Human gates** mark claims that require human ownership.

The result is a small framework for safer research workflows: the system can
prepare evidence, but it cannot truthfully sign the human part for you.

## Quick Start

```powershell
python -m pip install -e .
python -m pytest
python scripts/check_public_surface.py
python -m provenance_sensorium scan fixtures/sample_project
python -m provenance_sensorium receipt fixtures/sample_project --output receipt.json
python -m provenance_sensorium explain receipt.json
```

## Commands

- `sensorium scan PATH`
- `sensorium receipt PATH --output FILE`
- `sensorium explain RECEIPT`
- `sensorium init-fixture PATH`

All commands are local-only in v0.1.0.

## Public Boundary

This repository does not contain credentials, client data, private engagement
records, live target tooling, or private research corpus material. It ships
synthetic fixtures and public-safe abstractions.

## Status

v0.1.0 is a product seed: library, CLI, receipts, fixtures, tests, and release
gates. The product direction is live-state awareness for accountable AI research
workflows.
