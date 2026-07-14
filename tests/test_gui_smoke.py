"""
Headless GUI smoke tests.

These actually instantiate every Nexus application window using Qt's
"offscreen" platform plugin (no real display required), to verify the UI
code truly constructs and responds to basic interaction -- this is real
verification, not just "no syntax errors reported by the editor".
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared"))

pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def _add_src(app_dir_name: str):
    src = REPO_ROOT / app_dir_name / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def test_nexus_center_window_constructs(qapp):
    _add_src("nexus-center")
    from nexus_center.ui.main_window import NexusCenterWindow

    window = NexusCenterWindow()
    assert window.windowTitle() == "Nexus Center"
    window.close()


def test_nexus_installer_wizard_constructs_and_navigates(qapp):
    _add_src("nexus-installer")
    from nexus_installer.ui.main_window import NexusInstallerWindow

    window = NexusInstallerWindow()
    assert window.pages[0] is window.welcome_page
    window._go_next()
    assert window.current_index == 1
    window.close()


def test_nexus_driver_window_constructs(qapp):
    _add_src("nexus-driver")
    from nexus_driver.ui.main_window import NexusDriverWindow

    window = NexusDriverWindow()
    assert window.table.rowCount() > 0
    window.close()


def test_nexus_gaming_window_constructs(qapp):
    _add_src("nexus-gaming")
    from nexus_gaming.ui.main_window import NexusGamingWindow

    window = NexusGamingWindow()
    assert window.table.rowCount() > 0
    window.close()


def test_nexus_shell_manager_window_constructs(qapp):
    _add_src("nexus-shell-manager")
    from nexus_shell_manager.ui.main_window import NexusShellManagerWindow

    window = NexusShellManagerWindow()
    assert window.list_widget.count() > 0
    window.close()


def test_nexus_update_window_constructs(qapp):
    _add_src("nexus-update")
    from nexus_update.ui.main_window import NexusUpdateWindow

    window = NexusUpdateWindow()
    assert window.kernel_combo.count() > 0
    window.close()


def test_nexus_store_window_constructs(qapp):
    _add_src("nexus-store")
    from nexus_store.ui.main_window import NexusStoreWindow

    window = NexusStoreWindow()
    assert window.table.rowCount() > 0
    window.close()


def test_nexus_backup_window_constructs(qapp):
    _add_src("nexus-backup")
    from nexus_backup.ui.main_window import NexusBackupWindow

    window = NexusBackupWindow()
    assert window.snapshot_list.count() == 1
    window.close()


def test_nexus_settings_window_constructs(qapp):
    _add_src("nexus-settings")
    from nexus_settings.ui.main_window import NexusSettingsWindow

    window = NexusSettingsWindow()
    assert window.region_combo.count() > 0
    window.close()


def test_nexus_shell_manager_switch_button_updates_active_desktop(qapp):
    _add_src("nexus-shell-manager")
    from nexus_shell_manager.ui.main_window import NexusShellManagerWindow

    window = NexusShellManagerWindow()
    window.list_widget.setCurrentRow(2)  # some non-default desktop
    target_name = window.list_widget.currentItem().text()
    window.switch_btn.click()
    assert window.active_label.text() == f"Active desktop: {target_name}"
    window.close()


def test_nexus_driver_install_button_updates_status(qapp):
    _add_src("nexus-driver")
    from nexus_driver.ui.main_window import NexusDriverWindow

    window = NexusDriverWindow()
    install_btn = window.table.cellWidget(0, 3)
    install_btn.click()
    assert "installed" in window.statusBar().currentMessage().lower()
    window.close()


def test_nexus_backup_create_snapshot_button_adds_entry(qapp):
    _add_src("nexus-backup")
    from nexus_backup.ui.main_window import NexusBackupWindow

    window = NexusBackupWindow()
    initial_count = window.snapshot_list.count()
    window.create_btn.click()
    assert window.snapshot_list.count() == initial_count + 1
    window.close()
