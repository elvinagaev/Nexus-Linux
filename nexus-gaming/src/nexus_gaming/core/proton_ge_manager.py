"""
Proton-GE (GloriousEggroll's Proton build) installer for Nexus Gaming.

Proton-GE is not an apt package -- it is distributed as GitHub release
tarballs (github.com/GloriousEggroll/proton-ge-custom, the de-facto
standard distribution channel also used by Lutris/ProtonUp-Qt/Steam Deck
communities) that Steam automatically detects once extracted into
`~/.steam/root/compatibilitytools.d/`. No root privileges are needed since
everything lives under the user's own home directory.
"""

import io
import json
import tarfile
import urllib.request
from pathlib import Path

RELEASES_API_URL = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
COMPAT_TOOLS_DIR = Path.home() / ".steam" / "root" / "compatibilitytools.d"
_REQUEST_HEADERS = {"User-Agent": "nexus-gaming", "Accept": "application/vnd.github+json"}


def get_latest_release() -> dict | None:
    """Best-effort fetch of the latest Proton-GE release's tag + tarball URL."""
    try:
        request = urllib.request.Request(RELEASES_API_URL, headers=_REQUEST_HEADERS)
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError):
        return None

    tag = data.get("tag_name")
    asset_url = next(
        (asset["browser_download_url"] for asset in data.get("assets", [])
         if asset.get("name", "").endswith(".tar.gz")),
        None,
    )
    if not tag or not asset_url:
        return None
    return {"tag": tag, "url": asset_url}


def is_installed(tag: str) -> bool:
    return (COMPAT_TOOLS_DIR / tag).is_dir()


def install_latest(dry_run: bool = True) -> str:
    """Download and extract the latest Proton-GE release. Returns a status message."""
    release = get_latest_release()
    if release is None:
        return "Could not reach GitHub to check for the latest Proton-GE release."
    if is_installed(release["tag"]):
        return f"Proton-GE {release['tag']} is already installed."
    if dry_run:
        return f"Would download and install Proton-GE {release['tag']}."

    COMPAT_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(release["url"], headers=_REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response:
        archive_bytes = response.read()

    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        _safe_extract(archive, COMPAT_TOOLS_DIR)

    return f"Proton-GE {release['tag']} installed. Restart Steam to see it under Compatibility."


def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    """Extract while rejecting any member that would escape `destination`
    (defends against path traversal in a maliciously crafted archive)."""
    destination = destination.resolve()
    for member in archive.getmembers():
        target = (destination / member.name).resolve()
        if destination != target and destination not in target.parents:
            raise ValueError(f"Unsafe path in archive: {member.name}")
    try:
        archive.extractall(destination, filter="data")
    except TypeError:
        # Python < 3.12 doesn't support the `filter` kwarg; every member's
        # path was already validated above, so extraction is still safe.
        archive.extractall(destination)
