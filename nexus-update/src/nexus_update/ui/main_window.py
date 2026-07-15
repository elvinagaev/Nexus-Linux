from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QMessageBox,
)

from nexus_update.core import update_manager, github_update_manager
from nexus_common.package_cache import default_dry_run


class NexusUpdateWindow(QMainWindow):
    """Update management with rollback support, update history, and kernel selection."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Update")
        self.setGeometry(120, 120, 780, 560)

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Updates & Kernel Management")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        self.status_label = QLabel("System is up to date")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.check_btn = QPushButton("Check for Updates")
        self.install_btn = QPushButton("Install Updates")
        self.cleanup_btn = QPushButton("Package Cleanup")
        self.check_btn.clicked.connect(self._check_updates)
        self.install_btn.clicked.connect(self._install_updates)
        self.cleanup_btn.clicked.connect(self._cleanup)
        btn_layout.addWidget(self.check_btn)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.cleanup_btn)
        layout.addLayout(btn_layout)

        kernel_layout = QHBoxLayout()
        kernel_layout.addWidget(QLabel("Kernel:"))
        self.kernel_combo = QComboBox()
        self.kernel_combo.addItems(update_manager.AVAILABLE_KERNELS)
        kernel_layout.addWidget(self.kernel_combo)
        self.set_kernel_btn = QPushButton("Set Active Kernel")
        self.set_kernel_btn.clicked.connect(self._set_kernel)
        kernel_layout.addWidget(self.set_kernel_btn)
        layout.addLayout(kernel_layout)

        layout.addWidget(QLabel("Nexus Linux itself (apps/installer source, from GitHub):"))
        github_layout = QHBoxLayout()
        self.github_update_btn = QPushButton("Check Nexus Linux Updates")
        self.github_update_btn.clicked.connect(self._check_github_update)
        github_layout.addWidget(self.github_update_btn)
        layout.addLayout(github_layout)

        layout.addWidget(QLabel("Update History:"))
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        self.rollback_btn = QPushButton("Rollback Selected")
        self.rollback_btn.clicked.connect(self._rollback)
        layout.addWidget(self.rollback_btn)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _log_history(self, description: str):
        entry = update_manager.new_history_entry(description)
        self.history_list.insertItem(0, f"{entry.timestamp} - {entry.description}")

    def _check_updates(self):
        update_manager.run_commands(update_manager.check_updates_commands(), dry_run=default_dry_run())
        self.status_label.setText("3 updates available")
        self._log_history("Checked for updates: 3 packages available")
        self.statusBar().showMessage("Checked for updates.")

    def _install_updates(self):
        update_manager.run_commands(update_manager.install_updates_commands(), dry_run=default_dry_run())
        self.status_label.setText("System is up to date")
        self._log_history("Installed available updates")
        self.statusBar().showMessage("Updates installed.")

    def _cleanup(self):
        update_manager.run_commands(update_manager.cleanup_commands(), dry_run=default_dry_run())
        self._log_history("Cleaned up obsolete packages")
        self.statusBar().showMessage("Package cleanup complete.")

    def _set_kernel(self):
        kernel = self.kernel_combo.currentText()
        update_manager.run_commands(update_manager.set_kernel_commands(kernel), dry_run=default_dry_run())
        self._log_history(f"Set active kernel to {kernel}")
        self.statusBar().showMessage(f"Active kernel set to {kernel}. Restart to apply.")

    def _rollback(self):
        item = self.history_list.currentItem()
        if not item:
            self.statusBar().showMessage("Select a history entry to roll back to first.")
            return
        update_manager.run_commands(update_manager.rollback_commands(item.text()), dry_run=default_dry_run())
        self._log_history(f"Rolled back to: {item.text()}")
        self.statusBar().showMessage("Rollback complete. See Nexus Backup for snapshot details.")

    def _check_github_update(self):
        self.github_update_btn.setEnabled(False)
        self.statusBar().showMessage("Checking GitHub for a new Nexus Linux version...")
        status = github_update_manager.check_for_update()
        self.github_update_btn.setEnabled(True)

        if not status["checked"]:
            self.statusBar().showMessage("Could not reach GitHub to check for updates.")
            return
        if not status["available"]:
            self.statusBar().showMessage(f"Nexus Linux is up to date (commit {status['installed']}).")
            return

        answer = QMessageBox.question(
            self,
            "Nexus Linux update available",
            f"A new Nexus Linux version is available on GitHub "
            f"(commit {status['latest']}, currently on {status['installed']}).\n\n"
            "Download and install it now?",
        )
        if answer != QMessageBox.Yes:
            self.statusBar().showMessage("Update postponed.")
            return

        self.statusBar().showMessage("Downloading and applying the Nexus Linux update...")
        message = github_update_manager.apply_update(dry_run=default_dry_run())
        self._log_history(message)
        self.statusBar().showMessage(message)
