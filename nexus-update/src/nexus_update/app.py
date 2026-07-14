from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_ROOT = REPO_ROOT / "shared"
if str(SHARED_ROOT) not in sys.path:
    sys.path.append(str(SHARED_ROOT))

from nexus_common.base import NexusApplication, NexusApplicationInfo


def build_app() -> NexusApplication:
    info = NexusApplicationInfo(
        name="Nexus Update",
        slug="nexus-update",
        description="Update, rollback, and kernel management.",
        category="system",
    )
    return NexusApplication(info)
