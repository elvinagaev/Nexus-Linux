"""
Target-root installation helpers for Nexus Installer.

`disk_manager.apply_partition_plan()` partitions and formats the target
disk; the functions here take it from there: mount the new partitions
under `TARGET_ROOT`, copy the running live system onto them (the live
squashfs already has GNOME and every Nexus app baked in, so this is a
straightforward "clone the live filesystem" install rather than a
from-scratch debootstrap -- the same approach classic live-installers such
as Ubiquity/Calamares use for a "copy this live session" install path),
prepare a chroot (bind-mounting /dev, /proc, /sys, and fixing up DNS), and
finally generate a real /etc/fstab (using each partition's UUID from
`blkid`) before everything is unmounted again.

Like `disk_manager`/`efi_manager`/`locale_manager`, the `*_commands()`
helpers below only ever BUILD and return a list of shell command strings --
they never execute anything themselves, so they stay safe to call for
previews, logging, and tests. `InstallEngine` is responsible for actually
running them (see `_execute()`), elevating via `pkexec` exactly like every
other Nexus app in this repo does (the installer runs as the normal
"nexus" live-session user, not root).

The functions that need to write files as root (`write_desktop_selection`,
`apply_resolv_conf`, `apply_fstab`) are real "apply" functions, not pure
command builders -- they still only ever touch the filesystem via
`pkexec ... | tee ...`-style argument lists (never a shell string built
from interpolated values), and are only ever invoked when the caller has
already confirmed this is a real (non-simulated) install.
"""

import subprocess

TARGET_ROOT = "/target"

# Paths that must never be copied when cloning the running live filesystem
# onto the target disk: pseudo-filesystems, live-only runtime state, the
# live session's own user data (the installer creates a fresh account for
# the target system separately), and the target mountpoint itself.
RSYNC_EXCLUDES = [
    "/dev/*",
    "/proc/*",
    "/sys/*",
    "/tmp/*",
    "/run/*",
    "/mnt/*",
    "/media/*",
    "/lost+found",
    "/swapfile",
    "/home/*",
    "/root/*",
    f"{TARGET_ROOT}/*",
]


def mount_target_commands(disk: str) -> list:
    """Mount the freshly-formatted target partitions under TARGET_ROOT."""
    device = f"/dev/{disk}"
    return [
        f"mkdir -p {TARGET_ROOT}",
        f"mount {device}3 {TARGET_ROOT}",
        f"mkdir -p {TARGET_ROOT}/boot/efi",
        f"mount {device}1 {TARGET_ROOT}/boot/efi",
        f"swapon {device}2",
    ]


def copy_system_commands() -> list:
    """Clone the running live filesystem onto the mounted target root."""
    excludes = " ".join(f"--exclude={path}" for path in RSYNC_EXCLUDES)
    return [f"rsync -aAXH {excludes} / {TARGET_ROOT}/"]


def bind_mount_commands() -> list:
    """Bind-mount pseudo-filesystems so the target root can be chrooted into."""
    return [
        f"mount --bind /dev {TARGET_ROOT}/dev",
        f"mount --bind /dev/pts {TARGET_ROOT}/dev/pts",
        f"mount --bind /proc {TARGET_ROOT}/proc",
        f"mount --bind /sys {TARGET_ROOT}/sys",
    ]


def unmount_target_commands(disk: str) -> list:
    """Reverse of bind_mount_commands + mount_target_commands, deepest path first."""
    device = f"/dev/{disk}"
    return [
        f"umount {TARGET_ROOT}/dev/pts",
        f"umount {TARGET_ROOT}/dev",
        f"umount {TARGET_ROOT}/proc",
        f"umount {TARGET_ROOT}/sys",
        f"umount {TARGET_ROOT}/boot/efi",
        f"swapoff {device}2",
        f"umount {TARGET_ROOT}",
    ]


def apply_resolv_conf() -> None:
    """
    Ensure the target chroot can resolve DNS names (needed by every
    `apt-get` call in the desktop/profile/bootloader steps). On the live
    system /etc/resolv.conf is often a symlink into /run (e.g.
    systemd-resolved's stub file), and /run is deliberately excluded from
    copy_system_commands(), so the copied symlink would otherwise dangle
    inside the chroot. Reads the live session's own resolved nameserver
    config and writes it as a real file instead of a symlink.
    Never invoked during simulation/dry-run.
    """
    live = subprocess.run(
        ["pkexec", "cat", "/etc/resolv.conf"], capture_output=True, text=True, check=False,
    )
    content = live.stdout if live.returncode == 0 and live.stdout.strip() else "nameserver 8.8.8.8\n"
    subprocess.run(["pkexec", "rm", "-f", f"{TARGET_ROOT}/etc/resolv.conf"], check=True)
    subprocess.run(
        ["pkexec", "tee", f"{TARGET_ROOT}/etc/resolv.conf"],
        input=content,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def write_desktop_selection(desktop: str) -> None:
    """
    Record the chosen desktop environment in the target root so it is
    known after the first boot. Never invoked during simulation/dry-run.
    """
    subprocess.run(["pkexec", "mkdir", "-p", f"{TARGET_ROOT}/etc/nexus"], check=True)
    subprocess.run(
        ["pkexec", "tee", f"{TARGET_ROOT}/etc/nexus/desktop-selection.conf"],
        input=f"desktop={desktop}\n",
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def build_fstab(root_uuid: str, esp_uuid: str, swap_uuid: str) -> str:
    """Pure fstab-content builder, kept separate from I/O so it's unit-testable."""
    return (
        "# /etc/fstab: generated by Nexus Installer\n"
        f"UUID={root_uuid}  /          ext4  defaults    0 1\n"
        f"UUID={esp_uuid}  /boot/efi  vfat  umask=0077  0 2\n"
        f"UUID={swap_uuid}  none       swap  sw          0 0\n"
    )


def _read_uuid(device: str) -> str:
    result = subprocess.run(
        ["pkexec", "blkid", "-s", "UUID", "-o", "value", device],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def apply_fstab(disk: str) -> None:
    """
    Write a real /etc/fstab into the target root using each partition's
    filesystem UUID. Never invoked during simulation/dry-run.
    """
    device = f"/dev/{disk}"
    content = build_fstab(
        root_uuid=_read_uuid(f"{device}3"),
        esp_uuid=_read_uuid(f"{device}1"),
        swap_uuid=_read_uuid(f"{device}2"),
    )
    subprocess.run(
        ["pkexec", "tee", f"{TARGET_ROOT}/etc/fstab"],
        input=content,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )
