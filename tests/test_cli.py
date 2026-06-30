from pathlib import Path

from provenance_sensorium.cli import main


def test_scan_clean_fixture_returns_zero() -> None:
    assert main(["scan", "fixtures/sample_project"]) == 0


def test_scan_blocks_secret_file(tmp_path: Path) -> None:
    sample = tmp_path / "README.md"
    sample.write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")
    assert main(["scan", str(tmp_path)]) == 1


def test_receipt_and_explain_commands(tmp_path: Path) -> None:
    output = tmp_path / "receipt.json"
    assert main(["receipt", "fixtures/sample_project", "--output", str(output)]) == 0
    assert output.exists()
    assert main(["explain", str(output)]) == 0


def test_init_fixture_creates_sample(tmp_path: Path) -> None:
    target = tmp_path / "demo"
    assert main(["init-fixture", str(target)]) == 0
    assert (target / "README.md").exists()


def test_explain_surfaces_block_in_exit_code(tmp_path: Path) -> None:
    # A receipt that recorded a BLOCK must make `explain` exit non-zero too,
    # not always 0 -- fail-closed on the explain path.
    secret = tmp_path / "README.md"
    secret.write_text("api_key = sk-abcdefghijklmnopqrstuvwxyz\n", encoding="utf-8")
    output = tmp_path / "receipt.json"
    assert main(["receipt", str(tmp_path), "--output", str(output)]) == 1
    assert main(["explain", str(output)]) == 1
