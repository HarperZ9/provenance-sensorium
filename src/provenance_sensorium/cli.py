from __future__ import annotations

from pathlib import Path
import argparse
import sys

from .models import Status
from .receipts import build_receipt, explain_receipt, receipt_from_json, receipt_to_json


FIXTURE_README = """# Sensorium Sample Project

Claim: [evidence:tests] The sample project has a clean public release surface.
Claim: [evidence:receipt] Sensorium can produce a local provenance receipt.
"""

FIXTURE_EVIDENCE = """# Evidence

- tests: `python -m pytest`
- receipt: `python -m provenance_sensorium receipt fixtures/sample_project --output receipt.json`
"""


def has_block(receipt) -> bool:
    return any(decision.status is Status.BLOCK for decision in receipt.decisions)


def cmd_scan(args: argparse.Namespace) -> int:
    receipt = build_receipt(Path(args.path))
    print(explain_receipt(receipt), end="")
    return 1 if has_block(receipt) else 0


def cmd_receipt(args: argparse.Namespace) -> int:
    receipt = build_receipt(Path(args.path))
    Path(args.output).write_text(receipt_to_json(receipt), encoding="utf-8")
    return 1 if has_block(receipt) else 0


def cmd_explain(args: argparse.Namespace) -> int:
    receipt = receipt_from_json(Path(args.receipt).read_text(encoding="utf-8"))
    print(explain_receipt(receipt), end="")
    # Surface BLOCK decisions in the exit code, like scan/receipt -- a CI step
    # running `explain` on a stored receipt must fail-closed, not always exit 0.
    return 1 if has_block(receipt) else 0


def cmd_init_fixture(args: argparse.Namespace) -> int:
    target = Path(args.path)
    target.mkdir(parents=True, exist_ok=True)
    (target / "README.md").write_text(FIXTURE_README, encoding="utf-8")
    (target / "EVIDENCE.md").write_text(FIXTURE_EVIDENCE, encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Provenance Sensorium local awareness and provenance CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan a local path")
    scan.add_argument("path")
    scan.set_defaults(func=cmd_scan)

    receipt = subparsers.add_parser("receipt", help="write a JSON receipt")
    receipt.add_argument("path")
    receipt.add_argument("--output", required=True)
    receipt.set_defaults(func=cmd_receipt)

    explain = subparsers.add_parser("explain", help="explain a JSON receipt")
    explain.add_argument("receipt")
    explain.set_defaults(func=cmd_explain)

    init_fixture = subparsers.add_parser("init-fixture", help="create a synthetic fixture project")
    init_fixture.add_argument("path")
    init_fixture.set_defaults(func=cmd_init_fixture)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
