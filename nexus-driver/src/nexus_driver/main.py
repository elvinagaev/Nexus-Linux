import sys

try:
    from PySide6.QtWidgets import QApplication
    from .ui import NexusDriverWindow
    from nexus_common.theme import apply_theme
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


def main() -> int:
    if not PYSIDE6_AVAILABLE:
        print("ERROR: PySide6 is not installed.")
        print("Install it with: pip install PySide6")
        return 1

    app = QApplication(sys.argv)
    apply_theme(app, mode="dark")
    window = NexusDriverWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
