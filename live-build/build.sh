#!/bin/bash
# Build the Nexus Linux live ISO using live-build.
# Must run on a real Debian/Ubuntu machine (or CI) -- live-build does not run
# on Windows since it needs debootstrap, chroots, and mount namespaces.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

chmod +x auto/config auto/clean config/hooks/live/*.hook.chroot config/includes.chroot/usr/local/bin/*

echo "Staging Nexus application source into the live filesystem..."
STAGE_DIR="config/includes.chroot/opt/nexus-linux"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
# Every Nexus app lives here so its /usr/local/bin/nexus-* wrapper script and
# /usr/share/applications/*.desktop entry (both under config/includes.chroot)
# can actually launch it. Keep this list in sync with STAGED_APPS in
# nexus-update/src/nexus_update/core/github_update_manager.py.
for app in shared nexus-installer nexus-center nexus-gaming nexus-driver nexus-update \
           nexus-shell-manager nexus-store nexus-backup nexus-settings; do
    cp -r "$REPO_ROOT/$app" "$STAGE_DIR/$app"
done

echo "Cleaning any previous build..."
lb clean

echo "Configuring live-build..."
lb config

echo "Building the ISO (this takes a while)..."
lb build

echo "Done. Look for a .iso file in $SCRIPT_DIR."
