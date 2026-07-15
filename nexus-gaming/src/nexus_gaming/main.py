import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from .ui import NexusGamingWindow
    from nexus_common.theme import apply_theme
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


def _disable_welcome_autostart() -> None:
    """Remove the one-shot autostart entry the installer writes for a new
    account (see nexus_installer.core.account_manager) so this welcome
    launch only ever happens once per account, regardless of whether the
    user closes the window or opens Nexus Gaming manually later."""
    marker = Path.home() / ".config" / "autostart" / "nexus-gaming-welcome.desktop"
    try:
        marker.unlink(missing_ok=True)
    except OSError:
        pass


def main() -> int:
    if not PYSIDE6_AVAILABLE:
        print("ERROR: PySide6 is not installed.")
        print("Install it with: pip install PySide6")
        return 1

    _disable_welcome_autostart()
    app = QApplication(sys.argv)
    apply_theme(app, mode="dark")
    window = NexusGamingWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
