#!/bin/bash
# Disable GNOME's own first-run wizard.
#
# Nexus Installer already collects the user's region, account, and desktop
# choice during installation, so gnome-initial-setup must not run again and
# ask the same questions a second time. Nexus's own setup takes priority.

set -e

echo "Disabling GNOME's default initial setup wizard..."

mkdir -p /etc/skel/.config
touch /etc/skel/.config/gnome-initial-setup-done

if [ -d /home ]; then
    for userhome in /home/*; do
        if [ -d "$userhome" ]; then
            mkdir -p "$userhome/.config"
            touch "$userhome/.config/gnome-initial-setup-done"
        fi
    done
fi

# Belt-and-suspenders: mask the systemd units too, in case the marker file
# approach ever changes between GNOME versions.
systemctl --global mask gnome-initial-setup-first-login.service 2>/dev/null || true
systemctl --global mask gnome-initial-setup-copy-worker.service 2>/dev/null || true

echo "GNOME initial setup disabled; the Nexus first-boot experience takes priority."
