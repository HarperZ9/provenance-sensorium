from __future__ import annotations

import re

from .models import Decision, Observation, Provenance, Status


PRIVATE_PATH_FRAGMENTS = [
    ".env",
    "warden-ops",
    "private-corpus",
    "client-data",
    "customer-data",
    "signed-corpus",
]
# Word-boundary patterns (text is lowercased before matching). This catches
# word-final and inflected forms ("signed", "signature", "signing") that a
# trailing-space substring missed, while NOT firing on "design" (no boundary
# before "sign").
_HUMAN_GATE_PATTERNS = [
    re.compile(r"\bauthorship\b"),
    re.compile(r"\bauthorization\b"),
    re.compile(r"\battestation\b"),
    re.compile(r"\bcountersign(?:ed|ing|ature)?\b"),
    re.compile(r"\bsign(?:ed|ing|ature|atory)?\b"),
]


def _act_kind(text: str) -> str:
    if "authorship" in text:
        return "authorship_attestation"
    if "authorization" in text:
        return "authorization_attestation"
    if "attestation" in text:
        return "attestation"
    return "signature_attestation"


def _digest_hex(provenance: Provenance) -> str:
    if provenance.digest.startswith("sha256:"):
        return provenance.digest.removeprefix("sha256:")
    return provenance.digest


def _human_gap_payload(observation: Observation, text: str) -> dict[str, object]:
    return {
        "requires_human_act": True,
        "act_kind": _act_kind(text),
        "evidence_label": f"{observation.sensor}:{observation.subject}",
        "evidence_digest": _digest_hex(observation.provenance),
        "operator_attested": False,
    }


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
            if any(pattern.search(text) for pattern in _HUMAN_GATE_PATTERNS):
                decisions.append(
                    Decision(
                        layer=self.name,
                        status=Status.NEEDS_HUMAN,
                        subject=observation.subject,
                        reason="authorship, authorization, or attestation requires a human gate",
                        provenance=observation.provenance,
                        human_gap=_human_gap_payload(observation, text),
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
