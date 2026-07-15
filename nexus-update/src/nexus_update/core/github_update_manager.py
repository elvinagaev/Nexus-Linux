"""
GitHub-based whole-system update checker for Nexus Update.

Distinct from `update_manager.py`'s apt-based package upgrades: this checks
whether the Nexus Linux project itself (github.com/elvinagaev/Nexus-Linux)
has new commits, and -- only after the user explicitly confirms in the UI --
downloads the latest source tarball and re-syncs it over /opt/nexus-linux,
the same tree every Nexus app's launcher script (see
live-build/config/includes.chroot/usr/local/bin/) runs from.

Uses plain HTTPS + Python's stdlib (urllib/tarfile) instead of `git`, so no
git binary or repository state is needed on the target system, then
`rsync` (already required by the installer's live-filesystem clone step,
so always present) to apply the update -- elevated via `pkexec` since
/opt/nexus-linux is root-owned.
"""

import json
import subprocess
import tarfile
import urllib.request
from pathlib import Path

REPO = "elvinagaev/Nexus-Linux"
BRANCH = "main"
COMMIT_API_URL = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
TARBALL_URL = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.tar.gz"
VERSION_MARKER = Path("/etc/nexus/installed-commit.txt")
OPT_ROOT = Path("/opt/nexus-linux")
# Every app staged into /opt/nexus-linux by live-build/build.sh -- kept in
# sync with that script's STAGE_DIR copy list.
STAGED_APPS = [
    "shared", "nexus-installer", "nexus-center", "nexus-gaming", "nexus-driver",
    "nexus-update", "nexus-shell-manager", "nexus-store", "nexus-backup", "nexus-settings",
]
_REQUEST_HEADERS = {"User-Agent": "nexus-update"}


def get_installed_commit() -> str:
    """Best-effort read of the last commit SHA this system was updated to."""
    try:
        return VERSION_MARKER.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def get_latest_commit(timeout: int = 10) -> str:
    """Best-effort fetch of the latest commit SHA on GitHub. Empty string on failure."""
    try:
        request = urllib.request.Request(COMMIT_API_URL, headers=_REQUEST_HEADERS)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("sha", "")
    except (OSError, ValueError):
        return ""


def check_for_update() -> dict:
    """Returns {"checked": bool, "available": bool, "installed": str, "latest": str}."""
    latest = get_latest_commit()
    installed = get_installed_commit()
    return {
        "checked": bool(latest),
        "available": bool(latest) and latest != installed,
        "installed": installed[:10] if installed else "unknown",
        "latest": latest[:10] if latest else "unknown",
    }


def apply_update_commands() -> list:
    """Display-only preview of what a real update does."""
    return [
        f"curl -L {TARBALL_URL} -o /tmp/nexus-linux-update.tar.gz",
        "tar -xzf /tmp/nexus-linux-update.tar.gz -C /tmp/nexus-linux-update",
    ] + [
        f"rsync -a --delete /tmp/nexus-linux-update/*/{app}/ {OPT_ROOT}/{app}/"
        for app in STAGED_APPS
    ]


def apply_update(dry_run: bool = True) -> str:
    """
    Download the latest Nexus Linux source tarball and re-sync it over
    /opt/nexus-linux. Only ever called after the user explicitly confirms
    in the UI (this project never applies a system update silently).
    """
    latest = get_latest_commit()
    if not latest:
        return "Could not reach GitHub to fetch the update."
    if dry_run:
        return f"Would update Nexus Linux to commit {latest[:10]}."

    download_dir = Path("/tmp/nexus-linux-update")
    archive_path = Path("/tmp/nexus-linux-update.tar.gz")
    request = urllib.request.Request(TARBALL_URL, headers=_REQUEST_HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response:
        archive_path.write_bytes(response.read())

    download_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="r:gz") as archive:
        _safe_extract(archive, download_dir)

    extracted_root = next(download_dir.iterdir())
    for app in STAGED_APPS:
        source = extracted_root / app
        if not source.is_dir():
            continue
        subprocess.run(
            ["pkexec", "rsync", "-a", "--delete", f"{source}/", f"{OPT_ROOT / app}/"],
            check=True,
        )

    subprocess.run(["pkexec", "mkdir", "-p", str(VERSION_MARKER.parent)], check=True)
    subprocess.run(
        ["pkexec", "tee", str(VERSION_MARKER)],
        input=f"{latest}\n", text=True, check=True, stdout=subprocess.DEVNULL,
    )
    return f"Nexus Linux updated to commit {latest[:10]}. Restart apps to use the new version."


def _safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    """Reject any archive member that would extract outside `destination`."""
    destination = destination.resolve()
    for member in archive.getmembers():
        target = (destination / member.name).resolve()
        if destination != target and destination not in target.parents:
            raise ValueError(f"Unsafe path in archive: {member.name}")
    try:
        archive.extractall(destination, filter="data")
    except TypeError:
        archive.extractall(destination)
