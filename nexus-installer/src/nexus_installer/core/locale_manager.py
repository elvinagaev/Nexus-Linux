"""Region, locale, timezone, and keyboard layout handling for Nexus Installer."""

import subprocess
from pathlib import Path
import sys

_REPO_ROOT_MARKER = Path(__file__).resolve()
for _ in range(10):
    if (_REPO_ROOT_MARKER / "shared" / "nexus_common").exists():
        break
    _REPO_ROOT_MARKER = _REPO_ROOT_MARKER.parent
_SHARED_ROOT = _REPO_ROOT_MARKER / "shared"
if str(_SHARED_ROOT) not in sys.path:
    sys.path.append(str(_SHARED_ROOT))

from nexus_common.constants import REGIONS


def get_regions() -> list:
    return REGIONS


def find_region(name: str):
    for region in REGIONS:
        if region["region"] == name:
            return region
    return None


def apply_locale_commands(region: dict) -> list:
    """Build the shell commands needed to apply locale/timezone/keyboard settings."""
    return [
        f"locale-gen {region['locale']}",
        f"update-locale LANG={region['locale']}",
        f"ln -sf /usr/share/zoneinfo/{region['timezone']} /etc/localtime",
        f"echo '{region['timezone']}' > /etc/timezone",
        f"localectl set-x11-keymap {region['keyboard']}",
    ]


def apply_locale(region: dict, target_root: str | None = None) -> None:
    """
    Actually apply locale/timezone/keyboard settings. Never invoked during
    simulation/dry-run. Elevated via `pkexec` (the installer runs as a
    normal user, not root); `localectl`'s X11 keymap step is best-effort
    since it talks to systemd over D-Bus and may not work inside a chroot
    with no running D-Bus session -- timezone is set by writing
    /etc/localtime + /etc/timezone directly instead, for the same reason
    (and so no shell is ever needed for the redirection/symlink).
    """
    prefix = ["pkexec"]
    if target_root:
        prefix = prefix + ["chroot", target_root]

    subprocess.run([*prefix, "locale-gen", region["locale"]], check=True)
    subprocess.run([*prefix, "update-locale", f"LANG={region['locale']}"], check=True)
    subprocess.run(
        [*prefix, "ln", "-sfn", f"/usr/share/zoneinfo/{region['timezone']}", "/etc/localtime"],
        check=True,
    )
    subprocess.run(
        [*prefix, "tee", "/etc/timezone"],
        input=f"{region['timezone']}\n", text=True, check=True, stdout=subprocess.DEVNULL,
    )
    try:
        subprocess.run([*prefix, "localectl", "set-x11-keymap", region["keyboard"]], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
