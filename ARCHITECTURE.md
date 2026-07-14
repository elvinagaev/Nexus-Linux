# Nexus Linux - Architecture & Design

## Overview

Nexus Linux is a modular, Debian/Ubuntu-based operating system designed for flexibility, maintainability, and modern desktop experiences. Each component is independently developed, tested, and deployable, while sharing a common infrastructure layer.

## Core Principles

1. **Modularity**: Each application is independent and can be updated, replaced, or removed without breaking the system
2. **Debian Compatibility**: Built on Ubuntu/Debian package infrastructure (APT, DEB)
3. **Qt/PySide6**: Modern, consistent UI framework across all applications
4. **User-First**: Desktop selection at first boot, seamless switching between environments
5. **Gaming-Focused**: First-class support for Steam, Proton, Wine, Lutris
6. **Maintainability**: Clean architecture, comprehensive tests, automated CI/CD

## Architecture Layers

### 1. Shared Infrastructure (`shared/nexus_common/`)

**Responsibility**: Core abstractions, constants, and shared utilities

**Components**:
- `base.py`: Base classes (`NexusApplication`, `NexusApplicationInfo`)
- `constants.py`: System constants (desktop list, app registry)
- `__init__.py`: Public API exports

**Used by**: All application modules

### 2. Application Modules

Each module follows the pattern:
```
nexus-{name}/
├── README.md                 # Module documentation
├── pyproject.toml            # Python package metadata
├── src/nexus_{name}/
│   ├── __init__.py
│   ├── app.py               # Application factory
│   ├── main.py              # Entry point
│   └── ui/                  # UI components (if GUI)
├── tests/                   # Module tests
└── debian/                  # Debian packaging (optional)
```

#### Nexus Center
**Purpose**: Central system administration hub
**Category**: Settings/Administration
**Features**:
- System information display
- Desktop environment management
- Update and kernel selection
- Driver and firmware management
- Gaming configuration
- Backup and snapshot management

**Tech**: PySide6 (Qt6), tabbed interface

#### Nexus Shell Manager
**Purpose**: Desktop environment lifecycle management
**Category**: System
**Features**:
- Install desktop environments
- Remove desktop environments
- Switch active environment
- Configure display managers
- Manage Wayland/X11 sessions

**Tech**: Command-line backend, optional GUI frontend

#### Nexus Installer
**Purpose**: First-boot/installation experience
**Category**: System
**Features**:
- Graphical partitioning
- Desktop selection
- Profile selection (gaming, dev, office, minimal)
- Network configuration
- User setup

**Tech**: PySide6, system partitioning libraries

#### Nexus Update
**Purpose**: System and kernel update management
**Category**: System
**Features**:
- Update check and installation
- Kernel selection and management
- Rollback support
- Update history
- Automatic scheduling

**Tech**: APT backend, systemd integration

#### Nexus Driver
**Purpose**: Hardware driver and firmware management
**Category**: Hardware
**Features**:
- Automatic hardware detection
- NVIDIA/AMD/Intel driver installation
- Wi-Fi firmware
- Bluetooth firmware
- Device management

**Tech**: ubuntu-drivers-common, custom detection

#### Nexus Store
**Purpose**: Application marketplace and package discovery
**Category**: Software
**Features**:
- Application browsing
- Installation/removal UI
- Rating and reviews
- Dependency management
- Repositories configuration

**Tech**: APT backend, PySide6

#### Nexus Backup
**Purpose**: System snapshots and restore workflows
**Category**: System
**Features**:
- Create system snapshots
- Restore from snapshots
- Backup scheduling
- Storage management
- Rollback to previous states

**Tech**: BTRFS/LVM snapshots, systemd timers

#### Nexus Gaming
**Purpose**: Gaming configuration and compatibility
**Category**: Gaming
**Features**:
- Steam integration
- Proton/Wine configuration
- Lutris management
- MangoHud setup
- GameMode configuration
- GPU selection and monitoring
- Performance optimization

**Tech**: PySide6, Proton API, Steam

#### Nexus Settings
**Purpose**: System preference management and registry
**Category**: System
**Features**:
- Shared configuration storage
- Theme and appearance settings
- Keyboard/mouse configuration
- Sound settings
- Network preferences

**Tech**: GSettings/DConf backend

### 3. Debian Packaging Layer

**Location**: `debian/`

**Components**:
- `control`: Package metadata and dependencies
- `changelog`: Version history
- `rules`: Build automation (debhelper)
- `compat`: Debhelper compatibility level
- `install.d/`: First-boot setup scripts
  - `00-base-system.sh`: Base system initialization
  - `10-desktop-setup.sh`: Desktop environment selection
  - `20-gaming-setup.sh`: Gaming tools installation

**Build Process**:
```bash
dpkg-buildpackage -us -uc
```

## Data Flow

### First Boot
```
Boot → Nexus Installer runs
  ├─ User selects desktop environment
  ├─ Partitioning
  ├─ User account setup
  └─ System installed

Post-install → install.d scripts run
  ├─ Base system setup
  ├─ Desktop installation
  ├─ Gaming tools (if selected)
  └─ System ready

User login → Nexus Center available
```

### Desktop Switching
```
Nexus Center → Shell Manager UI
  ├─ User selects desktop
  ├─ Download/install packages
  ├─ Configure display manager
  └─ Restart session
```

### Updates
```
Nexus Update checks for updates
  ├─ Query APT repositories
  ├─ Create backup snapshot
  ├─ Install updates
  ├─ Kernel selection if needed
  └─ Reboot if required
```

## Technology Stack

- **Base OS**: Ubuntu/Debian LTS
- **Package Manager**: APT/DPKG
- **UI Framework**: Qt6 (PySide6)
- **Language**: Python 3.11+
- **CI/CD**: GitHub Actions
- **Testing**: pytest
- **Containerization**: Not used (runs bare metal)

## Testing Strategy

### Unit Tests
- Individual module functionality
- Constants and data structures
- Helper functions

### Integration Tests
- Module dependencies
- Shared library availability
- Project structure validation

### System Tests
- Debian package building
- First-boot script execution
- Desktop environment switching

## Future Roadmap

### Version 0.2
- Full Nexus Center UI
- Desktop switching functionality
- Update management backend

### Version 0.3
- ISO builder
- Installation media creation
- Automated testing in VM

### Version 1.0
- Full feature parity with major distros
- Official repositories
- Community support

### Beyond 1.0
- Custom Nexus Kernel
- Immutable filesystem edition
- Developer tools edition
- AI assistant integration
- Flatpak/AppImage support

