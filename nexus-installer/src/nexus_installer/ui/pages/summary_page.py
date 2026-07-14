from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SummaryPage(QWidget):
    title = "Installation Complete"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Nexus Linux is ready!")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(header)

        message = QLabel(
            "Your system has been installed with GNOME as the default desktop.\n"
            "Remove the installation media and restart to start using Nexus Linux.\n\n"
            "Use Nexus Shell Manager anytime to install or switch to another desktop, "
            "and Nexus Center to manage updates, drivers, and gaming tools."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        layout.addStretch()

        self.setLayout(layout)

    def is_valid(self) -> bool:
        return True

    def collect(self, config):
        pass
