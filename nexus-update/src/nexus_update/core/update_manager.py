"""Update, kernel, and rollback management for Nexus Update."""

import subprocess
from dataclasses import dataclass
from datetime import datetime

AVAILABLE_KERNELS = [
    "6.8.0-linux (current)",
    "6.7.0-linux",
    "6.6.0-linux",
]


@dataclass
class UpdateHistoryEntry:
    timestamp: str
    description: str


def check_updates_commands() -> list:
    return ["apt-get update", "apt list --upgradable"]


def install_updates_commands() -> list:
    return ["apt-get upgrade -y"]


def cleanup_commands() -> list:
    return ["apt-get autoremove -y", "apt-get autoclean"]


def rollback_commands(snapshot_label: str) -> list:
    return [f"nexus-backup restore '{snapshot_label}'"]


def set_kernel_commands(kernel: str) -> list:
    version = kernel.split(" ")[0]
    return [f"grub-reboot 'Advanced options>Linux {version}'", "update-grub"]


def run_commands(commands: list, dry_run: bool) -> None:
    """Execute a list of shell commands, elevated via pkexec, unless dry_run."""
    if dry_run:
        return
    for command in commands:
        subprocess.run(["pkexec", "sh", "-c", command], check=True)


def new_history_entry(description: str) -> UpdateHistoryEntry:
    return UpdateHistoryEntry(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), description=description)
