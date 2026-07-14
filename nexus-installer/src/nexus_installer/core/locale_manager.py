"""Region, locale, timezone, and keyboard layout handling for Nexus Installer."""

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
