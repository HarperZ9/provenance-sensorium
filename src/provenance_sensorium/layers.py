from __future__ import annotations

from .models import Decision, Observation, Provenance, Status


PRIVATE_PATH_FRAGMENTS = [
    ".env",
    "warden-ops",
    "private-corpus",
    "client-data",
    "customer-data",
    "signed-corpus",
]
HUMAN_GATE_TERMS = ["authorship", "authorization", "attestation", "sign ", "signed "]


class SecretGuard:
    name = "secret-guard"

    def evaluate(self, observations: list[Observation]) -> list[Decision]:
        return [
            Decision(
                layer=self.name,
                status=Status.BLOCK,
                subject=observation.subject,
                reason="secret-shaped value requires removal before publication",
                provenance=observation.provenance,
            )
            for observation in observations
            if observation.sensor == "secret-shape"
        ]


class BoundaryGuard:
    name = "boundary-guard"

    def evaluate(self, observations: list[Observation]) -> list[Decision]:
        decisions: list[Decision] = []
        for observation in observations:
            subject = observation.subject.replace("\\", "/").lower()
            if any(fragment in subject for fragment in PRIVATE_PATH_FRAGMENTS):
                decisions.append(
                    Decision(
                        layer=self.name,
                        status=Status.BLOCK,
                        subject=observation.subject,
                        reason="path is outside the public release boundary",
                        provenance=observation.provenance,
                    )
                )
        return decisions


class ClaimGuard:
    name = "claim-guard"

    def evaluate(self, observations: list[Observation]) -> list[Decision]:
        decisions: list[Decision] = []
        for observation in observations:
            if observation.sensor != "claim":
                continue
            claim = str(observation.data.get("claim", ""))
            if "[evidence:" in claim.lower():
                status = Status.PASS
                reason = "claim includes an evidence marker"
            else:
                status = Status.WARN
                reason = "claim lacks an evidence marker"
            decisions.append(
                Decision(
                    layer=self.name,
                    status=status,
                    subject=observation.subject,
                    reason=reason,
                    provenance=observation.provenance,
                )
            )
        return decisions


class HumanGate:
    name = "human-gate"

    def evaluate(self, observations: list[Observation]) -> list[Decision]:
        decisions: list[Decision] = []
        for observation in observations:
            text = (observation.summary + " " + str(observation.data)).lower()
            if any(term in text for term in HUMAN_GATE_TERMS):
                decisions.append(
                    Decision(
                        layer=self.name,
                        status=Status.NEEDS_HUMAN,
                        subject=observation.subject,
                        reason="authorship, authorization, or attestation requires a human gate",
                        provenance=observation.provenance,
                    )
                )
        return decisions


class DefaultExceptionStack:
    def __init__(self) -> None:
        self.layers = [SecretGuard(), BoundaryGuard(), ClaimGuard(), HumanGate()]

    def evaluate(self, observations: list[Observation]) -> list[Decision]:
        decisions: list[Decision] = []
        for layer in self.layers:
            decisions.extend(layer.evaluate(observations))
        return decisions
