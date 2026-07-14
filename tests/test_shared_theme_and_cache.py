"""Tests for shared theme and package prefetch/cache modules."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared"))

from nexus_common.theme import apply_theme, DARK_QSS, LIGHT_QSS, THEMES
from nexus_common.package_cache import (
    CacheablePackage, is_cached, install_from_cache, CACHE_ROOT,
)


class _FakeApp:
    def __init__(self):
        self.stylesheet = None

    def setStyleSheet(self, value):
        self.stylesheet = value


def test_themes_registry_has_dark_and_light():
    assert set(THEMES.keys()) == {"dark", "light"}
    assert THEMES["dark"] == DARK_QSS
    assert THEMES["light"] == LIGHT_QSS


def test_apply_theme_defaults_to_dark():
    app = _FakeApp()
    apply_theme(app)
    assert app.stylesheet == DARK_QSS


def test_apply_theme_light_mode():
    app = _FakeApp()
    apply_theme(app, mode="light")
    assert app.stylesheet == LIGHT_QSS


def test_apply_theme_unknown_mode_falls_back_to_dark():
    app = _FakeApp()
    apply_theme(app, mode="not-a-real-theme")
    assert app.stylesheet == DARK_QSS


def test_cacheable_package_with_no_packages_is_always_cached():
    item = CacheablePackage(id="proton", name="Proton", packages=[], description="")
    assert is_cached(item) is True


def test_cacheable_package_not_cached_off_linux_or_missing_cache():
    item = CacheablePackage(id="steam", name="Steam", packages=["steam"], description="")
    if sys.platform != "linux" or not CACHE_ROOT.exists():
        assert is_cached(item) is False


def test_install_from_cache_empty_packages_returns_no_commands():
    item = CacheablePackage(id="proton", name="Proton", packages=[], description="")
    commands = install_from_cache(item, dry_run=True)
    assert commands == []


def test_install_from_cache_dry_run_builds_command_without_executing():
    item = CacheablePackage(id="steam", name="Steam", packages=["steam"], description="")
    commands = install_from_cache(item, dry_run=True)
    assert len(commands) == 1
    assert "apt-get install -y --no-download" in commands[0]
    assert "steam" in commands[0]
