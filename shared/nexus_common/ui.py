from pathlib import Path
import sys

try:
    from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
    from PySide6.QtGui import QFont
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


if PYSIDE6_AVAILABLE:
    class NexusBaseWindow(QMainWindow):
        """Base window for all Nexus applications"""
        
        def __init__(self, title: str, description: str):
            super().__init__()
            self.setWindowTitle(f"Nexus - {title}")
            self.setGeometry(100, 100, 800, 600)
            
            # Create central widget
            central_widget = QWidget()
            layout = QVBoxLayout()
            
            # Header
            header = QLabel(f"Nexus Linux - {title}")
            font = header.font()
            font.setPointSize(16)
            font.setBold(True)
            header.setFont(font)
            layout.addWidget(header)
            
            # Description
            desc = QLabel(description)
            layout.addWidget(desc)
            
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)
            self.statusBar().showMessage("Ready")
