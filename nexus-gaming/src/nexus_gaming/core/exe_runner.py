"""
Simple "run a Windows .exe with Wine" launcher for Nexus Gaming.

Runs entirely as the current user (Wine never needs root), and always
passes the executable path as a single argv item -- never through a
shell -- so there is no command-injection risk regardless of what the
file is named.
"""

import shutil
import subprocess


def is_wine_available() -> bool:
    return shutil.which("wine") is not None


def run_exe(path: str) -> tuple:
    """Launch `path` under Wine in the background. Returns (started, message)."""
    if not is_wine_available():
        return False, "Wine is not installed yet -- install it from the list above first."
    try:
        subprocess.Popen(["wine", path])
    except OSError as exc:
        return False, f"Could not launch: {exc}"
    return True, f"Launching {path} with Wine..."
