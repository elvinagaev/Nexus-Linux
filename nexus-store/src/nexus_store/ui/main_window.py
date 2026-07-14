from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
)

from nexus_store.core.store_catalog import STORE_CATALOG
from nexus_common.package_cache import is_cached, install_from_cache, default_dry_run


class NexusStoreWindow(QMainWindow):
    """Browse and install applications from the Nexus package catalog."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Store")
        self.setGeometry(120, 120, 820, 560)

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Nexus Store")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search applications...")
        self.search_input.textChanged.connect(self._filter)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Application", "Description", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install Selected")
        self.remove_btn = QPushButton("Remove Selected")
        self.install_btn.clicked.connect(self._install_selected)
        self.remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self.install_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self._populate()
        self.statusBar().showMessage("Ready")

    def _populate(self, filter_text: str = ""):
        self.table.setRowCount(0)
        filter_text = filter_text.lower()
        for item in STORE_CATALOG:
            if filter_text and filter_text not in item.name.lower() and filter_text not in item.description.lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item.name))
            self.table.setItem(row, 1, QTableWidgetItem(item.description))
            status = "Installed" if is_cached(item) else "Available"
            self.table.setItem(row, 2, QTableWidgetItem(status))

    def _filter(self, text):
        self._populate(text)

    def _selected_item(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        name = self.table.item(row, 0).text()
        return next((item for item in STORE_CATALOG if item.name == name), None), row

    def _install_selected(self):
        result = self._selected_item()
        if not result or not result[0]:
            self.statusBar().showMessage("Select an application to install first.")
            return
        item, row = result
        install_from_cache(item, dry_run=default_dry_run())
        self.table.setItem(row, 2, QTableWidgetItem("Installed"))
        self.statusBar().showMessage(f"{item.name} installed.")

    def _remove_selected(self):
        result = self._selected_item()
        if not result or not result[0]:
            self.statusBar().showMessage("Select an application to remove first.")
            return
        item, row = result
        self.table.setItem(row, 2, QTableWidgetItem("Available"))
        self.statusBar().showMessage(f"{item.name} removed.")
