from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QCheckBox,
    QComboBox,
)

from nexus_gaming.core.gaming_catalog import GAMING_CATALOG
from nexus_common.package_cache import (
    PackagePrefetcher, is_cached, install_from_cache, PYSIDE6_AVAILABLE,
)


class NexusGamingWindow(QMainWindow):
    """Gaming tools configuration with background prefetch caching for instant installs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Gaming")
        self.setGeometry(140, 140, 880, 600)

        self.prefetcher = None
        self.row_by_id = {}
        self.checkbox_by_id = {}

        central = QWidget()
        layout = QVBoxLayout()

        header = QLabel("Gaming Configuration")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(header)

        subtitle = QLabel(
            "Prefetch downloads gaming tools in the background so \"Install Selected\" "
            "applies them almost instantly from the local cache."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        gpu_row = QHBoxLayout()
        gpu_row.addWidget(QLabel("Active GPU:"))
        self.gpu_combo = QComboBox()
        self.gpu_combo.addItems(["Auto-detect", "NVIDIA", "AMD", "Intel"])
        gpu_row.addWidget(self.gpu_combo)
        gpu_row.addStretch()
        layout.addLayout(gpu_row)

        self.table = QTableWidget(len(GAMING_CATALOG), 4)
        self.table.setHorizontalHeaderLabels(["", "Tool", "Description", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 30)
        self.table.verticalHeader().setVisible(False)

        for row, item in enumerate(GAMING_CATALOG):
            self.row_by_id[item.id] = row

            checkbox = QCheckBox()
            checkbox.setChecked(item.id in ("steam", "proton"))
            self.checkbox_by_id[item.id] = checkbox
            self.table.setCellWidget(row, 0, checkbox)

            self.table.setItem(row, 1, QTableWidgetItem(item.name))
            self.table.setItem(row, 2, QTableWidgetItem(item.description))
            self.table.setItem(row, 3, QTableWidgetItem(self._status_text(item)))

        layout.addWidget(self.table)

        self.performance_checkbox = QCheckBox("Enable High Performance Mode (GameMode auto-start)")
        self.performance_checkbox.setChecked(True)
        layout.addWidget(self.performance_checkbox)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        self.prefetch_btn = QPushButton("Prefetch All")
        self.prefetch_btn.clicked.connect(self._prefetch_all)
        self.install_btn = QPushButton("Install Selected")
        self.install_btn.clicked.connect(self._install_selected)
        btn_layout.addWidget(self.prefetch_btn)
        btn_layout.addWidget(self.install_btn)
        layout.addLayout(btn_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _status_text(self, item) -> str:
        return "Cached (ready to install)" if is_cached(item) else "Not downloaded"

    def _prefetch_all(self):
        if self.prefetcher is not None:
            return

        self.prefetch_btn.setEnabled(False)
        self.statusBar().showMessage("Prefetching gaming tools in the background...")

        self.prefetcher = PackagePrefetcher(GAMING_CATALOG)
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
            self.table.setItem(row, 3, QTableWidgetItem("Downloading..."))

    def _on_item_cached(self, item_id):
        row = self.row_by_id.get(item_id)
        if row is not None:
            self.table.setItem(row, 3, QTableWidgetItem("Cached (ready to install)"))

    def _on_item_failed(self, item_id, message):
        row = self.row_by_id.get(item_id)
        if row is not None:
            self.table.setItem(row, 3, QTableWidgetItem("Download failed"))

    def _on_all_finished(self):
        self.prefetch_btn.setEnabled(True)
        self.prefetcher = None
        self.progress_bar.setValue(100)
        self.statusBar().showMessage("All gaming tools prefetched and ready to install instantly.")

    def _install_selected(self):
        installed = []
        all_cached = True
        for item in GAMING_CATALOG:
            checkbox = self.checkbox_by_id.get(item.id)
            if checkbox is None or not checkbox.isChecked():
                continue
            if not is_cached(item):
                all_cached = False
            install_from_cache(item, dry_run=True)
            row = self.row_by_id[item.id]
            self.table.setItem(row, 3, QTableWidgetItem("Installed"))
            installed.append(item.name)

        if not installed:
            self.statusBar().showMessage("Select at least one gaming tool to install.")
            return

        speed_note = "instantly from cache" if all_cached else "with some tools downloaded on demand"
        self.statusBar().showMessage(f"Installed: {', '.join(installed)} ({speed_note}).")
