from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QButtonGroup

from nexus_common.constants import INSTALL_PROFILES


class ProfilePage(QWidget):
    title = "Installation Profile"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Select an installation profile")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        self.button_group = QButtonGroup(self)
        for index, (slug, profile) in enumerate(INSTALL_PROFILES.items()):
            radio = QRadioButton(f"{profile['name']} \u2014 {profile['description']}")
            radio.setProperty("slug", slug)
            if slug == "minimal":
                radio.setChecked(True)
            self.button_group.addButton(radio, index)
            layout.addWidget(radio)

        layout.addStretch()
        self.setLayout(layout)

    def is_valid(self) -> bool:
        return self.button_group.checkedButton() is not None

    def collect(self, config):
        button = self.button_group.checkedButton()
        config.profile = button.property("slug") if button else "minimal"
