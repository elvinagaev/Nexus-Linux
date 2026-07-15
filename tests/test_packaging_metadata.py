"""
Packaging metadata checks.

These guard against the two real (non test-only) bugs that used to make the
monorepo fall apart outside of the pytest sys.path tricks:

1. `nexus_common` was never an installable dependency of any app, so a real
   `pip install <app>` (or the Debian package) could not import it.
2. Several apps' `core`/`ui` packages raised `RuntimeError` at import time
   whenever they were not running from inside a live checkout of the repo,
   which is exactly the case for a real (non-editable) install.
"""

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

APPS = [
    "nexus-center",
    "nexus-shell-manager",
    "nexus-installer",
    "nexus-update",
    "nexus-driver",
    "nexus-store",
    "nexus-backup",
    "nexus-gaming",
    "nexus-settings",
]


def _load(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def test_shared_nexus_common_is_an_installable_distribution():
    shared_pyproject = REPO_ROOT / "shared" / "pyproject.toml"
    assert shared_pyproject.exists(), "shared/pyproject.toml is required so nexus_common can be pip installed"

    data = _load(shared_pyproject)
    assert data["project"]["name"] == "nexus-common"
    assert "nexus_common" in data["tool"]["setuptools"]["packages"]


def test_root_pyproject_does_not_claim_a_nonexistent_nexus_common_package():
    root_pyproject = REPO_ROOT / "pyproject.toml"
    data = _load(root_pyproject)
    # The real shared/nexus_common package lives under shared/, not at the
    # repo root -- the root project must not (re-)declare it, or a real
    # `pip install .` / `pybuild` run at the repo root fails looking for a
    # top-level nexus_common/ directory that doesn't exist.
    assert data["tool"]["setuptools"]["packages"] == []


def test_every_app_depends_on_nexus_common_and_has_a_console_script():
    for app in APPS:
        pyproject = REPO_ROOT / app / "pyproject.toml"
        data = _load(pyproject)

        deps = data["project"]["dependencies"]
        assert any(dep.split("@")[0].strip() == "nexus-common" for dep in deps), (
            f"{app}/pyproject.toml must depend on nexus-common so real installs can import it"
        )

        package_name = app.replace("-", "_")
        scripts = data["project"].get("scripts", {})
        assert app in scripts, f"{app}/pyproject.toml must define a '{app}' console script"
        assert scripts[app] == f"{package_name}.main:main"


def test_no_core_or_ui_init_raises_when_repo_layout_is_missing():
    """
    Regression guard: `core/__init__.py`/`ui/__init__.py` used to `raise
    RuntimeError(...)` if they couldn't find `shared/nexus_common` by walking
    up parent directories -- which always happens for a real, installed
    (non-editable) package, crashing the app at import time even though
    nexus_common was otherwise perfectly importable as a normal dependency.
    """
    offending = []
    for pattern in ("core/__init__.py", "ui/__init__.py"):
        for path in REPO_ROOT.glob(f"nexus-*/src/nexus_*/{pattern}"):
            text = path.read_text(encoding="utf-8")
            if "_find_repo_root" in text and "raise RuntimeError" in text:
                offending.append(path)

    assert not offending, f"Files still crash on non-editable installs: {offending}"
