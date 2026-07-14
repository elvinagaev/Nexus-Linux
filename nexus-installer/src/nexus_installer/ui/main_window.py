import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
        QPushButton, QLabel,
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

from nexus_installer.core.install_engine import InstallConfiguration
from .pages import (
    WelcomePage, RegionPage, DesktopPage, ProfilePage,
    PartitionPage, AccountPage, ProgressPage, SummaryPage,
)


class NexusInstallerWindow(QMainWindow):
    """Wizard-style main window driving the Nexus Linux installation flow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Installer")
        self.setGeometry(100, 100, 900, 650)

        self.config = InstallConfiguration()

        central = QWidget()
        main_layout = QVBoxLayout()

        self.stack = QStackedWidget()
        self.welcome_page = WelcomePage()
        self.region_page = RegionPage()
        self.desktop_page = DesktopPage()
        self.profile_page = ProfilePage()
        self.partition_page = PartitionPage()
        self.account_page = AccountPage()
        self.progress_page = ProgressPage(self.config)
        self.summary_page = SummaryPage()

        self.pages = [
            self.welcome_page,
            self.region_page,
            self.desktop_page,
            self.profile_page,
            self.partition_page,
            self.account_page,
            self.progress_page,
            self.summary_page,
        ]
        for page in self.pages:
            self.stack.addWidget(page)

        main_layout.addWidget(self.stack)

        nav_layout = QHBoxLayout()
        self.step_label = QLabel()
        nav_layout.addWidget(self.step_label)
        nav_layout.addStretch()
        self.back_btn = QPushButton("Back")
        self.next_btn = QPushButton("Next")
        self.back_btn.clicked.connect(self._go_back)
        self.next_btn.clicked.connect(self._go_next)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.next_btn)
        main_layout.addLayout(nav_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.progress_page.install_finished.connect(self._on_install_finished)

        self.current_index = 0
        self._update_navigation()

    def _update_navigation(self):
        page = self.pages[self.current_index]
        self.step_label.setText(f"Step {self.current_index + 1} of {len(self.pages)}: {page.title}")

        is_progress_page = page is self.progress_page
        self.back_btn.setEnabled(self.current_index > 0 and not is_progress_page)
        self.next_btn.setEnabled(not is_progress_page or self.progress_page.is_finished)
        self.next_btn.setText("Finish" if page is self.summary_page else "Next")

    def _go_next(self):
        page = self.pages[self.current_index]
        if hasattr(page, "is_valid") and not page.is_valid():
            return
        if hasattr(page, "collect"):
            page.collect(self.config)

        if page is self.summary_page:
            self.close()
            return

        self.current_index += 1
        self.stack.setCurrentIndex(self.current_index)

        if self.pages[self.current_index] is self.progress_page:
            self.progress_page.start_installation()

        self._update_navigation()

    def _go_back(self):
        if self.current_index == 0:
            return
        self.current_index -= 1
        self.stack.setCurrentIndex(self.current_index)
        self._update_navigation()

    def _on_install_finished(self):
        self._update_navigation()
