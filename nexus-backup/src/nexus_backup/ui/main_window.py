from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QComboBox,
)
from PySide6.QtCore import Qt

from nexus_backup.core import backup_manager
from nexus_common.package_cache import default_dry_run


class NexusBackupWindow(QMainWindow):
    """Create, restore, and manage system snapshots."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Backup")
        self.setGeometry(120, 120, 780, 560)

        self.snapshots = [backup_manager.new_snapshot("Clean install")]

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Backup & System Snapshots")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        layout.addWidget(QLabel("System Snapshots:"))
        self.snapshot_list = QListWidget()
        layout.addWidget(self.snapshot_list)
        self._refresh_list()

        auto_layout = QHBoxLayout()
        self.auto_backup_checkbox = QCheckBox("Enable Automatic Backups")
        self.auto_backup_checkbox.setChecked(True)
        auto_layout.addWidget(self.auto_backup_checkbox)
        auto_layout.addWidget(QLabel("Frequency:"))
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.frequency_combo.setCurrentIndex(1)
        auto_layout.addWidget(self.frequency_combo)
        layout.addLayout(auto_layout)

        btn_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create Snapshot Now")
        self.restore_btn = QPushButton("Restore Selected")
        self.delete_btn = QPushButton("Delete Selected")
        self.create_btn.clicked.connect(self._create_snapshot)
        self.restore_btn.clicked.connect(self._restore_snapshot)
        self.delete_btn.clicked.connect(self._delete_snapshot)
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _refresh_list(self):
        self.snapshot_list.clear()
        for snapshot in self.snapshots:
            item = QListWidgetItem(f"{snapshot.timestamp} - {snapshot.description}")
            item.setData(Qt.UserRole, snapshot.id)
            self.snapshot_list.addItem(item)

    def _selected_snapshot(self):
        item = self.snapshot_list.currentItem()
        if not item:
            return None
        snapshot_id = item.data(Qt.UserRole)
        return next((s for s in self.snapshots if s.id == snapshot_id), None)

    def _create_snapshot(self):
        snapshot = backup_manager.new_snapshot("Manual snapshot")
        backup_manager.run_commands(
            backup_manager.create_snapshot_commands(snapshot.id), dry_run=default_dry_run(),
        )
        self.snapshots.insert(0, snapshot)
        self._refresh_list()
        self.statusBar().showMessage("Snapshot created.")

    def _restore_snapshot(self):
        snapshot = self._selected_snapshot()
        if not snapshot:
            self.statusBar().showMessage("Select a snapshot to restore first.")
            return
        backup_manager.run_commands(
            backup_manager.restore_snapshot_commands(snapshot.id), dry_run=default_dry_run(),
        )
        self.statusBar().showMessage(f"Restoring '{snapshot.description}'... the system will restart.")

    def _delete_snapshot(self):
        snapshot = self._selected_snapshot()
        if not snapshot:
            self.statusBar().showMessage("Select a snapshot to delete first.")
            return
        backup_manager.run_commands(
            backup_manager.delete_snapshot_commands(snapshot.id), dry_run=default_dry_run(),
        )
        self.snapshots = [s for s in self.snapshots if s.id != snapshot.id]
        self._refresh_list()
        self.statusBar().showMessage(f"Deleted snapshot '{snapshot.description}'.")
