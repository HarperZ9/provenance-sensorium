from pathlib import Path

from provenance_sensorium.models import Status
from provenance_sensorium.receipts import (
    build_receipt,
    explain_receipt,
    human_gap_requests,
    receipt_from_json,
    receipt_to_json,
)


def test_receipt_roundtrip_for_clean_fixture() -> None:
    receipt = build_receipt(Path("fixtures/sample_project"))
    text = receipt_to_json(receipt)
    loaded = receipt_from_json(text)
    assert loaded.root.endswith("fixtures/sample_project")
    assert all(decision.status is not Status.BLOCK for decision in loaded.decisions)


def test_explain_receipt_mentions_human_gate() -> None:
    receipt = build_receipt(Path("fixtures/sample_project"))
    explanation = explain_receipt(receipt)
    assert "Provenance Sensorium Receipt" in explanation
    assert "Human gate" in explanation


def test_human_gap_requests_extracts_gate_payloads(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "Claim: AI can sign authorship attestation\n",
        encoding="utf-8",
    )

    receipt = build_receipt(tmp_path)
    gaps = human_gap_requests(receipt)
    explanation = explain_receipt(receipt)

    assert len(gaps) == 1
    assert gaps[0]["requires_human_act"] is True
    assert gaps[0]["act_kind"] == "authorship_attestation"
    assert gaps[0]["operator_attested"] is False
    assert len(gaps[0]["evidence_digest"]) == 64
    assert "Human-gap payloads" in explanation
