# Usage

Provenance Sensorium reads bounded local state (files, git, Markdown claims,
secret-shaped text, fixture completeness), classifies it through exception
layers, and emits a provenance receipt you can inspect before you publish, hand
off, or attest.

This guide covers the real CLI and library surface in v0.1.0. Output blocks
marked *illustrative* were produced by running the tool locally and are
reproduced here for reference; timestamps and absolute paths will differ on your
machine.

## Install

Requires Python 3.9 or newer. No third-party runtime dependencies.

```powershell
python -m pip install -e .
```

After install, the `sensorium` console script is available. Every example below
also works without installing, by running the package as a module:

```powershell
python -m provenance_sensorium <command> ...
```

## Commands

| Command | Purpose |
| --- | --- |
| `sensorium scan PATH` | Scan a path, print a Markdown receipt to stdout. |
| `sensorium receipt PATH --output FILE` | Scan a path, write a JSON receipt to `FILE`. |
| `sensorium explain RECEIPT` | Render a stored JSON receipt back to the Markdown explanation. |
| `sensorium init-fixture PATH` | Create a synthetic `README.md` + `EVIDENCE.md` fixture under `PATH`. |

Exit codes: `scan`, `receipt`, and `explain` return `1` when any decision is a
`block` (for example, a secret-shaped value), and `0` otherwise. This lets you
wire the tool into a release gate that fails closed. `init-fixture` always
returns `0` on success.

The `--output` flag on `receipt` is required. There are no other flags.

## Status values

Receipts use a fixed set of statuses: `pass`, `warn`, `block`, `needs-human`,
`unverified`. Observations carry the raw sensor status; decisions carry the
exception-layer verdict.

## Example 1 — scan a clean fixture

```powershell
python -m provenance_sensorium scan fixtures/sample_project
```

Output (illustrative):

```
# Provenance Sensorium Receipt

Root: `fixtures/sample_project`
Observations: 6
Decisions: 2

## Decisions
- `pass` via `claim-guard` on `fixtures\sample_project\README.md:3`: claim includes an evidence marker
- `pass` via `claim-guard` on `fixtures\sample_project\README.md:4`: claim includes an evidence marker

## Human gate

Human authorization, authorship, and attestation remain explicit gates. The receipt prepares evidence; it does not sign the human act.
```

The clean fixture exits `0`.

## Example 2 — scan a path that contains a secret

A path whose text contains a secret-shaped value (for example, a line of the
form `api_key` `=` `sk-<20+ characters>`, written here with spaces so this guide
does not trip the tool's own scanner) is blocked by the `secret-guard` layer:

```powershell
python -m provenance_sensorium scan ./some_dir
```

Output (illustrative):

```
# Provenance Sensorium Receipt

Root: `./some_dir`
Observations: 4
Decisions: 1

## Decisions
- `block` via `secret-guard` on `some_dir\README.md:1`: secret-shaped value requires removal before publication

## Human gate

Human authorization, authorship, and attestation remain explicit gates. The receipt prepares evidence; it does not sign the human act.
```

Because a decision is `block`, the command exits `1`.

## Example 3 — write and re-explain a JSON receipt

```powershell
python -m provenance_sensorium receipt fixtures/sample_project --output receipt.json
python -m provenance_sensorium explain receipt.json
```

`receipt.json` is deterministic JSON (sorted keys, two-space indent). Its
top-level shape is:

```json
{
  "decisions": [ ... ],
  "observations": [ ... ],
  "root": "fixtures/sample_project"
}
```

Each decision and observation carries a `provenance` block with `source`,
`digest` (full-width `sha256:` hash), `timestamp` (UTC ISO-8601), and
`confidence`. `explain` reads that JSON back and prints the same Markdown
explanation as `scan`. Running `explain` on a receipt that recorded a `block`
also exits `1`, so a stored receipt fails closed in CI.

## Example 4 — create a fixture, then use the library

Create a fresh synthetic fixture:

```powershell
python -m provenance_sensorium init-fixture ./demo_fixture
```

This writes `demo_fixture/README.md` and `demo_fixture/EVIDENCE.md`.

Build and inspect a receipt directly from Python:

```python
from pathlib import Path
from provenance_sensorium import build_receipt, explain_receipt, receipt_to_json

receipt = build_receipt(Path("fixtures/sample_project"))

print(len(receipt.observations))          # -> 6
print(len(receipt.decisions))             # -> 2
print(receipt.decisions[0].status.value)  # -> "pass"

# Markdown explanation (same text the CLI prints):
print(explain_receipt(receipt))

# Deterministic JSON, suitable for committing as evidence:
Path("receipt.json").write_text(receipt_to_json(receipt), encoding="utf-8")
```

The public library surface is exported from the package root:

```python
from provenance_sensorium import (
    Decision, Observation, Provenance, Receipt, Status,
    build_receipt, explain_receipt, receipt_from_json, receipt_to_json,
)
```

`build_receipt(path, sensors=None, stack=None)` accepts optional custom sensor
and exception-stack objects; omitting them uses the default sensor set
(`file`, `git`, `claim`, `secret-shape`, `fixture`) and the default exception
stack (`secret-guard`, `boundary-guard`, `claim-guard`, `human-gate`).

## Human gate

Every receipt ends with a human-gate note. The tool prepares evidence; it does
not, and cannot, sign the human act of authorship, authorization, or
attestation for you. Treat `needs-human` decisions as work that requires a
person to own.
