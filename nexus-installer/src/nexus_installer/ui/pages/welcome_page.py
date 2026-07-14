from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class WelcomePage(QWidget):
    title = "Welcome"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Welcome to Nexus Linux")
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(header)

        description = QLabel(
            "This wizard will guide you through installing Nexus Linux.\n\n"
            "You will choose your region, desktop environment, usage profile, "
            "and disk layout. GNOME is installed automatically by default and "
            "can be changed later using Nexus Shell Manager."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        layout.addStretch()

        self.setLayout(layout)

    def is_valid(self) -> bool:
        return True

    def collect(self, config):
        pass
