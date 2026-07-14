"""System preference management for Nexus Settings."""

import subprocess

from nexus_common.constants import REGIONS


def get_regions() -> list:
    return REGIONS


def apply_hostname_commands(hostname: str) -> list:
    return [f"hostnamectl set-hostname {hostname}"]


def apply_locale_commands(region: dict) -> list:
    return [
        f"locale-gen {region['locale']}",
        f"update-locale LANG={region['locale']}",
        f"localectl set-x11-keymap {region['keyboard']}",
    ]


def run_commands(commands: list, dry_run: bool) -> None:
    """Execute a list of shell commands, elevated via pkexec, unless dry_run."""
    if dry_run:
        return
    for command in commands:
        subprocess.run(["pkexec", "sh", "-c", command], check=True)
