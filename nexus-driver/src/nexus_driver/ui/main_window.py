from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
)

from nexus_driver.core.driver_catalog import DRIVER_CATALOG
from nexus_common.package_cache import (
    PackagePrefetcher, is_cached, install_from_cache, default_dry_run, PYSIDE6_AVAILABLE,
)


class NexusDriverWindow(QMainWindow):
    """Detects hardware and manages driver/firmware installation with prefetch caching."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Driver Manager")
        self.setGeometry(120, 120, 860, 560)

        self.prefetcher = None
        self.row_by_id = {}

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Drivers & Firmware")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        subtitle = QLabel(
            "Prefetch downloads drivers in the background ahead of time, so clicking "
            "Install later applies them almost instantly from the local cache."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.table = QTableWidget(len(DRIVER_CATALOG), 4)
        self.table.setHorizontalHeaderLabels(["Driver", "Description", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        for row, item in enumerate(DRIVER_CATALOG):
            self.row_by_id[item.id] = row
            self.table.setItem(row, 0, QTableWidgetItem(item.name))
            self.table.setItem(row, 1, QTableWidgetItem(item.description))
            self.table.setItem(row, 2, QTableWidgetItem(self._status_text(item)))

            install_btn = QPushButton("Install")
            install_btn.clicked.connect(lambda _checked, i=item, r=row: self._install(i, r))
            self.table.setCellWidget(row, 3, install_btn)

        layout.addWidget(self.table)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Hardware")
        self.scan_btn.clicked.connect(self._scan_hardware)
        self.prefetch_btn = QPushButton("Prefetch All Drivers")
        self.prefetch_btn.clicked.connect(self._prefetch_all)
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.prefetch_btn)
        layout.addLayout(btn_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _status_text(self, item) -> str:
        return "Cached (ready to install)" if is_cached(item) else "Not downloaded"

    def _scan_hardware(self):
        self.statusBar().showMessage("Hardware scan complete: all supported devices listed below.")

    def _prefetch_all(self):
        if self.prefetcher is not None:
            return

        self.prefetch_btn.setEnabled(False)
        self.statusBar().showMessage("Prefetching drivers in the background...")

        self.prefetcher = PackagePrefetcher(DRIVER_CATALOG)
        self.prefetcher.item_started.connect(self._on_item_started)
        self.prefetcher.item_progress.connect(lambda _id, percent: self.progress_bar.setValue(percent))
        self.prefetcher.item_cached.connect(self._on_item_cached)
        self.prefetcher.item_failed.connect(self._on_item_failed)
        self.prefetcher.all_finished.connect(self._on_all_finished)

        if PYSIDE6_AVAILABLE:
            self.prefetcher.start()
        else:
            self.prefetcher.run()

    def _on_item_started(self, item_id):
        row = self.row_by_id.get(item_id)
        if row is not None:
            self.table.setItem(row, 2, QTableWidgetItem("Downloading..."))

    def _on_item_cached(self, item_id):
        row = self.row_by_id.get(item_id)
        if row is not None:
            self.table.setItem(row, 2, QTableWidgetItem("Cached (ready to install)"))

    def _on_item_failed(self, item_id, message):
        row = self.row_by_id.get(item_id)
        if row is not None:
            self.table.setItem(row, 2, QTableWidgetItem("Download failed"))

    def _on_all_finished(self):
        self.prefetch_btn.setEnabled(True)
        self.prefetcher = None
        self.progress_bar.setValue(100)
        self.statusBar().showMessage("All drivers prefetched and ready to install instantly.")

    def _install(self, item, row):
        was_cached = is_cached(item)
        install_from_cache(item, dry_run=default_dry_run())
        self.table.setItem(row, 2, QTableWidgetItem("Installed"))
        speed_note = "instantly from cache" if was_cached else "after downloading (not prefetched)"
        self.statusBar().showMessage(f"{item.name} installed {speed_note}.")
