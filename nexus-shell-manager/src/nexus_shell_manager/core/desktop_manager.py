"""
Desktop environment lifecycle management for Nexus Shell Manager.

Maps each supported desktop slug to its real Debian/Ubuntu package name
(matching the mapping used by debian/install.d/10-desktop-setup.sh so the
live install and post-install management stay consistent), and builds the
install/remove/switch commands. Real execution is elevated via `pkexec`,
matching the pattern used by shared/nexus_common/package_cache.py.
"""

import subprocess
from pathlib import Path

DESKTOP_PACKAGES = {
    "gnome": "ubuntu-gnome-desktop",
    "hyprland": "hyprland",
    "kde": "kde-standard",
    "xfce": "xfce4",
    "cinnamon": "cinnamon-desktop-environment",
    "cosmic": "cosmic-desktop",
    "mate": "mate-desktop-environment",
    "lxqt": "lxqt",
    "sway": "sway",
    "i3": "i3",
}

DISPLAY_MANAGERS = ["gdm3", "sddm", "lightdm"]
SESSION_TYPES = ["Wayland", "X11"]

DESKTOP_SELECTION_FILE = "/etc/nexus/desktop-selection.conf"


def package_for(slug: str) -> str:
    return DESKTOP_PACKAGES.get(slug, slug)


def install_commands(slug: str) -> list:
    package = package_for(slug)
    return [
        "apt-get install -y -o Dpkg::Options::=--force-confdef "
        f"-o Dpkg::Options::=--force-confold {package}"
    ]


def remove_commands(slug: str) -> list:
    package = package_for(slug)
    return [f"apt-get remove -y {package}"]


def switch_commands(slug: str) -> list:
    return [
        "mkdir -p /etc/nexus",
        f"echo 'desktop={slug}' > {DESKTOP_SELECTION_FILE}",
        "systemctl restart display-manager",
    ]


def configure_display_manager_commands(display_manager: str) -> list:
    return [f"dpkg-reconfigure {display_manager}"]


def run_commands(commands: list, dry_run: bool) -> None:
    """Execute a list of shell commands, elevated via pkexec, unless dry_run.

    DEBIAN_FRONTEND=noninteractive stops apt/dpkg from blocking on a debconf
    question (e.g. picking a default display manager when switching desktop
    environments pulls in sddm/lightdm alongside the existing gdm3) that has
    no tty to be answered on here.
    """
    if dry_run:
        return
    for command in commands:
        subprocess.run(["pkexec", "env", "DEBIAN_FRONTEND=noninteractive", "sh", "-c", command], check=True)


def read_active_desktop() -> str:
    """Best-effort read of the currently configured desktop, defaulting to gnome."""
    path = Path(DESKTOP_SELECTION_FILE)
    if not path.exists():
        return "gnome"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("desktop="):
            return line.split("=", 1)[1].strip() or "gnome"
    return "gnome"
