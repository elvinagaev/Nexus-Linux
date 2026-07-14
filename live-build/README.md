Nexus Linux — Live ISO build (live-build)
==========================================

This directory produces the *actual bootable live ISO* described in the
project spec: boot the disc, GNOME is already running, and Nexus Installer
launches itself automatically inside that live session.

This is a different layer from `nexus-installer/` (the Python/PySide6 wizard
application itself) and from the pre-existing Debian netinst/DVD skeleton at
the repository root (`dists/`, `pool/`, `install.amd/`, `isolinux/`, ...) —
that skeleton boots the classic `debian-installer` (text/GTK wizard, no
desktop). This folder builds a genuine *live* image using `live-build`,
which is the standard Debian tool for exactly this job.

Why a separate mechanism is needed
-----------------------------------
A live ISO needs:
1. A full GNOME session installed inside the live filesystem (squashfs).
2. Nexus Installer's source + its Python dependencies pre-installed there.
3. An autostart entry so the live GNOME session launches Nexus Installer by
   itself, the same way Ubuntu's live sessions show an "Install Ubuntu" icon
   or auto-launch Ubiquity.

None of that exists inside a netinst/DVD skeleton (no desktop is ever
booted), which is why the two must be built with different tooling.

Requirements
------------
`live-build` only runs on Linux (it uses `debootstrap`, chroots, and mount
namespaces) — **it cannot run on Windows**. You have two options:

1. Run it yourself on a real Debian/Ubuntu machine or VM:
   ```bash
   sudo apt-get install live-build
   sudo ./build.sh
   ```
2. Trigger the `Build Live ISO` GitHub Actions workflow
   (`.github/workflows/build-iso.yml`) from the Actions tab — it runs on a
   Linux runner and uploads the resulting `.iso` as a downloadable artifact.

What `build.sh` does
---------------------
1. Copies `shared/`, `nexus-installer/`, and `nexus-center/` into
   `config/includes.chroot/opt/nexus-linux/` so they end up inside the live
   filesystem.
2. Runs `lb clean` and `lb config` (see `auto/config`) targeting Debian
   trixie, matching the Debian codename already used by the netinst skeleton
   in this repository.
3. Runs `lb build`, which produces a hybrid ISO you can boot in a VM or
   write to a USB stick.

Package selection
------------------
`config/package-lists/nexus-desktop.list.chroot` installs `task-gnome-desktop`
+ `gdm3` + `python3-pyside6.qtcore/.qtgui/.qtwidgets` + `network-manager-gnome` + `sudo` +
`firmware-linux` + `locales`, so GNOME, networking, and Nexus Installer's
runtime dependency are all present in the live filesystem.

Automatic login
----------------
`config/includes.chroot/etc/gdm3/daemon.conf` enables GDM automatic login for
the `nexus` live user (the same username set via `username=nexus` in
`auto/config`'s `--bootappend-live`). Without this, the live session would
stop at a login screen the user has no password for -- automatic login is
what actually gets you from "boot the disc" to "GNOME desktop is already
there" without any extra steps.

Autostart mechanism
--------------------
`config/includes.chroot/etc/skel/.config/autostart/nexus-installer.desktop`
is copied into the live user's home directory at boot (via `/etc/skel`),
which is the same mechanism real distros use to auto-launch their installer
on first boot. A matching launcher icon is also placed on the live desktop
in case the user closes the auto-launched window and wants to reopen it.

Known simplifications (for a follow-up iteration)
--------------------------------------------------
- Nexus Installer currently runs directly from its Python source inside
  `/opt/nexus-linux` via a small wrapper script, rather than from a properly
  built `.deb` package. Packaging each Nexus app as its own `.deb` (with
  per-app `debian/` control files) is a natural next step once the apps are
  further along.
- The project spec says "Ubuntu LTS" as the base, but the netinst skeleton
  already in this repository is Debian 13 (trixie). This live-build config
  follows the Debian codename already present so the two ISO types stay
  consistent; switching the base to Ubuntu later mainly means pointing
  live-build at Ubuntu's archives and using Ubuntu package names
  (e.g. `ubuntu-gnome-desktop`) instead of `task-gnome-desktop`.
- I was not able to actually boot-test the resulting ISO myself (no Linux
  environment available here) — the configuration follows the standard,
  well-documented live-build layout, but you should boot it in a VM
  (e.g. QEMU/VirtualBox) before trusting it on real hardware.
