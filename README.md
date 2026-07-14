# Nexus Linux

*A system you don't need to configure. Download and play.*

A modular Linux distribution scaffold based on Ubuntu/Debian LTS, featuring independent applications for system administration, desktop management, installation, updates, drivers, gaming, and backups.

## Philosophy

- **Ubuntu/Debian-based**: Compatible with Ubuntu LTS and Debian package ecosystem
- **Modular**: Each application is independently developed and deployable
- **Modern**: Qt6/PySide6 UI framework for consistent user experience
- **User-first**: Desktop selection on first boot, swappable environments, gaming-focused
- **Maintainable**: Clean architecture, automated testing, CI/CD automation

## Project structure

```
nexus-linux/
├── shared/              # Common infrastructure and utilities
│   └── nexus_common/    # Core modules, constants, base classes
├── nexus-center/        # Central settings hub
├── nexus-shell-manager/ # Desktop environment management
├── nexus-installer/     # Graphical installer
├── nexus-update/        # Update and kernel management
├── nexus-driver/        # Driver and firmware installation
├── nexus-store/         # Application marketplace
├── nexus-backup/        # Snapshots and restore
├── nexus-gaming/        # Gaming configuration
├── nexus-settings/      # System preferences
├── debian/              # Debian/Ubuntu packaging
├── install.d/           # First-boot installation scripts
├── tests/               # Test suite
└── .github/             # GitHub Actions CI/CD
```

## Supported Desktop Environments

- Hyprland (recommended)
- KDE Plasma
- XFCE
- Cinnamon
- GNOME
- COSMIC
- MATE
- LXQt
- Sway
- i3

## Development

Install test dependencies:
```bash
pip install pytest
```

Run tests:
```bash
pytest -v
```

Build Debian package:
```bash
dpkg-buildpackage -us -uc
```

## Future plans

- Custom Nexus Kernel
- Own package repository
- ISO builder
- Immutable edition
- Developer edition
- Gaming edition
- AI assistant integration
