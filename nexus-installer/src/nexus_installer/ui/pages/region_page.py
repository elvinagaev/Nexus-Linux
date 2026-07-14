from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

from nexus_common.constants import REGIONS


class RegionPage(QWidget):
    title = "Region & Language"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Select your region")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        layout.addWidget(QLabel("Region:"))
        self.region_combo = QComboBox()
        for region in REGIONS:
            self.region_combo.addItem(region["region"], region)
        layout.addWidget(self.region_combo)

        self.details_label = QLabel()
        layout.addWidget(self.details_label)
        self.region_combo.currentIndexChanged.connect(self._update_details)
        self._update_details()

        layout.addStretch()
        self.setLayout(layout)

    def _update_details(self):
        region = self.region_combo.currentData()
        if region:
            self.details_label.setText(
                f"Locale: {region['locale']}\n"
                f"Timezone: {region['timezone']}\n"
                f"Keyboard layout: {region['keyboard']}"
            )

    def is_valid(self) -> bool:
        return self.region_combo.currentData() is not None

    def collect(self, config):
        config.region = self.region_combo.currentData() or {}
