from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

from .secret_patterns import first_secret_or_pii_match


SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build", "*.egg-info"}
TEXT_SUFFIXES = {".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".py"}
FORBIDDEN_PATHS = [".env", "warden-ops", "private-corpus", "client-data", "customer-data", "signed-corpus"]


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
        if path.is_symlink():
            continue  # never follow symlinks out of the tree
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
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if first_secret_or_pii_match(text) is not None:
            findings.append(
                PublicSurfaceFinding(rel, "secret-shape", "secret or private-contact shaped text")
            )
    return findings
