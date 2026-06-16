from pathlib import Path

from warden_sensorium.models import Status
from warden_sensorium.sensors import ClaimSensor, FileSensor, GitSensor, SecretShapeSensor


def test_file_sensor_hashes_file(tmp_path: Path) -> None:
    sample = tmp_path / "README.md"
    sample.write_bytes(b"# Sample\n")
    observations = FileSensor().observe(sample)
    assert observations[0].sensor == "file"
    assert observations[0].status is Status.PASS
    assert observations[0].data["bytes"] == 9
    assert observations[0].provenance.digest.startswith("sha256:")


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


def test_secret_shape_sensor_flags_token_text(tmp_path: Path) -> None:
    sample = tmp_path / "note.md"
    sample.write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")
    observations = SecretShapeSensor().observe(sample)
    assert observations[0].sensor == "secret-shape"
    assert observations[0].status is Status.WARN
    assert observations[0].data["pattern"] == "secret"
