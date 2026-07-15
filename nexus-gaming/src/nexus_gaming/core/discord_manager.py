"""
Discord installer for Nexus Gaming.

Discord does not publish an apt repository, so unlike the rest of
GAMING_CATALOG (plain `apt-get install` from Debian's own repos), it ships
as a standalone .deb from Discord's own official download endpoint. This
downloads that .deb to a world-readable temp path and installs it with
`apt-get install` (not raw `dpkg -i`) so apt still resolves any missing
runtime dependencies -- elevated via `pkexec` with `DEBIAN_FRONTEND=
noninteractive` like every other real install action in this project.
"""

import subprocess
import urllib.request
from pathlib import Path

DISCORD_DEB_URL = "https://discord.com/api/download?platform=linux&format=deb"
# /tmp is world-readable by default regardless of the calling user's home
# directory permissions, so the pkexec'd (root) apt-get call below can
# always read the file this unprivileged download wrote.
DOWNLOAD_PATH = Path("/tmp/nexus-gaming-discord.deb")


def install_commands() -> list:
    """Display-only preview of what a real install does."""
    return [
        f"curl -L {DISCORD_DEB_URL} -o {DOWNLOAD_PATH}",
        "apt-get install -y -o Dpkg::Options::=--force-confdef "
        f"-o Dpkg::Options::=--force-confold {DOWNLOAD_PATH}",
    ]


def install_discord(dry_run: bool = True) -> str:
    """Download the current Discord .deb and install it for real."""
    if dry_run:
        return "Would download and install the latest Discord .deb."

    request = urllib.request.Request(DISCORD_DEB_URL, headers={"User-Agent": "nexus-gaming"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            DOWNLOAD_PATH.write_bytes(response.read())
    except OSError as exc:
        return f"Could not download Discord: {exc}"

    subprocess.run(
        [
            "pkexec", "env", "DEBIAN_FRONTEND=noninteractive",
            "apt-get", "install", "-y",
            "-o", "Dpkg::Options::=--force-confdef",
            "-o", "Dpkg::Options::=--force-confold",
            str(DOWNLOAD_PATH),
        ],
        check=True,
    )
    return "Discord installed."
