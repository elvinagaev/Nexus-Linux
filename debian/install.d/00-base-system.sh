#!/bin/bash
# First-boot setup script for Nexus Linux
# Ensures essential system services are configured

set -e

echo "Configuring Nexus Linux system services..."

# Ensure locale is set
if ! locale | grep -q "LANG="; then
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
fi

# Update package lists
apt-get update -qq || true

# Install essential dependencies if missing
for pkg in python3-pyside6.qtcore python3-pyside6.qtgui python3-pyside6.qtwidgets ubuntu-drivers-common; do
    if ! dpkg -l | grep -q "^ii.*$pkg"; then
        apt-get install -y "$pkg" || true
    fi
done

echo "Nexus Linux system services configured."
