"""
Shared package prefetch/cache manager used by Nexus Driver and Nexus Gaming.

The idea: downloading .deb packages ahead of time (while the user is still
browsing the list, or right after first boot) means the actual "Install"
button click just applies already-downloaded files from the local cache --
making the perceived install time almost instant instead of waiting on a
full network download.
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PySide6.QtCore import QThread, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

    class QThread:  # type: ignore
        """Fallback used when PySide6 is unavailable; run() is called directly."""

        def start(self):
            self.run()


CACHE_ROOT = Path("/var/cache/nexus/packages")


@dataclass
class CacheablePackage:
    id: str
    name: str
    packages: list = field(default_factory=list)
    description: str = ""


def is_cached(item: CacheablePackage) -> bool:
    """Best-effort check for whether an item's .deb files are already cached."""
    if not item.packages:
        return True
    if sys.platform != "linux" or not CACHE_ROOT.exists():
        return False
    cached_names = {path.name.split("_")[0] for path in CACHE_ROOT.glob("*.deb")}
    return all(pkg in cached_names for pkg in item.packages)


def default_dry_run() -> bool:
    """Whether install/prefetch actions should simulate instead of executing.

    Real package operations only make sense on Linux; everywhere else (e.g.
    this Windows dev machine) they must stay simulated. The NEXUS_DRY_RUN
    environment variable always takes priority when set -- this lets tests
    (including headless GUI smoke tests running on a real Linux CI runner,
    which has no pkexec/polkit session available) force simulation instead
    of relying on the platform check.
    """
    override = os.environ.get("NEXUS_DRY_RUN")
    if override is not None:
        return override.strip().lower() not in ("0", "false", "")
    return sys.platform != "linux"


def install_from_cache(item: CacheablePackage, dry_run: bool = True) -> list:
    """Build (and optionally run) the install command using only the local cache.

    Real execution is elevated via `pkexec` -- GUI apps run as a normal user,
    and `apt-get` requires root, so without this the command would just fail
    silently (or with a permission error) instead of prompting for auth.
    """
    if not item.packages:
        return []
    command = [
        "apt-get", "install", "-y", "--no-download",
        "-o", f"Dir::Cache::Archives={CACHE_ROOT}",
        "-o", "Dpkg::Options::=--force-confdef",
        "-o", "Dpkg::Options::=--force-confold",
        *item.packages,
    ]
    if not dry_run:
        subprocess.run(["pkexec", "env", "DEBIAN_FRONTEND=noninteractive", *command], check=True)
    return [" ".join(command)]


class PackagePrefetcher(QThread if PYSIDE6_AVAILABLE else object):
    """Downloads a list of CacheablePackage items in the background."""

    if PYSIDE6_AVAILABLE:
        item_started = Signal(str)
        item_progress = Signal(str, int)
        item_cached = Signal(str)
        item_failed = Signal(str, str)
        all_finished = Signal()

    def __init__(self, items):
        if PYSIDE6_AVAILABLE:
            super().__init__()
        self.items = list(items)
        self._simulate = default_dry_run()

    def run(self):
        for item in self.items:
            self._emit_started(item.id)
            try:
                self._prefetch(item)
            except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed
                self._emit_failed(item.id, str(exc))
                continue
            self._emit_cached(item.id)
        self._emit_all_finished()

    def _prefetch(self, item: CacheablePackage):
        if not item.packages:
            if self._simulate:
                time.sleep(0.2)
            self._emit_progress(item.id, 100)
            return

        if self._simulate:
            for percent in (20, 45, 70, 90, 100):
                self._emit_progress(item.id, percent)
                time.sleep(0.1)
            return

        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        command = [
            "apt-get", "install", "--download-only", "-y",
            "-o", f"Dir::Cache::Archives={CACHE_ROOT}",
            *item.packages,
        ]
        subprocess.run(["pkexec", "env", "DEBIAN_FRONTEND=noninteractive", *command], check=True)
        self._emit_progress(item.id, 100)

    def _emit_started(self, item_id):
        if PYSIDE6_AVAILABLE:
            self.item_started.emit(item_id)

    def _emit_progress(self, item_id, percent):
        if PYSIDE6_AVAILABLE:
            self.item_progress.emit(item_id, percent)

    def _emit_cached(self, item_id):
        if PYSIDE6_AVAILABLE:
            self.item_cached.emit(item_id)

    def _emit_failed(self, item_id, message):
        if PYSIDE6_AVAILABLE:
            self.item_failed.emit(item_id, message)

    def _emit_all_finished(self):
        if PYSIDE6_AVAILABLE:
            self.all_finished.emit()
