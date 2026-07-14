from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem, QHeaderView,
)

from nexus_installer.core import disk_manager, efi_manager


class PartitionPage(QWidget):
    title = "Disk Partitioning"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Choose a disk and partitioning method")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        self.disks = disk_manager.list_disks()

        layout.addWidget(QLabel("Target disk:"))
        self.disk_combo = QComboBox()
        for disk in self.disks:
            self.disk_combo.addItem(f"/dev/{disk.name} \u2014 {disk.size} ({disk.model})", disk)
        layout.addWidget(self.disk_combo)

        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.erase_radio = QRadioButton("Erase disk and install Nexus Linux (recommended)")
        self.manual_radio = QRadioButton("Manual partitioning")
        self.erase_radio.setChecked(True)
        self.mode_group.addButton(self.erase_radio, 0)
        self.mode_group.addButton(self.manual_radio, 1)
        mode_layout.addWidget(self.erase_radio)
        mode_layout.addWidget(self.manual_radio)
        layout.addLayout(mode_layout)

        self.partition_table = QTableWidget(0, 4)
        self.partition_table.setHorizontalHeaderLabels(["Partition", "Size", "Filesystem", "Mountpoint"])
        self.partition_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.partition_table)

        self.boot_mode_label = QLabel()
        layout.addWidget(self.boot_mode_label)

        self.efi_status_label = QLabel()
        self.efi_status_label.setWordWrap(True)
        layout.addWidget(self.efi_status_label)

        self.disk_combo.currentIndexChanged.connect(self._refresh_partitions)
        self._refresh_partitions()

        layout.addStretch()
        self.setLayout(layout)

    def _refresh_partitions(self):
        disk = self.disk_combo.currentData()
        self.partition_table.setRowCount(0)
        if disk is None:
            self.boot_mode_label.setText("")
            self.efi_status_label.setText("No disks detected.")
            return

        for partition in disk.partitions:
            row = self.partition_table.rowCount()
            self.partition_table.insertRow(row)
            self.partition_table.setItem(row, 0, QTableWidgetItem(partition.name))
            self.partition_table.setItem(row, 1, QTableWidgetItem(partition.size))
            self.partition_table.setItem(row, 2, QTableWidgetItem(partition.fstype or "unformatted"))
            self.partition_table.setItem(row, 3, QTableWidgetItem(partition.mountpoint or ""))

        boot_mode = efi_manager.detect_boot_mode()
        self.boot_mode_label.setText(f"Detected boot mode: {boot_mode.upper()}")

        is_valid, message = efi_manager.validate_esp(disk.partitions)
        prefix = "\u2713" if is_valid else "\u26a0"
        self.efi_status_label.setText(f"{prefix} {message}")

    def is_valid(self) -> bool:
        return self.disk_combo.currentData() is not None

    def collect(self, config):
        disk = self.disk_combo.currentData()
        config.disk = disk.name if disk else ""
        config.partition_mode = "erase" if self.erase_radio.isChecked() else "manual"
