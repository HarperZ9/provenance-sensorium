from __future__ import annotations

from pathlib import Path
import json
from typing import Any

from .layers import DefaultExceptionStack
from .models import Receipt
from .sensors import default_sensors


def build_receipt(
    path: Path,
    sensors: list[object] | None = None,
    stack: DefaultExceptionStack | None = None,
) -> Receipt:
    active_sensors = sensors or default_sensors()
    observations = []
    for sensor in active_sensors:
        observations.extend(sensor.observe(path))
    decisions = (stack or DefaultExceptionStack()).evaluate(observations)
    return Receipt(root=path.as_posix(), observations=observations, decisions=decisions)


def receipt_to_json(receipt: Receipt) -> str:
    return json.dumps(receipt.to_dict(), indent=2, sort_keys=True) + "\n"


def receipt_from_json(text: str) -> Receipt:
    return Receipt.from_dict(json.loads(text))


def human_gap_requests(receipt: Receipt) -> list[dict[str, Any]]:
    return [
        dict(decision.human_gap)
        for decision in receipt.decisions
        if decision.human_gap is not None
    ]


def explain_receipt(receipt: Receipt) -> str:
    lines = [
        "# Provenance Sensorium Receipt",
        "",
        f"Root: `{receipt.root}`",
        f"Observations: {len(receipt.observations)}",
        f"Decisions: {len(receipt.decisions)}",
        "",
        "## Decisions",
    ]
    if receipt.decisions:
        for decision in receipt.decisions:
            lines.append(
                f"- `{decision.status.value}` via `{decision.layer}` "
                f"on `{decision.subject}`: {decision.reason}"
            )
    else:
        lines.append("- `pass`: no exception layer emitted a finding")
    gaps = human_gap_requests(receipt)
    if gaps:
        lines.extend(["", "## Human-gap payloads"])
        for gap in gaps:
            lines.append(
                f"- `{gap['act_kind']}` on `{gap['evidence_label']}`: "
                "operator attestation required"
            )
    lines.extend(
        [
            "",
            "## Human gate",
            "",
            "Human authorization, authorship, and attestation remain explicit "
            "gates. The receipt prepares evidence; it does not sign the human act.",
        ]
    )
    return "\n".join(lines) + "\n"
