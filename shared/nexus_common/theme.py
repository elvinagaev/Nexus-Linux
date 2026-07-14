"""
Shared visual theme for all Nexus Linux applications.

Every Nexus app (Center, Installer, Driver Manager, Gaming, ...) applies this
same stylesheet so the whole operating system feels like one coherent
product instead of a collection of unrelated tools. Dark is the default;
light is available for users who prefer it (see Nexus Center > Appearance).
"""

NEXUS_ACCENT = "#7c5cff"
NEXUS_ACCENT_HOVER = "#9375ff"
NEXUS_ACCENT_PRESSED = "#6647e0"

DARK_QSS = f"""
QWidget {{
    background-color: #14151a;
    color: #e6e6e6;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: #14151a;
}}

QLabel {{
    color: #e6e6e6;
    background: transparent;
}}

QPushButton {{
    background-color: {NEXUS_ACCENT};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {NEXUS_ACCENT_HOVER};
}}

QPushButton:pressed {{
    background-color: {NEXUS_ACCENT_PRESSED};
}}

QPushButton:disabled {{
    background-color: #33343d;
    color: #77787f;
}}

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {{
    background-color: #1e1f26;
    border: 1px solid #33343d;
    border-radius: 6px;
    padding: 6px;
    color: #e6e6e6;
    selection-background-color: {NEXUS_ACCENT};
}}

QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {NEXUS_ACCENT};
}}

QTabWidget::pane {{
    border: 1px solid #2a2b33;
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background: #1e1f26;
    color: #b7b8c2;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background: {NEXUS_ACCENT};
    color: #ffffff;
}}

QListWidget, QTableWidget {{
    background-color: #1a1b21;
    border: 1px solid #2a2b33;
    border-radius: 6px;
    gridline-color: #2a2b33;
}}

QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: {NEXUS_ACCENT};
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: #1e1f26;
    color: #b7b8c2;
    padding: 6px;
    border: none;
}}

QProgressBar {{
    background-color: #1e1f26;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {NEXUS_ACCENT};
    border-radius: 6px;
}}

QCheckBox, QRadioButton {{
    spacing: 8px;
}}

QStatusBar {{
    background-color: #1a1b21;
    color: #b7b8c2;
}}

QScrollBar:vertical {{
    background: #1a1b21;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: #33343d;
    border-radius: 5px;
}}
"""

LIGHT_QSS = f"""
QWidget {{
    background-color: #f5f6fa;
    color: #1c1d21;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: #f5f6fa;
}}

QPushButton {{
    background-color: {NEXUS_ACCENT};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {NEXUS_ACCENT_PRESSED};
}}

QPushButton:disabled {{
    background-color: #d7d8e0;
    color: #9a9ba3;
}}

QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {{
    background-color: #ffffff;
    border: 1px solid #d7d8e0;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: {NEXUS_ACCENT};
}}

QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {NEXUS_ACCENT};
}}

QTabWidget::pane {{
    border: 1px solid #d7d8e0;
    border-radius: 8px;
}}

QTabBar::tab {{
    background: #ffffff;
    color: #57585f;
    padding: 8px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background: {NEXUS_ACCENT};
    color: #ffffff;
}}

QListWidget, QTableWidget {{
    background-color: #ffffff;
    border: 1px solid #d7d8e0;
    border-radius: 6px;
}}

QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: {NEXUS_ACCENT};
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: #eef0f6;
    color: #57585f;
    padding: 6px;
    border: none;
}}

QProgressBar {{
    background-color: #e7e8ef;
    border-radius: 6px;
    text-align: center;
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {NEXUS_ACCENT};
    border-radius: 6px;
}}

QStatusBar {{
    background-color: #eef0f6;
    color: #57585f;
}}
"""

THEMES = {"dark": DARK_QSS, "light": LIGHT_QSS}


def apply_theme(app, mode: str = "dark") -> None:
    """Apply the shared Nexus Linux stylesheet to a QApplication instance."""
    app.setStyleSheet(THEMES.get(mode, DARK_QSS))
