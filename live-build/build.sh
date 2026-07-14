#!/bin/bash
# Build the Nexus Linux live ISO using live-build.
# Must run on a real Debian/Ubuntu machine (or CI) -- live-build does not run
# on Windows since it needs debootstrap, chroots, and mount namespaces.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

chmod +x auto/config auto/clean config/includes.chroot/usr/local/bin/nexus-installer

echo "Staging Nexus application source into the live filesystem..."
STAGE_DIR="config/includes.chroot/opt/nexus-linux"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
cp -r "$REPO_ROOT/shared" "$STAGE_DIR/shared"
cp -r "$REPO_ROOT/nexus-installer" "$STAGE_DIR/nexus-installer"
cp -r "$REPO_ROOT/nexus-center" "$STAGE_DIR/nexus-center"

echo "Cleaning any previous build..."
lb clean

echo "Configuring live-build..."
lb config

echo "Building the ISO (this takes a while)..."
lb build

echo "Done. Look for a .iso file in $SCRIPT_DIR."
