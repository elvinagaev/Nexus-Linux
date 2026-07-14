"""Tests validating the live-build configuration that produces the bootable
live ISO (GNOME already running + Nexus Installer auto-launched), as opposed
to the classic Debian netinst/DVD skeleton kept at the repository root."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "live-build"


def test_live_build_auto_scripts_exist():
    assert (ROOT / "auto" / "config").exists()
    assert (ROOT / "auto" / "clean").exists()


def test_live_build_config_targets_gnome_desktop():
    package_list = ROOT / "config" / "package-lists" / "nexus-desktop.list.chroot"
    assert package_list.exists()
    content = package_list.read_text(encoding="utf-8")
    assert "task-gnome-desktop" in content
    assert "python3-pyside6" in content


def test_live_build_has_autostart_entry_for_installer():
    autostart = (
        ROOT / "config" / "includes.chroot" / "etc" / "skel" / ".config"
        / "autostart" / "nexus-installer.desktop"
    )
    assert autostart.exists()
    content = autostart.read_text(encoding="utf-8")
    assert "X-GNOME-Autostart-enabled=true" in content
    assert "/usr/local/bin/nexus-installer" in content


def test_live_build_launcher_script_sets_pythonpath():
    launcher = ROOT / "config" / "includes.chroot" / "usr" / "local" / "bin" / "nexus-installer"
    assert launcher.exists()
    content = launcher.read_text(encoding="utf-8")
    assert "nexus_installer.main" in content
    assert "PYTHONPATH" in content


def test_build_iso_workflow_exists():
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "build-iso.yml"
    assert workflow.exists()
    content = workflow.read_text(encoding="utf-8")
    assert "live-build" in content
    assert "upload-artifact" in content
