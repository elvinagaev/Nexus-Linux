SUPPORTED_DESKTOPS = {
    "gnome": "GNOME",
    "hyprland": "Hyprland",
    "kde": "KDE Plasma",
    "xfce": "XFCE",
    "cinnamon": "Cinnamon",
    "cosmic": "COSMIC",
    "mate": "MATE",
    "lxqt": "LXQt",
    "sway": "Sway",
    "i3": "i3",
}

# GNOME is installed automatically during first install for maximum compatibility.
# Hyprland is flagged as the recommended choice for users who want to switch later
# via Nexus Shell Manager.
DEFAULT_DESKTOP = "gnome"
RECOMMENDED_DESKTOP = "hyprland"

APP_REGISTRY = {
    "nexus-center": "System settings and administration",
    "nexus-shell-manager": "Desktop environment lifecycle management",
    "nexus-installer": "Installation and profile selection",
    "nexus-update": "Update, rollback, and kernel maintenance",
    "nexus-driver": "Driver and firmware management",
    "nexus-store": "Application marketplace",
    "nexus-backup": "Snapshots and restore workflows",
    "nexus-gaming": "Gaming configuration and compatibility",
    "nexus-settings": "System preference management",
}

INSTALL_PROFILES = {
    "gaming": {
        "name": "Gaming",
        "description": "Steam, Proton, Wine, Lutris, MangoHud, and GameMode pre-installed",
        "packages": ["steam", "wine", "lutris", "mangohud", "gamemode"],
    },
    "developer": {
        "name": "Developer",
        "description": "Git, build tools, containers, and popular editors",
        "packages": ["git", "build-essential", "docker.io", "code"],
    },
    "office": {
        "name": "Office",
        "description": "LibreOffice, email client, and productivity tools",
        "packages": ["libreoffice", "thunderbird"],
    },
    "minimal": {
        "name": "Minimal",
        "description": "Bare essentials only; install extras later from Nexus Store",
        "packages": [],
    },
}

# Curated list of regions used by the installer's region/language step.
# Each entry provides the locale, timezone, and keyboard layout to apply.
REGIONS = [
    {"region": "United States", "locale": "en_US.UTF-8", "timezone": "America/New_York", "keyboard": "us"},
    {"region": "United Kingdom", "locale": "en_GB.UTF-8", "timezone": "Europe/London", "keyboard": "gb"},
    {"region": "Germany", "locale": "de_DE.UTF-8", "timezone": "Europe/Berlin", "keyboard": "de"},
    {"region": "France", "locale": "fr_FR.UTF-8", "timezone": "Europe/Paris", "keyboard": "fr"},
    {"region": "Russia", "locale": "ru_RU.UTF-8", "timezone": "Europe/Moscow", "keyboard": "ru"},
    {"region": "Spain", "locale": "es_ES.UTF-8", "timezone": "Europe/Madrid", "keyboard": "es"},
    {"region": "Brazil", "locale": "pt_BR.UTF-8", "timezone": "America/Sao_Paulo", "keyboard": "br"},
    {"region": "Japan", "locale": "ja_JP.UTF-8", "timezone": "Asia/Tokyo", "keyboard": "jp"},
    {"region": "China", "locale": "zh_CN.UTF-8", "timezone": "Asia/Shanghai", "keyboard": "cn"},
    {"region": "India", "locale": "en_IN.UTF-8", "timezone": "Asia/Kolkata", "keyboard": "in"},
]


def get_desktop_display_name(slug: str) -> str:
    return SUPPORTED_DESKTOPS.get(slug, slug)

