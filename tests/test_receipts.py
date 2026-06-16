from pathlib import Path

from warden_sensorium.models import Status
from warden_sensorium.receipts import build_receipt, explain_receipt, receipt_from_json, receipt_to_json


def test_receipt_roundtrip_for_clean_fixture() -> None:
    receipt = build_receipt(Path("fixtures/sample_project"))
    text = receipt_to_json(receipt)
    loaded = receipt_from_json(text)
    assert loaded.root.endswith("fixtures/sample_project")
    assert all(decision.status is not Status.BLOCK for decision in loaded.decisions)


def test_explain_receipt_mentions_human_gate() -> None:
    receipt = build_receipt(Path("fixtures/sample_project"))
    explanation = explain_receipt(receipt)
    assert "WARDEN Sensorium Receipt" in explanation
    assert "Human gate" in explanation
