from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QCheckBox,
)

from nexus_installer.core.account_manager import AccountConfiguration, validate_account


def _password_score(password: str) -> int:
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c.isupper() for c in password) and any(c.islower() for c in password):
        score += 1
    return min(score, 4)


class AccountPage(QWidget):
    title = "Create Your Account"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        header = QLabel("Create your account")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        info = QLabel(
            "This account will be created automatically. Nexus Linux replaces "
            "GNOME's own first-run setup, so you won't be asked again after install."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()

        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Jane Doe")
        self.full_name_input.textChanged.connect(self._suggest_username)
        form.addRow("Full name:", self.full_name_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("jane")
        form.addRow("Username:", self.username_input)

        self.hostname_input = QLineEdit("nexus-linux")
        form.addRow("Computer name:", self.hostname_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self._update_strength)
        form.addRow("Password:", self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        form.addRow("Confirm password:", self.confirm_input)

        layout.addLayout(form)

        self.strength_label = QLabel("Password strength: \u2014")
        layout.addWidget(self.strength_label)

        self.auto_login_checkbox = QCheckBox("Log in automatically")
        layout.addWidget(self.auto_login_checkbox)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff5c5c;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        layout.addStretch()
        self.setLayout(layout)

    def _suggest_username(self, text):
        if not self.username_input.text() and text.strip():
            suggestion = text.strip().lower().split(" ")[0]
            suggestion = "".join(ch for ch in suggestion if ch.isalnum())
            self.username_input.setText(suggestion)

    def _update_strength(self, password):
        labels = ["Very weak", "Weak", "Fair", "Good", "Strong"]
        self.strength_label.setText(f"Password strength: {labels[_password_score(password)]}")

    def _build_account(self) -> AccountConfiguration:
        return AccountConfiguration(
            full_name=self.full_name_input.text().strip(),
            username=self.username_input.text().strip(),
            password=self.password_input.text(),
            hostname=self.hostname_input.text().strip() or "nexus-linux",
            auto_login=self.auto_login_checkbox.isChecked(),
        )

    def is_valid(self) -> bool:
        account = self._build_account()
        ok, message = validate_account(account)
        if not ok:
            self.error_label.setText(message)
            return False
        if account.password != self.confirm_input.text():
            self.error_label.setText("Passwords do not match.")
            return False
        self.error_label.setText("")
        return True

    def collect(self, config):
        config.account = self._build_account()
