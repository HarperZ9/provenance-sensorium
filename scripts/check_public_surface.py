from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warden_sensorium.public_surface import check_public_surface  # noqa: E402


def main() -> int:
    findings = check_public_surface(ROOT)
    for finding in findings:
        print(f"{finding.path}: {finding.code}: {finding.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
