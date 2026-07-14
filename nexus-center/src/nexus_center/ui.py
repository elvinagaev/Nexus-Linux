"""
Nexus Center main application UI built with PySide6.
Provides a central hub for system settings and administration.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTabWidget, QStackedWidget, QListWidget,
        QListWidgetItem, QFrame
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon, QFont, QColor
except ImportError:
    print("PySide6 not installed. Install with: pip install PySide6")
    sys.exit(1)

# Add parent paths for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared"
if str(SHARED_ROOT) not in sys.path:
    sys.path.insert(0, str(SHARED_ROOT))

from nexus_common.constants import SUPPORTED_DESKTOPS


class SettingsPanel(QFrame):
    """Base panel for settings sections."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 4px; }")

    def add_widget(self, widget):
        self.layout.addWidget(widget)


class SystemSettingsPanel(SettingsPanel):
    """System settings panel."""

    def __init__(self, parent=None):
        super().__init__("System Settings", parent)
        
        title = QLabel("System Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        self.add_widget(title)

        self.add_widget(QLabel("Hostname:"))
        hostname_btn = QPushButton("Configure")
        self.add_widget(hostname_btn)

        self.add_widget(QLabel("Time & Date:"))
        time_btn = QPushButton("Configure")
        self.add_widget(time_btn)

        self.layout.addStretch()


class DesktopEnvironmentPanel(SettingsPanel):
    """Desktop environment management panel."""

    def __init__(self, parent=None):
        super().__init__("Desktop Environments", parent)
        
        title = QLabel("Desktop Environments")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        self.add_widget(title)

        self.add_widget(QLabel("Installed:"))
        
        self.de_list = QListWidget()
        for slug, name in SUPPORTED_DESKTOPS.items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, slug)
            self.de_list.addItem(item)
        self.add_widget(self.de_list)

        button_layout = QHBoxLayout()
        install_btn = QPushButton("Install")
        remove_btn = QPushButton("Remove")
        set_default_btn = QPushButton("Set as Default")
        
        button_layout.addWidget(install_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(set_default_btn)
        
        self.layout.addLayout(button_layout)
        self.layout.addStretch()


class UpdatesPanel(SettingsPanel):
    """Updates and maintenance panel."""

    def __init__(self, parent=None):
        super().__init__("Updates", parent)
        
        title = QLabel("Updates & Maintenance")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        self.add_widget(title)

        self.add_widget(QLabel("System updates available: 5"))
        
        check_btn = QPushButton("Check for Updates")
        self.add_widget(check_btn)

        update_btn = QPushButton("Install All Updates")
        self.add_widget(update_btn)

        self.add_widget(QLabel("Kernel:"))
        kernel_btn = QPushButton("Manage Kernels")
        self.add_widget(kernel_btn)

        self.layout.addStretch()


class NexusCenterWindow(QMainWindow):
    """Main Nexus Center application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Center")
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left sidebar for navigation
        sidebar_layout = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar_layout)
        sidebar_frame.setMaximumWidth(200)
        sidebar_frame.setStyleSheet("QFrame { background-color: #2c3e50; }")

        sidebar_title = QLabel("Nexus Center")
        sidebar_title_font = QFont()
        sidebar_title_font.setPointSize(12)
        sidebar_title_font.setBold(True)
        sidebar_title.setFont(sidebar_title_font)
        sidebar_title.setStyleSheet("color: white;")
        sidebar_layout.addWidget(sidebar_title)

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("System", SystemSettingsPanel),
            ("Desktops", DesktopEnvironmentPanel),
            ("Updates", UpdatesPanel),
        ]

        self.stacked_widget = QStackedWidget()

        for name, panel_class in nav_items:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    border: none;
                    padding: 8px;
                    text-align: left;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3d5a73;
                }
            """)
            btn.clicked.connect(lambda checked=False, n=name: self.switch_panel(n))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn

            # Create and register panel
            panel = panel_class()
            self.stacked_widget.addWidget(panel)

        sidebar_layout.addStretch()

        # Right content area
        content_frame = QFrame()
        content_layout = QVBoxLayout()
        content_frame.setLayout(content_layout)
        content_layout.addWidget(self.stacked_widget)

        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(content_frame, 1)

        # Set initial panel
        self.switch_panel("System")

    def switch_panel(self, panel_name: str):
        """Switch to a different settings panel."""
        index = list(self.nav_buttons.keys()).index(panel_name)
        self.stacked_widget.setCurrentIndex(index)
        
        # Highlight active button
        for name, btn in self.nav_buttons.items():
            if name == panel_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 8px;
                        text-align: left;
                        border-radius: 4px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #34495e;
                        color: white;
                        border: none;
                        padding: 8px;
                        text-align: left;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #3d5a73;
                    }
                """)

    def apply_styling(self):
        """Apply application-wide styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)


def main():
    """Entry point for Nexus Center application."""
    app = QApplication(sys.argv)
    window = NexusCenterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
