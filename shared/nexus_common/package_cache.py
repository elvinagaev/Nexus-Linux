"""
Shared package prefetch/cache manager used by Nexus Driver and Nexus Gaming.

The idea: downloading .deb packages ahead of time (while the user is still
browsing the list, or right after first boot) means the actual "Install"
button click just applies already-downloaded files from the local cache --
making the perceived install time almost instant instead of waiting on a
full network download.
"""

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


def install_from_cache(item: CacheablePackage, dry_run: bool = True) -> list:
    """Build (and optionally run) the install command using only the local cache."""
    if not item.packages:
        return []
    command = [
        "apt-get", "install", "-y", "--no-download",
        "-o", f"Dir::Cache::Archives={CACHE_ROOT}",
        *item.packages,
    ]
    if not dry_run:
        subprocess.run(command, check=True)
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
        self._simulate = sys.platform != "linux"

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
        subprocess.run(command, check=True)
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
