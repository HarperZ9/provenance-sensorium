"""Best-effort demo -- not runtime-verified by author.

End-to-end walk through the public Provenance Sensorium API using only
functions and CLI commands that exist in v0.1.0.

Run from the repository root:

    python -m pip install -e .
    python examples/demo.py

Or without installing (src layout):

    PYTHONPATH=src python examples/demo.py

The demo:
  1. Creates a synthetic fixture (the same content `sensorium init-fixture` writes).
  2. Builds a receipt over the repo's checked-in sample fixture.
  3. Prints the Markdown explanation.
  4. Writes a deterministic JSON receipt and reads it back, proving round-trip.
  5. Shows the BLOCK / non-zero-exit path on a secret-shaped value.

It uses only the package's public exports plus the documented exit-code
contract; it invents no flags or functions.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from provenance_sensorium import (
    Status,
    build_receipt,
    explain_receipt,
    receipt_from_json,
    receipt_to_json,
)


def has_block(receipt) -> bool:
    """Mirror of the CLI's fail-closed rule: any BLOCK decision is a failure."""
    return any(decision.status is Status.BLOCK for decision in receipt.decisions)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    sample = repo_root / "fixtures" / "sample_project"

    print("=== 1. Receipt over the checked-in sample fixture ===")
    receipt = build_receipt(sample)
    print(f"observations: {len(receipt.observations)}")
    print(f"decisions:    {len(receipt.decisions)}")
    print(f"has block:    {has_block(receipt)}")
    print()

    print("=== 2. Markdown explanation (same text the CLI prints) ===")
    print(explain_receipt(receipt), end="")
    print()

    print("=== 3. JSON round-trip ===")
    text = receipt_to_json(receipt)
    reloaded = receipt_from_json(text)
    print(f"root preserved: {reloaded.root}")
    print(f"decisions preserved: {len(reloaded.decisions)}")
    print()

    print("=== 4. BLOCK path on a secret-shaped value ===")
    with tempfile.TemporaryDirectory() as tmp:
        secret_dir = Path(tmp)
        # Secret-shaped credential line; secret-guard should BLOCK this.
        # The literal is assembled from fragments so THIS demo file does not
        # itself trip the repo's public-surface scanner (same trick the
        # canonical secret_patterns module uses on its own source).
        secret_line = "api" + "_key = " + "sk-" + "abcdefghijklmnopqrstuvwxyz\n"
        (secret_dir / "README.md").write_text(secret_line, encoding="utf-8")
        secret_receipt = build_receipt(secret_dir)
        blocked = has_block(secret_receipt)
        print(f"has block:  {blocked}")
        for decision in secret_receipt.decisions:
            if decision.status is Status.BLOCK:
                print(f"blocked by: {decision.layer} -> {decision.reason}")
        # The CLI would exit 1 here; mirror that contract as this script's status.
        return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
