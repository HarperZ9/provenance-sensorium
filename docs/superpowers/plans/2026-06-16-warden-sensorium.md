# WARDEN Sensorium Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and release WARDEN Sensorium, a public-safe live-state awareness and provenance framework for AI-assisted research/security work.

**Architecture:** The package is a local-only Python CLI and library. Sensors create structured observations with provenance; exception layers classify observations; receipts preserve the chain from source state to decision; human gates mark claims that require human ownership.

**Tech Stack:** Python 3.9+, standard library, pytest, setuptools, GitHub Releases, static GitHub Pages promotion.

---

## File Structure

- Create `src/warden_sensorium/models.py`: status enums, provenance, observation, decision, receipt dataclasses.
- Create `src/warden_sensorium/sensors.py`: file, git, claim, secret-shape, fixture sensors.
- Create `src/warden_sensorium/layers.py`: secret, boundary, claim, and human-gate exception layers.
- Create `src/warden_sensorium/receipts.py`: receipt assembly, JSON output, Markdown explanation.
- Create `src/warden_sensorium/cli.py`: `scan`, `receipt`, `explain`, and `init-fixture` commands.
- Create `src/warden_sensorium/public_surface.py`: release hygiene checks.
- Create `src/warden_sensorium/__main__.py`: module entrypoint.
- Modify `src/warden_sensorium/__init__.py`: package exports.
- Create `scripts/check_public_surface.py`: repo-level gate wrapper.
- Create `fixtures/sample_project/`: synthetic clean fixture.
- Create `tests/`: focused tests for models, sensors, layers, receipts, CLI, and public-surface checks.
- Create `README.md`, `LICENSE`, `pyproject.toml`, `.github/workflows/tests.yml`, and `project-docs/public-boundary.md`.

## Task 1: Project Metadata And Package Skeleton

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `pyproject.toml`
- Create: `src/warden_sensorium/__init__.py`
- Create: `src/warden_sensorium/__main__.py`
- Create: `.github/workflows/tests.yml`
- Create: `project-docs/public-boundary.md`

- [ ] **Step 1: Write package metadata**

Create `pyproject.toml` with package name `warden-sensorium`, version `0.1.0`, Python `>=3.9`, console script `sensorium`, and pytest config pointing at `tests`.

- [ ] **Step 2: Add public README**

Write `README.md` that states the product boundary, quickstart commands, core concepts, and release gates.

- [ ] **Step 3: Add license and boundary docs**

Add MIT license and a public-boundary document that explicitly excludes `warden-ops`, credentials, client data, private corpus, and live target tooling.

- [ ] **Step 4: Add package entrypoints**

Create empty exports in `__init__.py` and route `python -m warden_sensorium` to `cli.main`.

- [ ] **Step 5: Add CI workflow**

Create a GitHub Actions workflow that installs the package, runs pytest, runs the public-surface gate, and scans the fixture.

- [ ] **Step 6: Commit**

Run:

```powershell
git add README.md LICENSE pyproject.toml src/warden_sensorium/__init__.py src/warden_sensorium/__main__.py .github/workflows/tests.yml project-docs/public-boundary.md
git commit -m "chore: scaffold WARDEN Sensorium package"
```

## Task 2: Core Models

**Files:**
- Create: `src/warden_sensorium/models.py`
- Create: `tests/test_models.py`
- Modify: `src/warden_sensorium/__init__.py`

- [ ] **Step 1: Write model tests**

Test that `Status` values include `pass`, `warn`, `block`, `needs-human`, and `unverified`; test that `Provenance.digest_text("abc")` is stable; test that receipts serialize to dictionaries with observations and decisions.

- [ ] **Step 2: Run model tests and confirm failure**

Run:

```powershell
python -m pytest tests/test_models.py -v
```

Expected: import failure for missing `warden_sensorium.models`.

- [ ] **Step 3: Implement models**

Implement dataclasses:

- `Status`
- `Provenance`
- `Observation`
- `Decision`
- `Receipt`

Each dataclass gets `to_dict()`. `Provenance` gets `digest_text()` and `from_text()`.

- [ ] **Step 4: Export models**

Update `__init__.py` to export the model classes.

- [ ] **Step 5: Verify**

Run:

```powershell
python -m pytest tests/test_models.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add src/warden_sensorium/models.py src/warden_sensorium/__init__.py tests/test_models.py
git commit -m "feat: add sensorium evidence models"
```

## Task 3: Sensors

**Files:**
- Create: `src/warden_sensorium/sensors.py`
- Create: `tests/test_sensors.py`
- Create: `fixtures/sample_project/README.md`
- Create: `fixtures/sample_project/EVIDENCE.md`

- [ ] **Step 1: Write sensor tests**

Cover file hashing, non-git fallback, claim extraction from Markdown, secret-shape detection, and fixture scanning.

- [ ] **Step 2: Run sensor tests and confirm failure**

Run:

```powershell
python -m pytest tests/test_sensors.py -v
```

Expected: import failure for missing sensors.

- [ ] **Step 3: Implement sensors**

Implement:

- `FileSensor`
- `GitSensor`
- `ClaimSensor`
- `SecretShapeSensor`
- `FixtureSensor`
- `default_sensors()`

Sensors return observations only. They do not decide pass/fail.

- [ ] **Step 4: Add clean fixture**

