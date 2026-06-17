from provenance_sensorium.models import Decision, Observation, Provenance, Receipt, Status


def test_status_values_are_stable() -> None:
    assert [status.value for status in Status] == [
        "pass",
        "warn",
        "block",
        "needs-human",
        "unverified",
    ]


def test_provenance_digest_text_is_stable() -> None:
    digest = Provenance.digest_text("abc")
    assert digest == "sha256:ba7816bf8f01cfea414140de5dae2223"


def test_receipt_serializes_observations_and_decisions() -> None:
    provenance = Provenance.from_text(source="fixture.txt", text="hello", confidence="high")
    observation = Observation(
        sensor="file",
        subject="fixture.txt",
        summary="read fixture",
        status=Status.PASS,
        provenance=provenance,
        data={"bytes": 5},
    )
    decision = Decision(
        layer="claim",
        status=Status.PASS,
        subject="fixture.txt",
        reason="evidence marker present",
        provenance=provenance,
    )
    receipt = Receipt(root="fixture", observations=[observation], decisions=[decision])
    rendered = receipt.to_dict()
    assert rendered["root"] == "fixture"
    assert rendered["observations"][0]["data"]["bytes"] == 5
    assert rendered["decisions"][0]["status"] == "pass"
