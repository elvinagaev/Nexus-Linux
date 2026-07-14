"""Catalog of drivers and firmware that Nexus Driver Manager can prefetch and install."""

from nexus_common.package_cache import CacheablePackage

DRIVER_CATALOG = [
    CacheablePackage(
        id="nvidia",
        name="NVIDIA Graphics Driver",
        packages=["nvidia-driver-550"],
        description="Proprietary NVIDIA driver with CUDA and Vulkan support.",
    ),
    CacheablePackage(
        id="amd",
        name="AMD Graphics Driver",
        packages=["mesa-vulkan-drivers", "firmware-amd-graphics"],
        description="Open-source AMD GPU stack (Mesa + firmware).",
    ),
    CacheablePackage(
        id="intel",
        name="Intel Graphics Driver",
        packages=["intel-media-va-driver-non-free"],
        description="Intel integrated graphics video acceleration.",
    ),
    CacheablePackage(
        id="wifi",
        name="Wi-Fi Firmware",
        packages=["linux-firmware"],
        description="Common Wi-Fi adapter firmware bundle.",
    ),
    CacheablePackage(
        id="bluetooth",
        name="Bluetooth Firmware",
        packages=["bluez", "bluez-firmware"],
        description="Bluetooth stack and firmware.",
    ),
]
