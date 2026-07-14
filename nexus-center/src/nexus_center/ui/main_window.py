from pathlib import Path
import sys

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
        QComboBox, QSpinBox, QCheckBox, QStatusBar, QMessageBox, QScrollArea
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon, QFont
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parents[4]
SHARED_ROOT = REPO_ROOT / "shared"
if str(SHARED_ROOT) not in sys.path:
    sys.path.append(str(SHARED_ROOT))

from nexus_common.constants import SUPPORTED_DESKTOPS
from nexus_common.theme import apply_theme


def create_system_tab():
    """Create System Settings tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("System Information")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # System info (placeholder)
    info_label = QLabel("System Status:\n• CPU: Loading...\n• Memory: Loading...\n• Storage: Loading...")
    layout.addWidget(info_label)
    
    # Hostname section
    hostname_label = QLabel("Computer Name:")
    hostname_input = QLineEdit()
    hostname_input.setPlaceholderText("Enter your computer name")
    layout.addWidget(hostname_label)
    layout.addWidget(hostname_input)
    
    # Apply button
    apply_btn = QPushButton("Apply Changes")
    layout.addWidget(apply_btn)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_desktop_tab():
    """Create Desktop Environment tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Desktop Environments")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # Current desktop info
    current = QLabel("Current Desktop: Hyprland (recommended)")
    layout.addWidget(current)
    
    # Desktop selection list
    desktop_label = QLabel("Available Desktops:")
    layout.addWidget(desktop_label)
    
    desktop_list = QListWidget()
    for slug, name in SUPPORTED_DESKTOPS.items():
        desktop_list.addItem(f"{name} ({slug})")
    
    layout.addWidget(desktop_list)
    
    # Action buttons
    btn_layout = QHBoxLayout()
    install_btn = QPushButton("Install")
    remove_btn = QPushButton("Remove")
    switch_btn = QPushButton("Switch To")
    
    btn_layout.addWidget(install_btn)
    btn_layout.addWidget(remove_btn)
    btn_layout.addWidget(switch_btn)
    layout.addLayout(btn_layout)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_updates_tab():
    """Create Updates & Kernel tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Updates & Kernel Management")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # Update status
    status = QLabel("System is up to date\nLast checked: Just now")
    layout.addWidget(status)
    
    # Kernel section
    kernel_label = QLabel("Kernel Selection:")
    kernel_combo = QComboBox()
    kernel_combo.addItems(["6.8.0-linux (current)", "6.7.0-linux", "6.6.0-linux"])
    layout.addWidget(kernel_label)
    layout.addWidget(kernel_combo)
    
    # Buttons
    btn_layout = QHBoxLayout()
    check_btn = QPushButton("Check for Updates")
    install_btn = QPushButton("Install Updates")
    rollback_btn = QPushButton("Rollback")
    
    btn_layout.addWidget(check_btn)
    btn_layout.addWidget(install_btn)
    btn_layout.addWidget(rollback_btn)
    layout.addLayout(btn_layout)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_drivers_tab():
    """Create Drivers & Firmware tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Drivers & Firmware")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # Driver list
    driver_list = QListWidget()
    drivers = [
        "NVIDIA Driver (450.0) - Installed",
        "AMD Drivers - Not installed",
        "Intel Drivers - Installed",
        "Broadcom WiFi - Installed",
        "Realtek Audio - Installed"
    ]
    for driver in drivers:
        driver_list.addItem(driver)
    
    layout.addWidget(QLabel("Detected Hardware Drivers:"))
    layout.addWidget(driver_list)
    
    # Buttons
    btn_layout = QHBoxLayout()
    scan_btn = QPushButton("Scan Hardware")
    install_btn = QPushButton("Install Selected")
    btn_layout.addWidget(scan_btn)
    btn_layout.addWidget(install_btn)
    layout.addLayout(btn_layout)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_gaming_tab():
    """Create Gaming Configuration tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Gaming Configuration")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # Gaming tools status
    tools_list = QListWidget()
    tools = [
        "Steam - Installed",
        "Proton - Installed",
        "Wine - Installed",
        "Lutris - Not installed",
        "MangoHud - Installed",
        "GameMode - Installed"
    ]
    for tool in tools:
        tools_list.addItem(tool)
    
    layout.addWidget(QLabel("Gaming Tools:"))
    layout.addWidget(tools_list)
    
    # Gaming options
    gpu_label = QLabel("GPU:")
    gpu_combo = QComboBox()
    gpu_combo.addItems(["NVIDIA GeForce RTX 3070", "AMD Radeon RX 6800"])
    layout.addWidget(gpu_label)
    layout.addWidget(gpu_combo)
    
    # Performance settings
    performance = QCheckBox("Enable High Performance Mode")
    performance.setChecked(True)
    layout.addWidget(performance)
    
    # Buttons
    btn_layout = QHBoxLayout()
    install_btn = QPushButton("Install Gaming Tools")
    config_btn = QPushButton("Configure")
    btn_layout.addWidget(install_btn)
    btn_layout.addWidget(config_btn)
    layout.addLayout(btn_layout)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_backup_tab():
    """Create Backup & Snapshots tab"""
    widget = QWidget()
    layout = QVBoxLayout()
    
    # Title
    title = QLabel("Backup & System Snapshots")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)
    
    # Snapshots list
    snapshot_list = QListWidget()
    snapshots = [
        "2026-07-14 12:30 - After updates",
        "2026-07-13 18:00 - Gaming setup",
        "2026-07-10 09:00 - Clean install"
    ]
    for snapshot in snapshots:
        snapshot_list.addItem(snapshot)
    
    layout.addWidget(QLabel("System Snapshots:"))
    layout.addWidget(snapshot_list)
    
    # Backup options
    auto_backup = QCheckBox("Enable Automatic Backups")
    auto_backup.setChecked(True)
    layout.addWidget(auto_backup)
    
    frequency_label = QLabel("Backup Frequency:")
    frequency = QComboBox()
    frequency.addItems(["Daily", "Weekly", "Monthly"])
    frequency.setCurrentIndex(1)
    layout.addWidget(frequency_label)
    layout.addWidget(frequency)
    
    # Buttons
    btn_layout = QHBoxLayout()
    create_btn = QPushButton("Create Snapshot Now")
    restore_btn = QPushButton("Restore Selected")
    btn_layout.addWidget(create_btn)
    btn_layout.addWidget(restore_btn)
    layout.addLayout(btn_layout)
    
    layout.addStretch()
    widget.setLayout(layout)
    return widget


def create_appearance_tab():
    """Create Appearance tab with dark/light theme switching"""
    widget = QWidget()
    layout = QVBoxLayout()

    title = QLabel("Appearance")
    font = title.font()
    font.setPointSize(14)
    font.setBold(True)
    title.setFont(font)
    layout.addWidget(title)

    description = QLabel("Choose the design language used across every Nexus application.")
    description.setWordWrap(True)
    layout.addWidget(description)

    theme_label = QLabel("Theme:")
    layout.addWidget(theme_label)

    theme_combo = QComboBox()
    theme_combo.addItems(["Dark (default)", "Light"])

    def _on_theme_changed(index):
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, mode="light" if index == 1 else "dark")

    theme_combo.currentIndexChanged.connect(_on_theme_changed)
    layout.addWidget(theme_combo)

    accent_note = QLabel("Accent color: Nexus Violet (#7c5cff)")
    layout.addWidget(accent_note)

    layout.addStretch()
    widget.setLayout(layout)
    return widget


class NexusCenterWindow(QMainWindow):
    """Main Nexus Center application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Center")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("Nexus Linux - System Administration")
        font = header.font()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        main_layout.addWidget(header)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(create_system_tab(), "System")
        tabs.addTab(create_desktop_tab(), "Desktops")
        tabs.addTab(create_updates_tab(), "Updates")
        tabs.addTab(create_drivers_tab(), "Drivers")
        tabs.addTab(create_gaming_tab(), "Gaming")
        tabs.addTab(create_backup_tab(), "Backup")
        tabs.addTab(create_appearance_tab(), "Appearance")
        
        main_layout.addWidget(tabs)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
