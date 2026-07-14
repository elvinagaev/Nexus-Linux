from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_debian_packaging_metadata_exists():
    control = REPO_ROOT / "debian" / "control"
    rules = REPO_ROOT / "debian" / "rules"
    changelog = REPO_ROOT / "debian" / "changelog"

    assert control.exists(), "debian/control is required for Debian packaging"
    assert rules.exists(), "debian/rules is required for Debian packaging"
    assert changelog.exists(), "debian/changelog is required for Debian packaging"


def test_debian_metadata_mentions_python3_and_dh_python():
    control_text = (REPO_ROOT / "debian" / "control").read_text(encoding="utf-8")
    assert "python3" in control_text
    assert "dh-python" in control_text or "debhelper-compat" in control_text
