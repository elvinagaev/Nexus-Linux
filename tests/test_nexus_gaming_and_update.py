"""
Tests for Nexus Gaming's Discord/Proton-GE/exe-runner features and Nexus
Update's GitHub-based whole-system update checker.

None of these hit the real network -- functions that do (GitHub API calls,
downloads) are monkeypatched so the tests stay deterministic and offline,
consistent with the rest of the suite (NEXUS_DRY_RUN always forces
simulation for anything that touches subprocess/pkexec).
"""

import io
import tarfile

import pytest

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared"))
sys.path.insert(0, str(REPO_ROOT / "nexus-gaming" / "src"))
sys.path.insert(0, str(REPO_ROOT / "nexus-update" / "src"))

from nexus_gaming.core import discord_manager, exe_runner, proton_ge_manager
from nexus_update.core import github_update_manager


def test_discord_install_commands_reference_apt_and_deb_path():
    commands = discord_manager.install_commands()
    assert any("curl" in cmd and "discord.com" in cmd for cmd in commands)
    assert any("apt-get install" in cmd and str(discord_manager.DOWNLOAD_PATH) in cmd for cmd in commands)


def test_discord_install_dry_run_does_not_download():
    message = discord_manager.install_discord(dry_run=True)
    assert "Would" in message


def test_exe_runner_reports_missing_wine(monkeypatch):
    monkeypatch.setattr(exe_runner.shutil, "which", lambda _name: None)
    started, message = exe_runner.run_exe("C:/game.exe")
    assert started is False
    assert "Wine is not installed" in message


def test_exe_runner_launches_when_wine_present(monkeypatch):
    launched = {}

    class FakePopen:
        def __init__(self, argv):
            launched["argv"] = argv

    monkeypatch.setattr(exe_runner.shutil, "which", lambda _name: "/usr/bin/wine")
    monkeypatch.setattr(exe_runner.subprocess, "Popen", FakePopen)

    started, message = exe_runner.run_exe("/home/user/game.exe")
    assert started is True
    assert launched["argv"] == ["wine", "/home/user/game.exe"]
    assert "Launching" in message


def test_proton_ge_is_installed_false_when_directory_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(proton_ge_manager, "COMPAT_TOOLS_DIR", tmp_path)
    assert proton_ge_manager.is_installed("GE-Proton9-99") is False


def test_proton_ge_is_installed_true_when_directory_present(monkeypatch, tmp_path):
    (tmp_path / "GE-Proton9-99").mkdir()
    monkeypatch.setattr(proton_ge_manager, "COMPAT_TOOLS_DIR", tmp_path)
    assert proton_ge_manager.is_installed("GE-Proton9-99") is True


def test_proton_ge_install_latest_handles_unreachable_github(monkeypatch):
    monkeypatch.setattr(proton_ge_manager, "get_latest_release", lambda: None)
    message = proton_ge_manager.install_latest(dry_run=True)
    assert "Could not reach GitHub" in message


def test_proton_ge_install_latest_dry_run_reports_tag_without_downloading(monkeypatch):
    monkeypatch.setattr(
        proton_ge_manager, "get_latest_release",
        lambda: {"tag": "GE-Proton9-99", "url": "https://example.invalid/x.tar.gz"},
    )
    monkeypatch.setattr(proton_ge_manager, "is_installed", lambda _tag: False)
    message = proton_ge_manager.install_latest(dry_run=True)
    assert "GE-Proton9-99" in message
    assert "Would" in message


def _make_tarball_with_member(name: str) -> tarfile.TarFile:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo(name=name)
        data = b"payload"
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))
    buffer.seek(0)
    return tarfile.open(fileobj=buffer, mode="r:gz")


def test_proton_ge_safe_extract_rejects_path_traversal(tmp_path):
    archive = _make_tarball_with_member("../../etc/passwd")
    with pytest.raises(ValueError):
        proton_ge_manager._safe_extract(archive, tmp_path)


def test_proton_ge_safe_extract_allows_normal_member(tmp_path):
    archive = _make_tarball_with_member("GE-Proton9-99/files/bin/wine")
    proton_ge_manager._safe_extract(archive, tmp_path)
    assert (tmp_path / "GE-Proton9-99" / "files" / "bin" / "wine").exists()


def test_github_update_get_installed_commit_defaults_to_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(github_update_manager, "VERSION_MARKER", tmp_path / "missing.txt")
    assert github_update_manager.get_installed_commit() == ""


def test_github_update_check_for_update_handles_network_failure(monkeypatch):
    monkeypatch.setattr(github_update_manager, "get_latest_commit", lambda timeout=10: "")
    status = github_update_manager.check_for_update()
    assert status["checked"] is False
    assert status["available"] is False


def test_github_update_check_for_update_detects_new_commit(monkeypatch):
    monkeypatch.setattr(github_update_manager, "get_latest_commit", lambda timeout=10: "abc1234567")
    monkeypatch.setattr(github_update_manager, "get_installed_commit", lambda: "def7654321")
    status = github_update_manager.check_for_update()
    assert status["checked"] is True
    assert status["available"] is True


def test_github_update_check_for_update_up_to_date(monkeypatch):
    monkeypatch.setattr(github_update_manager, "get_latest_commit", lambda timeout=10: "abc1234567")
    monkeypatch.setattr(github_update_manager, "get_installed_commit", lambda: "abc1234567")
    status = github_update_manager.check_for_update()
    assert status["checked"] is True
    assert status["available"] is False


def test_github_update_apply_update_commands_cover_every_staged_app():
    commands = github_update_manager.apply_update_commands()
    for app in github_update_manager.STAGED_APPS:
        assert any(app in cmd for cmd in commands)


def test_github_update_apply_update_dry_run_reports_commit_without_downloading(monkeypatch):
    monkeypatch.setattr(github_update_manager, "get_latest_commit", lambda timeout=10: "abc1234567")
    message = github_update_manager.apply_update(dry_run=True)
    assert "abc1234567" in message
    assert "Would" in message


def test_github_update_apply_update_handles_unreachable_github(monkeypatch):
    monkeypatch.setattr(github_update_manager, "get_latest_commit", lambda timeout=10: "")
    message = github_update_manager.apply_update(dry_run=False)
    assert "Could not reach GitHub" in message


def test_github_update_safe_extract_rejects_path_traversal(tmp_path):
    archive = _make_tarball_with_member("../outside.txt")
    with pytest.raises(ValueError):
        github_update_manager._safe_extract(archive, tmp_path)
