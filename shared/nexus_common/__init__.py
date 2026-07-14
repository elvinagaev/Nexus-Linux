from .base import NexusApplication, NexusApplicationInfo
from .constants import APP_REGISTRY, SUPPORTED_DESKTOPS, get_desktop_display_name

try:
    from .ui import NexusBaseWindow
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

__all__ = [
    "NexusApplication",
    "NexusApplicationInfo",
    "APP_REGISTRY",
    "SUPPORTED_DESKTOPS",
    "get_desktop_display_name",
    "NexusBaseWindow",
    "UI_AVAILABLE",
]
