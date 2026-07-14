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

if str(_SHARED_ROOT) not in sys.path:
    sys.path.append(str(_SHARED_ROOT))

from . import store_catalog  # noqa: E402

__all__ = ["store_catalog"]
