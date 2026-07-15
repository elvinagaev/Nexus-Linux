"""Tests for the Nexus Installer core logic (disk, EFI, region, engine)."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "shared"))
sys.path.insert(0, str(REPO_ROOT / "nexus-installer" / "src"))

from nexus_common.constants import (
    DEFAULT_DESKTOP, RECOMMENDED_DESKTOP, DESKTOP_PACKAGES, INSTALL_PROFILES, REGIONS,
    SUPPORTED_DESKTOPS,
)
from nexus_installer.core import disk_manager, efi_manager, locale_manager, account_manager, target_installer
from nexus_installer.core.install_engine import InstallConfiguration, INSTALL_STEPS
from nexus_installer.core.account_manager import AccountConfiguration, validate_account


def test_default_desktop_is_gnome():
    assert DEFAULT_DESKTOP == "gnome"
    assert DEFAULT_DESKTOP in SUPPORTED_DESKTOPS


def test_recommended_desktop_is_hyprland():
    assert RECOMMENDED_DESKTOP == "hyprland"
    assert RECOMMENDED_DESKTOP in SUPPORTED_DESKTOPS


def test_install_profiles_has_four_options():
    expected = {"gaming", "developer", "office", "minimal"}
    assert expected == set(INSTALL_PROFILES.keys())
    for profile in INSTALL_PROFILES.values():
        assert "name" in profile
        assert "description" in profile
        assert "packages" in profile


def test_regions_have_required_fields():
    assert len(REGIONS) > 0
    for region in REGIONS:
        assert "region" in region
        assert "locale" in region
        assert "timezone" in region
        assert "keyboard" in region


def test_list_disks_returns_data():
    disks = disk_manager.list_disks()
    assert isinstance(disks, list)
    assert len(disks) > 0
    for disk in disks:
        assert disk.name
        assert disk.size


def test_build_erase_plan_has_expected_defaults():
    plan = disk_manager.build_erase_plan("sda")
    assert plan.disk == "sda"
    assert plan.mode == "erase"
    assert plan.efi_size_mb == 512
    assert plan.swap_size_mb == 2048


def test_apply_partition_plan_dry_run_returns_commands_without_executing():
    plan = disk_manager.build_erase_plan("sda")
    commands = disk_manager.apply_partition_plan(plan, dry_run=True)
    assert len(commands) > 0
    assert any("mkfs.vfat" in cmd for cmd in commands)
    assert any("mkswap" in cmd for cmd in commands)
    assert any("mkfs.ext4" in cmd for cmd in commands)


def test_detect_boot_mode_returns_valid_value():
    mode = efi_manager.detect_boot_mode()
    assert mode in ("uefi", "bios")


def test_bootloader_commands_uefi():
    commands = efi_manager.bootloader_commands("uefi", "sda")
    assert any("grub-efi-amd64" in cmd for cmd in commands)
    assert any("grub-install" in cmd and "x86_64-efi" in cmd for cmd in commands)
    # The ESP is already mounted by target_installer during base_system, so
    # bootloader_commands must not try to mount it again.
    assert not any(cmd.startswith("mount ") for cmd in commands)


def test_bootloader_commands_bios():
    commands = efi_manager.bootloader_commands("bios", "sda")
    assert any("grub-pc" in cmd for cmd in commands)
    assert any(cmd == "grub-install /dev/sda" for cmd in commands)


def test_validate_esp_with_vfat_partition():
    disks = disk_manager.list_disks()
    disk_with_esp = next((d for d in disks if any(p.fstype == "vfat" for p in d.partitions)), None)
    if disk_with_esp is not None:
        is_valid, message = efi_manager.validate_esp(disk_with_esp.partitions)
        assert is_valid is True
        assert "EFI" in message


def test_get_regions_returns_list():
    regions = locale_manager.get_regions()
    assert regions == REGIONS


def test_find_region_by_name():
    region = locale_manager.find_region("Germany")
    assert region is not None
    assert region["locale"] == "de_DE.UTF-8"


def test_find_region_unknown_returns_none():
    assert locale_manager.find_region("Nowhere") is None


def test_apply_locale_commands_contains_expected_calls():
    region = {"region": "Test", "locale": "en_US.UTF-8", "timezone": "UTC", "keyboard": "us"}
    commands = locale_manager.apply_locale_commands(region)
    assert any("locale-gen" in cmd for cmd in commands)
    assert any("update-locale" in cmd for cmd in commands)
    assert any("localectl" in cmd for cmd in commands)


def test_install_configuration_defaults():
    config = InstallConfiguration()
    assert config.desktop == "gnome"
    assert config.profile == "minimal"
    assert config.disk == ""
    assert config.partition_mode == "erase"
    assert config.region == {}
    assert config.account.username == ""


def test_install_steps_cover_full_flow():
    step_ids = [step_id for step_id, _ in INSTALL_STEPS]
    assert step_ids == [
        "partition", "base_system", "account", "desktop", "profile", "bootloader", "finalize",
    ]


def test_validate_account_accepts_valid_input():
    account = AccountConfiguration(
        full_name="Jane Doe", username="jane", password="correct-horse", hostname="nexus-pc",
    )
    is_valid, message = validate_account(account)
    assert is_valid is True
    assert message == ""


def test_validate_account_rejects_short_password():
    account = AccountConfiguration(username="jane", password="short", hostname="nexus-pc")
    is_valid, message = validate_account(account)
    assert is_valid is False
    assert "Password" in message


def test_validate_account_rejects_invalid_username():
    account = AccountConfiguration(username="Jane Doe", password="correct-horse", hostname="nexus-pc")
    is_valid, message = validate_account(account)
    assert is_valid is False
    assert "Username" in message


def test_validate_account_rejects_invalid_hostname():
    account = AccountConfiguration(username="jane", password="correct-horse", hostname="bad host!")
    is_valid, message = validate_account(account)
    assert is_valid is False
    assert "Computer name" in message


def test_build_display_commands_never_exposes_password():
    account = AccountConfiguration(
        full_name="Jane Doe", username="jane", password="super-secret-value", hostname="nexus-pc",
    )
    commands = account_manager.build_display_commands(account)
    joined = "\n".join(commands)
    assert "super-secret-value" not in joined
    assert "********" in joined


def test_desktop_packages_cover_all_supported_desktops():
    assert set(DESKTOP_PACKAGES.keys()) == set(SUPPORTED_DESKTOPS.keys())


def test_mount_target_commands_mounts_root_esp_and_swap():
    commands = target_installer.mount_target_commands("sda")
    assert "mount /dev/sda3 /target" in commands
    assert "mount /dev/sda1 /target/boot/efi" in commands
    assert "swapon /dev/sda2" in commands


def test_copy_system_commands_excludes_pseudo_and_live_only_paths():
    commands = target_installer.copy_system_commands()
    assert len(commands) == 1
    command = commands[0]
    assert command.startswith("rsync")
    for excluded in ("/dev/*", "/proc/*", "/sys/*", "/run/*", "/home/*", "/target/*"):
        assert f"--exclude={excluded}" in command


def test_bind_mount_commands_covers_dev_proc_sys():
    commands = target_installer.bind_mount_commands()
    assert "mount --bind /dev /target/dev" in commands
    assert "mount --bind /proc /target/proc" in commands
    assert "mount --bind /sys /target/sys" in commands


def test_unmount_target_commands_reverses_mount_order():
    commands = target_installer.unmount_target_commands("sda")
    assert commands.index("umount /target/dev") < commands.index("umount /target")
    assert "swapoff /dev/sda2" in commands
    assert commands[-1] == "umount /target"


def test_build_fstab_contains_each_uuid_and_mountpoint():
    content = target_installer.build_fstab("root-uuid", "esp-uuid", "swap-uuid")
    assert "UUID=root-uuid" in content
    assert "UUID=esp-uuid" in content
    assert "UUID=swap-uuid" in content
    assert " / " in content
    assert "/boot/efi" in content
    assert "swap" in content
