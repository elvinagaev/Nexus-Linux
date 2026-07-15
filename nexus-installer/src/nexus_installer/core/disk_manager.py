"""
Disk detection and partitioning logic for Nexus Installer.

On Linux this uses `lsblk` to discover real disks. On non-Linux development
machines it falls back to a small set of mock disks so the installer UI can
still be built and tested.
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class Partition:
    name: str
    size: str
    fstype: str | None
    mountpoint: str | None


@dataclass
class Disk:
    name: str
    size: str
    model: str
    partitions: list = field(default_factory=list)


def list_disks() -> list:
    """Detect available disks. Returns mock data on non-Linux systems."""
    if sys.platform != "linux":
        return _mock_disks()

    try:
        result = subprocess.run(
            ["lsblk", "-J", "-b", "-o", "NAME,SIZE,MODEL,TYPE,FSTYPE,MOUNTPOINT"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    disks = []
    for device in data.get("blockdevices", []):
        if device.get("type") != "disk":
            continue
        partitions = [
            Partition(
                name=child.get("name", ""),
                size=_format_size(child.get("size")),
                fstype=child.get("fstype"),
                mountpoint=child.get("mountpoint"),
            )
            for child in device.get("children", [])
        ]
        disks.append(
            Disk(
                name=device.get("name", ""),
                size=_format_size(device.get("size")),
                model=device.get("model") or "Unknown",
                partitions=partitions,
            )
        )
    return disks


def _format_size(size_bytes) -> str:
    if size_bytes is None:
        return "Unknown"
    try:
        size_bytes = float(size_bytes)
    except (TypeError, ValueError):
        return "Unknown"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def _mock_disks() -> list:
    """Development/demo data used when not running on Linux."""
    return [
        Disk(
            name="sda",
            size="512.0 GB",
            model="Nexus Virtual Disk",
            partitions=[
                Partition(name="sda1", size="512.0 MB", fstype="vfat", mountpoint=None),
                Partition(name="sda2", size="511.5 GB", fstype="ext4", mountpoint=None),
            ],
        ),
        Disk(
            name="nvme0n1",
            size="1.0 TB",
            model="Nexus NVMe SSD",
            partitions=[],
        ),
    ]


@dataclass
class PartitionPlan:
    disk: str
    mode: str  # "erase" or "manual"
    efi_size_mb: int = 512
    swap_size_mb: int = 2048


def build_erase_plan(disk: str, efi_size_mb: int = 512, swap_size_mb: int = 2048) -> PartitionPlan:
    return PartitionPlan(disk=disk, mode="erase", efi_size_mb=efi_size_mb, swap_size_mb=swap_size_mb)


def apply_partition_plan(plan: PartitionPlan, dry_run: bool = True) -> list:
    """
    Build the shell commands required to apply the partition plan.

    When `dry_run` is True (default), the commands are returned but not
    executed. This keeps the function safe to call for previews and tests.
    Only pass dry_run=False when running for real inside a target install
    environment (e.g. a chroot from a live session).
    """
    device = f"/dev/{plan.disk}"
    swap_end = plan.efi_size_mb + plan.swap_size_mb
    commands = [
        f"parted -s {device} mklabel gpt",
        f"parted -s {device} mkpart ESP fat32 1MiB {plan.efi_size_mb}MiB",
        f"parted -s {device} set 1 esp on",
        f"parted -s {device} mkpart primary linux-swap {plan.efi_size_mb}MiB {swap_end}MiB",
        f"parted -s {device} mkpart primary ext4 {swap_end}MiB 100%",
        f"mkfs.vfat -F32 {device}1",
        f"mkswap {device}2",
        f"mkfs.ext4 -F {device}3",
    ]

    if not dry_run:
        for command in commands:
            # Elevated via `pkexec` -- the installer runs as the normal
            # live-session user, not root (same convention as every other
            # Nexus app's real subprocess calls).
            subprocess.run(["pkexec", *command.split()], check=True)

    return commands
