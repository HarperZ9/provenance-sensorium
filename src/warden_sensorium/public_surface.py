from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import fnmatch
import re


SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build", "*.egg-info"}
TEXT_SUFFIXES = {".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".py"}
FORBIDDEN_PATHS = [".env", "warden-ops", "private-corpus", "client-data", "customer-data", "signed-corpus"]
SECRET_TEXT = [
    re.compile(r"(?i)\b(api[_-]?key|password|bearer)\b\s*[:=]\s*\S+"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\b\d{3}[-.) ]?\d{3}[- ]?\d{4}\b"),
]


@dataclass(frozen=True)
class PublicSurfaceFinding:
    path: Path
    code: str
    message: str


def gitignore_patterns(root: Path) -> list[str]:
    ignore = root / ".gitignore"
    if not ignore.exists():
        return []
    patterns: list[str] = []
    for line in ignore.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("!"):
            patterns.append(stripped.rstrip("/"))
    return patterns


def is_ignored(path: Path, root: Path, patterns: list[str]) -> bool:
    rel = path.relative_to(root).as_posix()
    name = path.name
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern):
            return True
    return False


def iter_public_files(root: Path) -> list[Path]:
    patterns = gitignore_patterns(root)
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS or part.endswith(".egg-info") for part in rel_parts):
            continue
        if is_ignored(path, root, patterns):
            continue
        if path.is_file():
            files.append(path)
    return files


def check_public_surface(root: Path) -> list[PublicSurfaceFinding]:
    root = root.resolve()
    findings: list[PublicSurfaceFinding] = []
    for path in iter_public_files(root):
        rel = path.relative_to(root)
        rel_text = rel.as_posix().lower()
        if any(fragment in rel_text for fragment in FORBIDDEN_PATHS):
            findings.append(PublicSurfaceFinding(rel, "private-path", "path is outside public boundary"))
            continue
        if rel.parts and rel.parts[0] == "tests":
            continue
        if rel.as_posix() in {"src/warden_sensorium/public_surface.py", "src/warden_sensorium/sensors.py"}:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_TEXT:
            if pattern.search(text):
                findings.append(PublicSurfaceFinding(rel, "secret-shape", "secret or private-contact shaped text"))
                break
    return findings
