"""
Install orchestration engine for Nexus Installer.

Runs the installation as a sequence of steps (partitioning, base system,
desktop environment, profile packages, bootloader/EFI configuration,
finalizing) and reports progress so the UI can show exactly what is being
installed and how it is going. The "base system" step mounts the freshly
partitioned target disk and clones the running live filesystem onto it
(see `target_installer`), then account/desktop/profile/bootloader all run
for real inside a chroot of that target root, exactly like a normal
Ubiquity/Calamares-style "install from a live session" installer.

When not running on Linux (e.g. during development), destructive commands
are simulated instead of executed so the wizard can be exercised safely.
"""

import subprocess
import time
from dataclasses import dataclass, field

try:
    from PySide6.QtCore import QThread, Signal
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

    class QThread:  # type: ignore
        """Fallback used when PySide6 is unavailable; run() is called directly."""

        def start(self):
            self.run()

from . import disk_manager, efi_manager, locale_manager, account_manager, target_installer
from nexus_common.constants import DEFAULT_DESKTOP, DESKTOP_PACKAGES, INSTALL_PROFILES
from nexus_common.package_cache import default_dry_run
from .account_manager import AccountConfiguration


@dataclass
class InstallConfiguration:
    region: dict = field(default_factory=dict)
    desktop: str = "gnome"
    profile: str = "minimal"
    disk: str = ""
    partition_mode: str = "erase"
    account: AccountConfiguration = field(default_factory=AccountConfiguration)


INSTALL_STEPS = [
    ("partition", "Partitioning disk"),
    ("base_system", "Installing base system"),
    ("account", "Creating user account"),
    ("desktop", "Installing desktop environment"),
    ("profile", "Installing profile packages"),
    ("bootloader", "Configuring bootloader"),
    ("finalize", "Finalizing installation"),
]


