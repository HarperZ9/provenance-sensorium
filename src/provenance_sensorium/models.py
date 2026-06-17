from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Any


class Status(Enum):
    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"
    NEEDS_HUMAN = "needs-human"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class Provenance:
    source: str
    digest: str
    timestamp: str
    confidence: str
    command: str | None = None

    @staticmethod
    def digest_text(text: str) -> str:
        # Full-width SHA-256 — the digest is the re-derivable trust anchor, so it
        # must be the whole hash, never truncated.
        return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def from_text(
        cls,
        source: str,
        text: str,
        confidence: str,
        command: str | None = None,
    ) -> "Provenance":
        return cls(
            source=source,
            digest=cls.digest_text(text),
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=confidence,
            command=command,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "source": self.source,
            "digest": self.digest,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }
        if self.command:
            data["command"] = self.command
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Provenance":
        return cls(
            source=str(data["source"]),
            digest=str(data["digest"]),
            timestamp=str(data["timestamp"]),
            confidence=str(data["confidence"]),
            command=data.get("command"),
        )


@dataclass(frozen=True)
class Observation:
    sensor: str
    subject: str
    summary: str
    status: Status
    provenance: Provenance
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sensor": self.sensor,
            "subject": self.subject,
            "summary": self.summary,
            "status": self.status.value,
            "provenance": self.provenance.to_dict(),
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Observation":
        return cls(
            sensor=str(data["sensor"]),
            subject=str(data["subject"]),
            summary=str(data["summary"]),
            status=Status(str(data["status"])),
            provenance=Provenance.from_dict(data["provenance"]),
            data=dict(data.get("data", {})),
        )


@dataclass(frozen=True)
class Decision:
    layer: str
    status: Status
    subject: str
    reason: str
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "status": self.status.value,
            "subject": self.subject,
            "reason": self.reason,
            "provenance": self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Decision":
        return cls(
            layer=str(data["layer"]),
            status=Status(str(data["status"])),
            subject=str(data["subject"]),
            reason=str(data["reason"]),
            provenance=Provenance.from_dict(data["provenance"]),
        )


@dataclass(frozen=True)
class Receipt:
    root: str
    observations: list[Observation]
    decisions: list[Decision]

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "observations": [observation.to_dict() for observation in self.observations],
            "decisions": [decision.to_dict() for decision in self.decisions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Receipt":
        return cls(
            root=str(data["root"]),
            observations=[Observation.from_dict(item) for item in data.get("observations", [])],
            decisions=[Decision.from_dict(item) for item in data.get("decisions", [])],
        )
