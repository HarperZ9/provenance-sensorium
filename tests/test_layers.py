from warden_sensorium.layers import BoundaryGuard, ClaimGuard, DefaultExceptionStack, HumanGate, SecretGuard
from warden_sensorium.models import Observation, Provenance, Status


def obs(sensor: str, subject: str, summary: str, data: dict[str, str] | None = None) -> Observation:
    return Observation(
        sensor=sensor,
        subject=subject,
        summary=summary,
        status=Status.PASS,
        provenance=Provenance.from_text(source=subject, text=summary, confidence="high"),
        data=data or {},
    )


def test_secret_guard_blocks_secret_shape_observation() -> None:
    observation = obs("secret-shape", "README.md", "secret-like text", {"pattern": "secret"})
    decisions = SecretGuard().evaluate([observation])
    assert decisions[0].status is Status.BLOCK


def test_boundary_guard_blocks_private_paths() -> None:
    observation = obs("file", "private/warden-ops/runbook.md", "file")
    decisions = BoundaryGuard().evaluate([observation])
    assert decisions[0].status is Status.BLOCK


def test_claim_guard_warns_without_evidence_marker() -> None:
    observation = obs("claim", "README.md", "Claim: system is verified", {"claim": "system is verified"})
    decisions = ClaimGuard().evaluate([observation])
    assert decisions[0].status is Status.WARN


def test_claim_guard_passes_evidence_marked_claim() -> None:
    observation = obs("claim", "README.md", "Claim", {"claim": "[evidence:tests] system passes"})
    decisions = ClaimGuard().evaluate([observation])
    assert decisions[0].status is Status.PASS


def test_human_gate_marks_attestation_as_needs_human() -> None:
    observation = obs("claim", "README.md", "Claim", {"claim": "AI can sign authorship attestation"})
    decisions = HumanGate().evaluate([observation])
    assert decisions[0].status is Status.NEEDS_HUMAN


def test_default_stack_runs_multiple_layers() -> None:
    observation = obs("claim", ".env", "Claim", {"claim": "authorization is approved"})
    statuses = [decision.status for decision in DefaultExceptionStack().evaluate([observation])]
    assert Status.BLOCK in statuses
    assert Status.NEEDS_HUMAN in statuses
