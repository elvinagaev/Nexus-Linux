#!/bin/bash
# Desktop environment installation script
# Installs the desktop environment selected during installation.
# GNOME is installed automatically by default when no selection is present,
# ensuring maximum compatibility on first boot.

set -e
# Never let apt/dpkg block on an interactive debconf question (e.g. picking
# a default display manager when a second desktop's package pulls in
# sddm/lightdm alongside gdm3) -- no tty is attached here.
export DEBIAN_FRONTEND=noninteractive

CONFIG_FILE="/etc/nexus/desktop-selection.conf"
DEFAULT_DESKTOP="gnome"

SELECTED_DESKTOP="$DEFAULT_DESKTOP"
if [ -f "$CONFIG_FILE" ]; then
    SELECTED_DESKTOP=$(grep -m1 '^desktop=' "$CONFIG_FILE" | cut -d'=' -f2)
    SELECTED_DESKTOP=${SELECTED_DESKTOP:-$DEFAULT_DESKTOP}
fi

echo "Installing selected desktop environment: $SELECTED_DESKTOP"

install_desktop() {
    local package=$1
    echo "Installing $package..."
    apt-get install -y "$package" || echo "Failed to install $package"
}

case "$SELECTED_DESKTOP" in
    gnome)    install_desktop ubuntu-gnome-desktop ;;
    hyprland) install_desktop hyprland ;;
    kde)      install_desktop kde-standard ;;
    xfce)     install_desktop xfce4 ;;
    cinnamon) install_desktop cinnamon-desktop-environment ;;
    cosmic)   install_desktop cosmic-desktop ;;
    mate)     install_desktop mate-desktop-environment ;;
    lxqt)     install_desktop lxqt ;;
    sway)     install_desktop sway ;;
    i3)       install_desktop i3 ;;
    *)
        echo "Unknown desktop '$SELECTED_DESKTOP', defaulting to GNOME"
        install_desktop ubuntu-gnome-desktop
        ;;
esac

echo "Desktop environment configuration complete."