class InstallEngine(QThread if PYSIDE6_AVAILABLE else object):
    if PYSIDE6_AVAILABLE:
        step_started = Signal(str, str)
        step_progress = Signal(int)
        step_completed = Signal(str)
        step_failed = Signal(str, str)
        log_message = Signal(str)
        finished_install = Signal()

    def __init__(self, config: InstallConfiguration):
        if PYSIDE6_AVAILABLE:
            super().__init__()
        self.config = config
        self._simulate = default_dry_run()

    def run(self):
        total = len(INSTALL_STEPS)
        for index, (step_id, label) in enumerate(INSTALL_STEPS, start=1):
            self._emit_started(step_id, label)
            try:
                self._run_step(step_id)
            except Exception as exc:  # noqa: BLE001 - surfaced to the UI, not swallowed silently
                self._emit_failed(step_id, str(exc))
                return
            self._emit_progress(int(index / total * 100))
            self._emit_completed(step_id)
        self._emit_finished()

    def _run_step(self, step_id: str):
        if step_id == "partition":
            plan = disk_manager.build_erase_plan(self.config.disk)
            commands = disk_manager.apply_partition_plan(plan, dry_run=self._simulate)
            self._run_commands(commands)

        elif step_id == "base_system":
            self._emit_log("Mounting target partitions...")
            self._execute(target_installer.mount_target_commands(self.config.disk))

            self._emit_log("Copying the live system onto the target disk (this can take a while)...")
            self._execute(target_installer.copy_system_commands())

            self._emit_log("Preparing chroot environment...")
            self._execute(target_installer.bind_mount_commands())
            if not self._simulate:
                target_installer.apply_resolv_conf()
            self._execute(["apt-get update"], chroot=True)

            region = self.config.region or {}
            if region:
                self._run_commands(locale_manager.apply_locale_commands(region))
                if not self._simulate:
                    locale_manager.apply_locale(region, target_installer.TARGET_ROOT)

        elif step_id == "account":
            self._emit_log(f"Creating user account: {self.config.account.username}")
            self._run_commands(account_manager.build_display_commands(self.config.account))
            if not self._simulate:
                account_manager.apply_account(self.config.account, target_root=target_installer.TARGET_ROOT)

        elif step_id == "desktop":
            self._emit_log(f"Selected desktop environment: {self.config.desktop}")
            self._run_commands(
                [
                    "mkdir -p /etc/nexus",
                    f"echo 'desktop={self.config.desktop}' > /etc/nexus/desktop-selection.conf",
                ]
            )
            if not self._simulate:
                target_installer.write_desktop_selection(self.config.desktop)
            if self.config.desktop != DEFAULT_DESKTOP:
                package = DESKTOP_PACKAGES.get(self.config.desktop)
                if package:
                    self._execute(
                        [
                            "apt-get install -y "
                            "-o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold "
                            f"{package}"
                        ],
                        chroot=True,
                    )

        elif step_id == "profile":
            profile = INSTALL_PROFILES.get(self.config.profile, {})
            packages = profile.get("packages", [])
            if packages:
                self._execute(
                    [
                        "apt-get install -y "
                        "-o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold "
                        + " ".join(packages)
                    ],
                    chroot=True,
                )
            else:
                self._emit_log("No additional packages required for this profile.")

        elif step_id == "bootloader":
            boot_mode = efi_manager.detect_boot_mode()
            self._emit_log(f"Detected boot mode: {boot_mode.upper()}")
            self._execute(efi_manager.bootloader_commands(boot_mode, self.config.disk), chroot=True)

        else:
            self._emit_log("Generating fstab and unmounting target filesystems...")
            if not self._simulate:
                target_installer.apply_fstab(self.config.disk)
            self._execute(target_installer.unmount_target_commands(self.config.disk), best_effort=True)

    def _run_commands(self, commands):
        """Log-only preview -- never executes anything (used for masked/display
        command lists such as account_manager.build_display_commands)."""
        for command in commands:
            self._emit_log(f"$ {command}")
            if self._simulate:
                time.sleep(0.2)

    def _execute(self, commands, chroot=False, best_effort=False):
        """Log and, when not simulating, actually run each command.

        Elevated via `pkexec` (the installer runs as the normal live-session
        user, not root); `chroot=True` runs each command inside the target
        root at target_installer.TARGET_ROOT. Every command here is a plain
        space-separated argument list (no embedded quotes/redirection), so
        splitting on whitespace is safe and no shell is ever invoked.
        """
        for command in commands:
            self._emit_log(f"$ {command}")
            if self._simulate:
                time.sleep(0.2)
                continue
            argv = ["pkexec"]
            if chroot:
                argv += ["chroot", target_installer.TARGET_ROOT]
            # DEBIAN_FRONTEND=noninteractive stops any apt/dpkg debconf
            # question (e.g. "select default display manager" when a second
            # desktop environment's package pulls in sddm/lightdm alongside
            # the already-configured gdm3, or a conffile prompt) from
            # blocking forever on a tty that does not exist here. Harmless
            # for non-apt commands, which simply ignore the variable.
            argv += ["env", "DEBIAN_FRONTEND=noninteractive"]
            argv += command.split()
            try:
                subprocess.run(argv, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                if best_effort:
                    self._emit_log(f"(non-fatal) '{command}' failed: {exc}")
                    continue
                raise

    def _emit_started(self, step_id, label):
        self._emit_log(f"--- {label} ---")
        if PYSIDE6_AVAILABLE:
            self.step_started.emit(step_id, label)

    def _emit_progress(self, percent):
        if PYSIDE6_AVAILABLE:
            self.step_progress.emit(percent)

    def _emit_completed(self, step_id):
        if PYSIDE6_AVAILABLE:
            self.step_completed.emit(step_id)

    def _emit_failed(self, step_id, message):
        self._emit_log(f"ERROR: {message}")
        if PYSIDE6_AVAILABLE:
            self.step_failed.emit(step_id, message)

    def _emit_log(self, message):
        print(message)
        if PYSIDE6_AVAILABLE:
            self.log_message.emit(message)

    def _emit_finished(self):
        self._emit_log("Installation complete.")
        if PYSIDE6_AVAILABLE:
            self.finished_install.emit()
