from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox,
)
from PySide6.QtCore import Qt

from nexus_shell_manager.core import desktop_manager
from nexus_common.constants import SUPPORTED_DESKTOPS, DEFAULT_DESKTOP, RECOMMENDED_DESKTOP
from nexus_common.package_cache import default_dry_run


class NexusShellManagerWindow(QMainWindow):
    """Install, remove, and switch desktop environments; configure the display manager."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Shell Manager")
        self.setGeometry(120, 120, 780, 560)

        self.active_desktop = desktop_manager.read_active_desktop()

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Desktop Environments")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        self.active_label = QLabel()
        layout.addWidget(self.active_label)

        self.list_widget = QListWidget()
        default_row = 0
        for row, (slug, name) in enumerate(SUPPORTED_DESKTOPS.items()):
            label = name
            if slug == DEFAULT_DESKTOP:
                label += "  (Default)"
            elif slug == RECOMMENDED_DESKTOP:
                label += "  (Recommended)"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, slug)
            self.list_widget.addItem(item)
            if slug == self.active_desktop:
                default_row = row
        self.list_widget.setCurrentRow(default_row)

        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install")
        self.remove_btn = QPushButton("Remove")
        self.switch_btn = QPushButton("Switch To")
        self.install_btn.clicked.connect(self._install)
        self.remove_btn.clicked.connect(self._remove)
        self.switch_btn.clicked.connect(self._switch)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.switch_btn)
        layout.addLayout(btn_layout)

        dm_layout = QHBoxLayout()
        dm_layout.addWidget(QLabel("Display Manager:"))
        self.dm_combo = QComboBox()
        self.dm_combo.addItems(desktop_manager.DISPLAY_MANAGERS)
        dm_layout.addWidget(self.dm_combo)
        self.configure_dm_btn = QPushButton("Configure")
        self.configure_dm_btn.clicked.connect(self._configure_display_manager)
        dm_layout.addWidget(self.configure_dm_btn)
        layout.addLayout(dm_layout)

        session_layout = QHBoxLayout()
        session_layout.addWidget(QLabel("Session Type:"))
        self.session_combo = QComboBox()
        self.session_combo.addItems(desktop_manager.SESSION_TYPES)
        session_layout.addWidget(self.session_combo)
        layout.addLayout(session_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self._refresh_active_label()
        self.statusBar().showMessage("Ready")

    def _refresh_active_label(self):
        name = SUPPORTED_DESKTOPS.get(self.active_desktop, self.active_desktop)
        self.active_label.setText(f"Active desktop: {name}")

    def _selected_slug(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _install(self):
        slug = self._selected_slug()
        if not slug:
            self.statusBar().showMessage("Select a desktop environment first.")
            return
        commands = desktop_manager.install_commands(slug)
        desktop_manager.run_commands(commands, dry_run=default_dry_run())
        name = SUPPORTED_DESKTOPS.get(slug, slug)
        self.statusBar().showMessage(f"Installed {name} ({commands[0]}).")

    def _remove(self):
        slug = self._selected_slug()
        if not slug:
            self.statusBar().showMessage("Select a desktop environment first.")
            return
        if slug == self.active_desktop:
            self.statusBar().showMessage("Cannot remove the currently active desktop. Switch first.")
            return
        commands = desktop_manager.remove_commands(slug)
        desktop_manager.run_commands(commands, dry_run=default_dry_run())
        name = SUPPORTED_DESKTOPS.get(slug, slug)
        self.statusBar().showMessage(f"Removed {name}.")

    def _switch(self):
        slug = self._selected_slug()
        if not slug:
            self.statusBar().showMessage("Select a desktop environment first.")
            return
        commands = desktop_manager.switch_commands(slug)
        desktop_manager.run_commands(commands, dry_run=default_dry_run())
        self.active_desktop = slug
        self._refresh_active_label()
        name = SUPPORTED_DESKTOPS.get(slug, slug)
        self.statusBar().showMessage(f"Switched active desktop to {name}. Log out to apply.")

    def _configure_display_manager(self):
        dm = self.dm_combo.currentText()
        commands = desktop_manager.configure_display_manager_commands(dm)
        desktop_manager.run_commands(commands, dry_run=default_dry_run())
        self.statusBar().showMessage(f"Configured display manager: {dm}.")
