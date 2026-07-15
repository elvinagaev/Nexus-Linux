#!/bin/bash
# Gaming configuration and driver setup

set -e
# Never let apt/dpkg block on an interactive debconf question (no tty is
# attached when this script runs from a first-boot service).
export DEBIAN_FRONTEND=noninteractive

echo "Setting up gaming environment..."

# Install Steam if available
if apt-cache search "^steam\$" 2>/dev/null | grep -q .; then
    echo "Installing Steam..."
    apt-get install -y steam || echo "Steam installation skipped or failed"
fi

# Install Proton and Wine if available
for pkg in wine proton-tools; do
    if apt-cache search "^${pkg}\$" 2>/dev/null | grep -q .; then
        apt-get install -y "$pkg" || echo "Failed to install $pkg"
    fi
done

# Install MangoHud and GameMode if available
for pkg in mangohud gamemode; do
    if apt-cache search "^${pkg}\$" 2>/dev/null | grep -q .; then
        apt-get install -y "$pkg" || echo "Failed to install $pkg"
    fi
done

echo "Gaming environment setup complete."
