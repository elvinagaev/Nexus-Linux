from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPlainTextEdit
from PySide6.QtCore import Signal

from nexus_installer.core.install_engine import InstallEngine, PYSIDE6_AVAILABLE


class ProgressPage(QWidget):
    title = "Installing Nexus Linux"
    install_finished = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_finished = False
        self.engine = None

        layout = QVBoxLayout()

        header = QLabel("Installing Nexus Linux")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        self.status_label = QLabel("Waiting to start...")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        layout.addWidget(QLabel("Installation log:"))
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.setLayout(layout)

    def start_installation(self):
        if self.engine is not None:
            return  # already started, avoid double-running

        self.is_finished = False
        self.log_view.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting installation...")

        self.engine = InstallEngine(self.config)
        self.engine.step_started.connect(self._on_step_started)
        self.engine.step_progress.connect(self.progress_bar.setValue)
        self.engine.step_failed.connect(self._on_step_failed)
        self.engine.log_message.connect(self.log_view.appendPlainText)
        self.engine.finished_install.connect(self._on_finished)

        if PYSIDE6_AVAILABLE:
            self.engine.start()
        else:
            self.engine.run()

    def _on_step_started(self, step_id, label):
        self.status_label.setText(label)

    def _on_step_failed(self, step_id, message):
        self.status_label.setText(f"Installation failed at: {step_id}")

    def _on_finished(self):
        self.is_finished = True
        self.status_label.setText("Installation complete!")
        self.install_finished.emit()

    def is_valid(self) -> bool:
        return self.is_finished
