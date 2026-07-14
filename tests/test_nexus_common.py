from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))

from nexus_common.constants import APP_REGISTRY, SUPPORTED_DESKTOPS, get_desktop_display_name
from nexus_common.base import NexusApplicationInfo, NexusApplication


def test_supported_desktops_include_hyprland():
    assert "hyprland" in SUPPORTED_DESKTOPS


def test_desktop_lookup_returns_display_name():
    assert get_desktop_display_name("hyprland") == "Hyprland"


def test_app_registry_contains_core_modules():
    assert "nexus-center" in APP_REGISTRY
    assert "nexus-gaming" in APP_REGISTRY
    assert "nexus-shell-manager" in APP_REGISTRY
    assert "nexus-installer" in APP_REGISTRY
    assert "nexus-driver" in APP_REGISTRY
    assert "nexus-backup" in APP_REGISTRY


def test_supported_desktops_has_kde_xfce_gnome():
    assert "kde" in SUPPORTED_DESKTOPS
    assert "xfce" in SUPPORTED_DESKTOPS
    assert "gnome" in SUPPORTED_DESKTOPS


def test_app_registry_has_nine_modules():
    expected_apps = [
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
    for app in expected_apps:
        assert app in APP_REGISTRY, f"Missing app: {app}"


def test_application_info_creation():
    info = NexusApplicationInfo(
        name="Test App",
        slug="test-app",
        description="A test application",
        category="test"
    )
    assert info.name == "Test App"
    assert info.slug == "test-app"
    assert info.description == "A test application"
    assert info.category == "test"


def test_nexus_application_initialization():
    info = NexusApplicationInfo(
        name="Test",
        slug="test",
        description="Test",
        category="test"
    )
    app = NexusApplication(info)
    assert app.info.name == "Test"
    assert app.info.slug == "test"
