"""
User account and hostname configuration for Nexus Installer.

Security notes:
- Passwords are validated for minimum strength but are only ever held in
  memory for the duration of the install.
- Passwords are never written to any log or displayed command list --
  `build_display_commands` always returns a masked placeholder instead.
- The real account creation uses argument lists and stdin piping (never a
  shell string built from user input), which avoids shell injection and
  keeps the password out of the process list / shell history.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_USERNAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
_HOSTNAME_PATTERN = re.compile(r"^[a-zA-Z0-9-]{1,63}$")


@dataclass
class AccountConfiguration:
    full_name: str = ""
    username: str = ""
    password: str = ""
    hostname: str = "nexus-linux"
    auto_login: bool = False


def validate_account(account: AccountConfiguration) -> tuple:
    """Validate account fields. Returns (is_valid, error_message)."""
    if not _USERNAME_PATTERN.match(account.username):
        return False, (
            "Username must start with a lowercase letter or underscore and contain "
            "only lowercase letters, numbers, hyphens, or underscores."
        )
    if len(account.password) < 8:
        return False, "Password must be at least 8 characters."
    if not account.hostname or not _HOSTNAME_PATTERN.match(account.hostname):
        return False, "Computer name may only contain letters, numbers, and hyphens."
    return True, ""


def build_display_commands(account: AccountConfiguration) -> list:
    """Commands for display/logging purposes only -- the password is always masked."""
    return [
        f'useradd -m -s /bin/bash -c "{account.full_name}" {account.username}',
        f"echo '{account.username}:********' | chpasswd",
        f"hostnamectl set-hostname {account.hostname}",
        f"usermod -aG sudo {account.username}",
    ]


def apply_account(account: AccountConfiguration) -> None:
    """
    Actually create the account on a real Linux target. Never invoked during
    simulation/dry-run. The password is piped via stdin to `chpasswd` instead
    of being embedded in a command line, so it never appears in `ps` output
    or shell history.
    """
    subprocess.run(
        ["useradd", "-m", "-s", "/bin/bash", "-c", account.full_name, account.username],
        check=True,
    )
    subprocess.run(
        ["chpasswd"],
        input=f"{account.username}:{account.password}\n",
        text=True,
        check=True,
    )
    subprocess.run(["hostnamectl", "set-hostname", account.hostname], check=True)
    subprocess.run(["usermod", "-aG", "sudo", account.username], check=True)

    # Nexus Installer already collected region/desktop/account details, so the
    # first login should go straight to the desktop instead of GNOME's own
    # first-run wizard asking the same questions again.
    home_config = Path(f"/home/{account.username}/.config")
    home_config.mkdir(parents=True, exist_ok=True)
    (home_config / "gnome-initial-setup-done").touch()
