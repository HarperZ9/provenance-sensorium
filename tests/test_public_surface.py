from pathlib import Path

from warden_sensorium.public_surface import check_public_surface


def test_current_repo_public_surface_passes() -> None:
    findings = check_public_surface(Path("."))
    assert findings == []


def test_public_surface_rejects_env_file(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=value\n", encoding="utf-8")
    findings = check_public_surface(tmp_path)
    assert any(finding.code == "private-path" for finding in findings)


def test_public_surface_rejects_warden_ops_path(tmp_path: Path) -> None:
    private = tmp_path / "warden-ops"
    private.mkdir()
    (private / "README.md").write_text("private", encoding="utf-8")
    findings = check_public_surface(tmp_path)
    assert any(finding.code == "private-path" for finding in findings)


def test_public_surface_rejects_secret_shape(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")
    findings = check_public_surface(tmp_path)
    assert any(finding.code == "secret-shape" for finding in findings)