Add a synthetic project with a README containing evidence-marked claims and no secrets.

- [ ] **Step 5: Verify**

Run:

```powershell
python -m pytest tests/test_sensors.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add src/warden_sensorium/sensors.py tests/test_sensors.py fixtures/sample_project
git commit -m "feat: add live-state sensors"
```

## Task 4: Exception Layers

**Files:**
- Create: `src/warden_sensorium/layers.py`
- Create: `tests/test_layers.py`

- [ ] **Step 1: Write layer tests**

Test that secret-shaped observations block, private-boundary paths block, unevidenced claims warn, evidence-marked claims pass, and authorship/authorization/attestation claims require human gate.

- [ ] **Step 2: Run layer tests and confirm failure**

Run:

```powershell
python -m pytest tests/test_layers.py -v
```

Expected: import failure for missing layers.

- [ ] **Step 3: Implement layers**

Implement:

- `SecretGuard`
- `BoundaryGuard`
- `ClaimGuard`
- `HumanGate`
- `DefaultExceptionStack`

Each layer returns zero or more decisions. Default stack runs all layers.

- [ ] **Step 4: Verify**

Run:

```powershell
python -m pytest tests/test_layers.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/warden_sensorium/layers.py tests/test_layers.py
git commit -m "feat: add exception layers"
```

## Task 5: Receipts And CLI

**Files:**
- Create: `src/warden_sensorium/receipts.py`
- Create: `src/warden_sensorium/cli.py`
- Modify: `src/warden_sensorium/__main__.py`
- Create: `tests/test_receipts.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write receipt and CLI tests**

Test receipt JSON roundtrip, Markdown explanation, clean fixture scan exit code 0, blocked synthetic secret exit code 1, and `init-fixture` output.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```powershell
python -m pytest tests/test_receipts.py tests/test_cli.py -v
```

Expected: import failure for missing receipts and CLI.

- [ ] **Step 3: Implement receipts**

Create functions:

- `build_receipt(path, sensors=None, stack=None)`
- `receipt_to_json(receipt)`
- `receipt_from_json(text)`
- `explain_receipt(receipt)`

- [ ] **Step 4: Implement CLI**

Use `argparse` with commands:

- `scan PATH`
- `receipt PATH --output FILE`
- `explain RECEIPT`
- `init-fixture PATH`

Return code 1 when any decision has status `block`; otherwise 0.

- [ ] **Step 5: Verify**

Run:

```powershell
python -m pytest tests/test_receipts.py tests/test_cli.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add src/warden_sensorium/receipts.py src/warden_sensorium/cli.py src/warden_sensorium/__main__.py tests/test_receipts.py tests/test_cli.py
git commit -m "feat: add receipts and CLI"
```

## Task 6: Public Surface Gate

**Files:**
- Create: `src/warden_sensorium/public_surface.py`
- Create: `scripts/check_public_surface.py`
- Create: `tests/test_public_surface.py`

- [ ] **Step 1: Write public-surface tests**

Test that the checker rejects `.env`, `warden-ops`, token-shaped values, and private contact/payment strings, while allowing the current public tree.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```powershell
python -m pytest tests/test_public_surface.py -v
```

Expected: import failure for missing public-surface checker.

- [ ] **Step 3: Implement checker**

Implement a file walker that skips `.git`, caches, build output, and bytecode; flags forbidden path fragments and forbidden text patterns.

- [ ] **Step 4: Add script wrapper**

`scripts/check_public_surface.py` imports the package from `src` and exits 1 if findings exist.

- [ ] **Step 5: Verify**

Run:

```powershell
python -m pytest tests/test_public_surface.py -v
python scripts/check_public_surface.py
```

Expected: tests pass and script exits 0.

- [ ] **Step 6: Commit**

```powershell
git add src/warden_sensorium/public_surface.py scripts/check_public_surface.py tests/test_public_surface.py
git commit -m "feat: add public surface gate"
```

## Task 7: Full Verification, Publish, Release, Promote

**Files:**
- Modify: `C:\Users\Zain\harperz9.github.io\index.html`
- Modify: `C:\Users\Zain\harperz9.github.io\warden.html`

- [ ] **Step 1: Run full local gates**

Run:

```powershell
python -m pytest
python scripts/check_public_surface.py
python -m warden_sensorium scan fixtures/sample_project
python -m build
```

Expected: tests pass, public gate passes, fixture scan exits 0, build creates sdist/wheel.

- [ ] **Step 2: Publish GitHub repo**

Run:

```powershell
gh repo create HarperZ9/warden-sensorium --public --description "Live-state awareness and provenance framework for AI-assisted research and security work." --source . --remote origin --push
```

- [ ] **Step 3: Create release**

Run:

```powershell
gh release create v0.1.0 --repo HarperZ9/warden-sensorium --target main --title "WARDEN Sensorium v0.1.0" --notes-file RELEASE_NOTES.md
```

- [ ] **Step 4: Promote on portfolio**

Update the live site to list WARDEN Sensorium as a major product under WARDEN / AI safety / live-state awareness, not a small utility.

- [ ] **Step 5: Verify live public state**

Use GitHub metadata and Browser/Playwright snapshots to verify the repo, release, and site links are live.

- [ ] **Step 6: Commit and push site promotion**

Commit site edits and push `HarperZ9.github.io`.
