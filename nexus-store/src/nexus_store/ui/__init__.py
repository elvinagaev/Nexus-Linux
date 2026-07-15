from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path | None:
    current = start
    for _ in range(10):
        if (current / "shared" / "nexus_common").exists():
            return current
        current = current.parent
    # Not running from within the repo (e.g. a real installed package) --
    # nexus_common must already be installed as a normal dependency.
    return None


_REPO_ROOT = _find_repo_root(Path(__file__).resolve())
_SHARED_ROOT = _REPO_ROOT / "shared" if _REPO_ROOT is not None else None
_SRC_ROOT = _REPO_ROOT / "nexus-store" / "src" if _REPO_ROOT is not None else None

for _path in (_SHARED_ROOT, _SRC_ROOT):
    if _path is not None and str(_path) not in sys.path:
        sys.path.append(str(_path))

from .main_window import NexusStoreWindow  # noqa: E402

__all__ = ["NexusStoreWindow"]
