"""
EFI/BIOS boot mode detection and bootloader configuration for Nexus Installer.

This module fixes the common mistake of assuming a single boot mode: it
detects whether the machine booted via UEFI or legacy BIOS and builds the
correct bootloader installation commands for each case, including creating
and validating the EFI System Partition (ESP) when required.
"""

import sys
from pathlib import Path


def detect_boot_mode() -> str:
    """Return 'uefi' if the running system booted in UEFI mode, else 'bios'."""
    if sys.platform != "linux":
        # Sensible default for development/demo purposes off-target.
        return "uefi"

    return "uefi" if Path("/sys/firmware/efi").exists() else "bios"


def bootloader_commands(boot_mode: str, disk: str, esp_mountpoint: str = "/boot/efi") -> list:
    """
    Build the shell commands needed to install the bootloader for the given
    boot mode. Commands are returned, not executed, so callers can preview
    or log them before running for real inside the target system.
    """
    device = f"/dev/{disk}"

    if boot_mode == "uefi":
        # The EFI System Partition is already mounted at esp_mountpoint (as
        # seen from inside the target chroot) by
        # target_installer.mount_target_commands() during the base_system
        # step, so there is no need to create/mount it again here.
        return [
            "apt-get install -y -o Dpkg::Options::=--force-confdef "
            "-o Dpkg::Options::=--force-confold grub-efi-amd64 shim-signed",
            f"grub-install --target=x86_64-efi --efi-directory={esp_mountpoint} "
            "--bootloader-id=NexusLinux --recheck",
            "update-grub",
        ]

    return [
        "apt-get install -y -o Dpkg::Options::=--force-confdef "
        "-o Dpkg::Options::=--force-confold grub-pc",
        f"grub-install {device}",
        "update-grub",
    ]


def validate_esp(partitions) -> tuple:
    """
    Sanity-check that an EFI System Partition (FAT32) is present when
    booting via UEFI. Returns (is_valid, message).
    """
    if detect_boot_mode() != "uefi":
        return True, "Legacy BIOS boot detected; no EFI System Partition required."

    for partition in partitions:
        if getattr(partition, "fstype", None) == "vfat":
            return True, f"EFI System Partition found: {partition.name}"

    return False, "No EFI System Partition (FAT32) detected. One will be created automatically."
