from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

from nexus_common.constants import SUPPORTED_DESKTOPS, DEFAULT_DESKTOP, RECOMMENDED_DESKTOP


class DesktopPage(QWidget):
    title = "Desktop Environment"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Choose your desktop environment")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        info = QLabel(
            "GNOME is installed automatically by default for maximum compatibility. "
            "You can install, remove, or switch desktops later with Nexus Shell Manager."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.list_widget = QListWidget()
        default_row = 0
        for row, (slug, name) in enumerate(SUPPORTED_DESKTOPS.items()):
            label = name
            if slug == DEFAULT_DESKTOP:
                label += "  (Default)"
                default_row = row
            elif slug == RECOMMENDED_DESKTOP:
                label += "  (Recommended)"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, slug)
            self.list_widget.addItem(item)

        self.list_widget.setCurrentRow(default_row)
        layout.addWidget(self.list_widget)
        layout.addStretch()
        self.setLayout(layout)

    def is_valid(self) -> bool:
        return self.list_widget.currentItem() is not None

    def collect(self, config):
        item = self.list_widget.currentItem()
        config.desktop = item.data(Qt.UserRole) if item else DEFAULT_DESKTOP
