from pathlib import Path
import sys


def _find_repo_root(start: Path) -> Path:
    current = start
    for _ in range(10):
        if (current / "shared" / "nexus_common").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not locate the Nexus Linux repository root")


_REPO_ROOT = _find_repo_root(Path(__file__).resolve())
_SHARED_ROOT = _REPO_ROOT / "shared"
_SRC_ROOT = _REPO_ROOT / "nexus-shell-manager" / "src"

for _path in (_SHARED_ROOT, _SRC_ROOT):
    if str(_path) not in sys.path:
        sys.path.append(str(_path))

from .main_window import NexusShellManagerWindow  # noqa: E402

__all__ = ["NexusShellManagerWindow"]
