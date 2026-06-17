import os
from pathlib import Path

import pytest

from provenance_sensorium.models import Status
from provenance_sensorium.sensors import (
    ClaimSensor,
    FileSensor,
    GitSensor,
    SecretShapeSensor,
    iter_files,
)


def test_file_sensor_hashes_file(tmp_path: Path) -> None:
    sample = tmp_path / "README.md"
    sample.write_bytes(b"# Sample\n")
    observations = FileSensor().observe(sample)
    assert observations[0].sensor == "file"
    assert observations[0].status is Status.PASS
    assert observations[0].data["bytes"] == 9
    digest = observations[0].provenance.digest
    assert digest.startswith("sha256:")
    assert len(digest) == len("sha256:") + 64  # full-width SHA-256, not truncated


def test_git_sensor_handles_non_git_path(tmp_path: Path) -> None:
    observations = GitSensor().observe(tmp_path)
    assert observations[0].sensor == "git"
    assert observations[0].status is Status.UNVERIFIED
    assert "not a git repository" in observations[0].summary.lower()


def test_claim_sensor_extracts_markdown_claims(tmp_path: Path) -> None:
    sample = tmp_path / "README.md"
    sample.write_text("- Claim: [evidence:tests] fixture passes\n", encoding="utf-8")
    observations = ClaimSensor().observe(sample)
    assert observations[0].sensor == "claim"
    assert observations[0].data["claim"] == "[evidence:tests] fixture passes"
    # The sensor reports existence only; the PASS/WARN verdict is the guard's job.
    assert observations[0].status is Status.UNVERIFIED


def test_secret_shape_sensor_flags_token_text(tmp_path: Path) -> None:
    sample = tmp_path / "note.md"
    sample.write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")
    observations = SecretShapeSensor().observe(sample)
    assert observations[0].sensor == "secret-shape"
    assert observations[0].status is Status.WARN
    assert observations[0].data["pattern"] == "credential"


def test_secret_shape_sensor_flags_bare_sk_token(tmp_path: Path) -> None:
    # Regression: a bare sk- token with no 'api_key' on the line must NOT be
    # silently skipped (the old inverted content-based skip blinded the sensor).
    sample = tmp_path / "note.md"
    sample.write_text("leaked = sk-abcdefghijklmnopqrstuvwxyz1234\n", encoding="utf-8")
    observations = SecretShapeSensor().observe(sample)
    assert any(o.status is Status.WARN for o in observations)


def test_secret_shape_sensor_flags_github_token(tmp_path: Path) -> None:
    sample = tmp_path / "note.md"
    sample.write_text("ghp_" + "a" * 36 + "\n", encoding="utf-8")
    observations = SecretShapeSensor().observe(sample)
    assert any(o.data.get("pattern") == "github-token" for o in observations)


def test_iter_files_skips_symlinks(tmp_path: Path) -> None:
    real = tmp_path / "real.md"
    real.write_text("real\n", encoding="utf-8")
    link = tmp_path / "link.md"
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted in this environment")
    found = iter_files(tmp_path)
    assert real in found
    assert link not in found  # the symlink must not be traversed
