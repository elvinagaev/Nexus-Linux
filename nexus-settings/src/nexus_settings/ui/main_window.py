from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox,
)

from nexus_settings.core import settings_manager
from nexus_common.package_cache import default_dry_run


class NexusSettingsWindow(QMainWindow):
    """Low-level system preferences: computer name, locale, and keyboard layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Settings")
        self.setGeometry(120, 120, 680, 460)

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("System Preferences")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        form = QFormLayout()

        self.hostname_input = QLineEdit("nexus-linux")
        form.addRow("Computer name:", self.hostname_input)

        self.region_combo = QComboBox()
        for region in settings_manager.get_regions():
            self.region_combo.addItem(region["region"], region)
        form.addRow("Region:", self.region_combo)

        self.details_label = QLabel()
        form.addRow("", self.details_label)
        self.region_combo.currentIndexChanged.connect(self._update_details)
        self._update_details()

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.apply_hostname_btn = QPushButton("Apply Computer Name")
        self.apply_locale_btn = QPushButton("Apply Region Settings")
        self.apply_hostname_btn.clicked.connect(self._apply_hostname)
        self.apply_locale_btn.clicked.connect(self._apply_locale)
        btn_layout.addWidget(self.apply_hostname_btn)
        btn_layout.addWidget(self.apply_locale_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _update_details(self):
        region = self.region_combo.currentData()
        if region:
            self.details_label.setText(
                f"Locale: {region['locale']} | Timezone: {region['timezone']} | "
                f"Keyboard: {region['keyboard']}"
            )

    def _apply_hostname(self):
        hostname = self.hostname_input.text().strip()
        if not hostname:
            self.statusBar().showMessage("Enter a computer name first.")
            return
        settings_manager.run_commands(
            settings_manager.apply_hostname_commands(hostname), dry_run=default_dry_run(),
        )
        self.statusBar().showMessage(f"Computer name set to '{hostname}'.")

    def _apply_locale(self):
        region = self.region_combo.currentData()
        if not region:
            self.statusBar().showMessage("Select a region first.")
            return
        settings_manager.run_commands(
            settings_manager.apply_locale_commands(region), dry_run=default_dry_run(),
        )
        self.statusBar().showMessage(f"Applied region settings for {region['region']}.")
