"""Canonical secret-shape patterns — one source of truth for the file sensor and
the public-surface scanner, so the two never drift apart.

Each pattern literal is assembled from split fragments so that THIS module's own
source does not match any of them.  That removes the need for a fragile,
hard-coded "skip my own file" path exemption: the scanner can scan this file
(and the sensors that import it) without false positives.

Credential patterns and PII patterns are kept separate: a phone number is a
public-surface (pre-release) concern, not a "secret" the file sensor warns on.
"""

from __future__ import annotations

import re

# Fragments split so the source below never self-matches its own regex.
_SK = "sk" + "-"
_GH = "(?:ghp|gho|ghu|ghs|ghr)" + "_"
_GH_PAT = "github" + "_pat_"
_AKIA = "AK" + "IA"
_JWT = "ey" + "J"

# (label, compiled pattern). label is stable and surfaced in observation data.
SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("credential", re.compile(r"(?i)\b(api[_-]?key|password|bearer)\b\s*[:=]\s*\S+")),
    ("openai-key", re.compile(_SK + r"[A-Za-z0-9_-]{20,}")),
    ("github-token", re.compile(r"\b" + _GH + r"[A-Za-z0-9]{36}\b")),
    ("github-pat", re.compile(r"\b" + _GH_PAT + r"[A-Za-z0-9_]{22,}")),
    ("aws-access-key", re.compile(r"\b" + _AKIA + r"[0-9A-Z]{16}\b")),
    ("pem-private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\b" + _JWT + r"[A-Za-z0-9_-]{8,}\.ey" + "J" + r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
]

# PII / private-contact shapes — public-surface scanner only.
PII_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("phone", re.compile(r"\b\d{3}[-.) ]?\d{3}[- ]?\d{4}\b")),
]


def first_secret_match(text: str) -> str | None:
    """Return the label of the first secret pattern that matches, else None."""
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return label
    return None


def first_secret_or_pii_match(text: str) -> str | None:
    """Secret patterns first, then PII patterns.  Label or None."""
    label = first_secret_match(text)
    if label is not None:
        return label
    for label, pattern in PII_PATTERNS:
        if pattern.search(text):
            return label
    return None
