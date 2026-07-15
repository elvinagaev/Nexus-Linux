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

if _SHARED_ROOT is not None and str(_SHARED_ROOT) not in sys.path:
    sys.path.append(str(_SHARED_ROOT))

from . import driver_catalog  # noqa: E402

__all__ = ["driver_catalog"]
