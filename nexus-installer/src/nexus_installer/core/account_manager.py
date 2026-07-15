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
- Nexus Installer runs as the normal live-session user (not root), so every
  real subprocess call is elevated via `pkexec` -- the same convention used
  by every other Nexus app (nexus-backup, nexus-settings, nexus-driver...).
"""

import re
import subprocess
from dataclasses import dataclass

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


def apply_account(account: AccountConfiguration, target_root: str | None = None) -> None:
    """
    Actually create the account. Never invoked during simulation/dry-run.
    When `target_root` is given (the normal case during a real install),
    the account is created inside that target root via `chroot` instead of
    on whichever system this process happens to be running on. The
    password is still piped via stdin to `chpasswd` instead of being
    embedded in a command line, so it never appears in `ps` output or shell
    history, and every subprocess call uses an explicit argument list
    (never a shell string built from user input) so full_name/username/
    hostname can never be interpreted as shell syntax.
    """
    prefix = ["pkexec"]
    if target_root:
        prefix = prefix + ["chroot", target_root]

    subprocess.run(
        [*prefix, "useradd", "-m", "-s", "/bin/bash", "-c", account.full_name, account.username],
        check=True,
    )
    subprocess.run(
        [*prefix, "chpasswd"],
        input=f"{account.username}:{account.password}\n",
        text=True,
        check=True,
    )
    subprocess.run([*prefix, "usermod", "-aG", "sudo", account.username], check=True)

    if target_root:
        _write_hostname_files(prefix, account.hostname)
    else:
        subprocess.run([*prefix, "hostnamectl", "set-hostname", account.hostname], check=True)

    # Nexus Installer already collected region/desktop/account details, so the
    # first login should go straight to the desktop instead of GNOME's own
    # first-run wizard asking the same questions again.
    config_dir = f"/home/{account.username}/.config"
    subprocess.run([*prefix, "mkdir", "-p", config_dir], check=True)
    subprocess.run([*prefix, "touch", f"{config_dir}/gnome-initial-setup-done"], check=True)
    subprocess.run(
        [*prefix, "chown", "-R", f"{account.username}:{account.username}", config_dir],
        check=True,
    )


def _write_hostname_files(prefix: list, hostname: str) -> None:
    """
    Write /etc/hostname + /etc/hosts directly rather than via `hostnamectl`,
    which talks to systemd-hostnamed over D-Bus and doesn't reliably work
    inside a chroot with no running systemd/D-Bus session.
    """
    subprocess.run(
        [*prefix, "tee", "/etc/hostname"],
        input=f"{hostname}\n", text=True, check=True, stdout=subprocess.DEVNULL,
    )
    existing = subprocess.run(
        [*prefix, "cat", "/etc/hosts"], capture_output=True, text=True, check=False,
    )
    hosts_content = existing.stdout if existing.returncode == 0 and existing.stdout else "127.0.0.1\tlocalhost\n"
    if hostname not in hosts_content:
        hosts_content += f"127.0.1.1\t{hostname}\n"
    subprocess.run(
        [*prefix, "tee", "/etc/hosts"],
        input=hosts_content, text=True, check=True, stdout=subprocess.DEVNULL,
    )
