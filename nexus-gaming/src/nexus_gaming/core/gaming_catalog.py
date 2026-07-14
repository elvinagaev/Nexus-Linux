"""Catalog of gaming tools that Nexus Gaming can prefetch and install."""

from nexus_common.package_cache import CacheablePackage

GAMING_CATALOG = [
    CacheablePackage(
        id="steam",
        name="Steam",
        packages=["steam"],
        description="Game store and launcher, including the Proton compatibility layer.",
    ),
    CacheablePackage(
        id="proton",
        name="Proton",
        packages=[],
        description="Managed automatically by Steam Play; no separate package required.",
    ),
    CacheablePackage(
        id="wine",
        name="Wine",
        packages=["wine"],
        description="Run Windows applications and games natively.",
    ),
    CacheablePackage(
        id="lutris",
        name="Lutris",
        packages=["lutris"],
        description="Open gaming platform supporting multiple game stores.",
    ),
    CacheablePackage(
        id="mangohud",
        name="MangoHud",
        packages=["mangohud"],
        description="In-game performance overlay (FPS, temperatures, GPU/CPU usage).",
    ),
    CacheablePackage(
        id="gamemode",
        name="GameMode",
        packages=["gamemode"],
        description="Applies automatic performance optimizations while gaming.",
    ),
]
