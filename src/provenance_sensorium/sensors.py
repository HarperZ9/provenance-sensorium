from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .models import Observation, Provenance, Status


TEXT_SUFFIXES = {".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".py"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build"}
SECRET_PATTERNS = [
    ("secret", re.compile(r"(?i)\b(api[_-]?key|password|bearer)\b\s*[:=]\s*\S+")),
    ("secret", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
]


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    files: list[Path] = []
    for child in sorted(path.rglob("*")):
        if child.is_dir():
            continue
        if any(part in SKIP_DIRS for part in child.parts):
            continue
        files.append(child)
    return files


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


class FileSensor:
    name = "file"

    def observe(self, path: Path) -> list[Observation]:
        observations: list[Observation] = []
        for file_path in iter_files(path):
            try:
                payload = file_path.read_bytes()
            except OSError as exc:
                text = f"unreadable: {exc}"
                observations.append(
                    Observation(
                        sensor=self.name,
                        subject=str(file_path),
                        summary=text,
                        status=Status.UNVERIFIED,
                        provenance=Provenance.from_text(str(file_path), text, "low"),
                    )
                )
                continue
            digest = "sha256:" + __import__("hashlib").sha256(payload).hexdigest()[:32]
            observations.append(
                Observation(
                    sensor=self.name,
                    subject=str(file_path),
                    summary="file observed",
                    status=Status.PASS,
                    provenance=Provenance(
                        source=str(file_path),
                        digest=digest,
                        timestamp=Provenance.from_text(str(file_path), "", "high").timestamp,
                        confidence="high",
                    ),
                    data={"bytes": len(payload)},
                )
            )
        return observations


class GitSensor:
    name = "git"

    def observe(self, path: Path) -> list[Observation]:
        root = (path if path.is_dir() else path.parent).resolve()
        cmd = ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"]
        probe = subprocess.run(cmd, capture_output=True, text=True)
        if probe.returncode != 0:
            text = "not a git repository"
            return [
                Observation(
                    sensor=self.name,
                    subject=str(root),
                    summary=text,
                    status=Status.UNVERIFIED,
                    provenance=Provenance.from_text(str(root), text, "medium", " ".join(cmd)),
                )
            ]
        top_level = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if Path(top_level).resolve() != root:
            text = "not a git repository root"
            return [
                Observation(
                    sensor=self.name,
                    subject=str(root),
                    summary=text,
                    status=Status.UNVERIFIED,
                    provenance=Provenance.from_text(str(root), text, "medium", "git rev-parse --show-toplevel"),
                )
            ]
        branch = subprocess.run(
            ["git", "-C", str(root), "branch", "--show-current"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        text = f"branch={branch}; commit={commit}; dirty={len(status)}"
        return [
            Observation(
                sensor=self.name,
                subject=str(root),
                summary=text,
                status=Status.PASS,
                provenance=Provenance.from_text(str(root), text, "high", "git status --porcelain"),
                data={"branch": branch, "commit": commit, "dirty": len(status)},
            )
        ]


class ClaimSensor:
    name = "claim"

    def observe(self, path: Path) -> list[Observation]:
        observations: list[Observation] = []
        for file_path in iter_files(path):
            text = read_text(file_path)
            if text is None:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                match = re.match(r"^(?:[-*]\s*)?Claim:\s*(.+)$", stripped, re.IGNORECASE)
                if not match:
                    continue
                claim = match.group(1).strip()
                observations.append(
                    Observation(
                        sensor=self.name,
                        subject=f"{file_path}:{line_no}",
                        summary="claim observed",
                        status=Status.PASS,
                        provenance=Provenance.from_text(str(file_path), line, "high"),
                        data={"claim": claim},
                    )
                )
        return observations


class SecretShapeSensor:
    name = "secret-shape"

    def observe(self, path: Path) -> list[Observation]:
        observations: list[Observation] = []
        for file_path in iter_files(path):
            text = read_text(file_path)
            if text is None:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if "sk-abcdefghijklmnopqrstuvwxyz" in line and "api_key" not in line.lower():
                    continue
                for label, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        observations.append(
                            Observation(
                                sensor=self.name,
                                subject=f"{file_path}:{line_no}",
                                summary="secret-shaped text observed",
                                status=Status.WARN,
                                provenance=Provenance.from_text(str(file_path), line, "high"),
                                data={"pattern": label},
                            )
                        )
                        break
        return observations


class FixtureSensor:
    name = "fixture"

    def observe(self, path: Path) -> list[Observation]:
        required = ["README.md", "EVIDENCE.md"]
        missing = [name for name in required if not (path / name).exists()]
        status = Status.PASS if not missing else Status.WARN
        text = "fixture complete" if not missing else "fixture missing: " + ", ".join(missing)
        return [
            Observation(
                sensor=self.name,
                subject=str(path),
                summary=text,
                status=status,
                provenance=Provenance.from_text(str(path), text, "high"),
                data={"missing": missing},
            )
        ]


def default_sensors() -> list[object]:
    return [FileSensor(), GitSensor(), ClaimSensor(), SecretShapeSensor(), FixtureSensor()]
