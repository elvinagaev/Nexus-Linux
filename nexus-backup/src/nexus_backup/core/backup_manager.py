"""Snapshot creation and restore management for Nexus Backup."""

import subprocess
from dataclasses import dataclass
from datetime import datetime

SNAPSHOT_ROOT = "/.snapshots"


@dataclass
class Snapshot:
    id: str
    timestamp: str
    description: str


def create_snapshot_commands(snapshot_id: str) -> list:
    return [f"btrfs subvolume snapshot -r / {SNAPSHOT_ROOT}/{snapshot_id}"]


def restore_snapshot_commands(snapshot_id: str) -> list:
    return [f"btrfs subvolume set-default {SNAPSHOT_ROOT}/{snapshot_id}", "reboot"]


def delete_snapshot_commands(snapshot_id: str) -> list:
    return [f"btrfs subvolume delete {SNAPSHOT_ROOT}/{snapshot_id}"]


def run_commands(commands: list, dry_run: bool) -> None:
    """Execute a list of shell commands, elevated via pkexec, unless dry_run."""
    if dry_run:
        return
    for command in commands:
        subprocess.run(["pkexec", "sh", "-c", command], check=True)


def new_snapshot(description: str) -> Snapshot:
    now = datetime.now()
    return Snapshot(
        id=now.strftime("%Y%m%d-%H%M%S"),
        timestamp=now.strftime("%Y-%m-%d %H:%M"),
        description=description,
    )
