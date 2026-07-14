#!/usr/bin/env python3
"""
Quick validation script for Nexus Linux project
Checks all critical components
"""

import sys
from pathlib import Path

def check_project():
    root = Path(__file__).resolve().parent
    errors = []
    warnings = []
    
    # Check shared module
    shared = root / "shared" / "nexus_common"
    required_files = ["__init__.py", "base.py", "constants.py", "ui.py"]
    
    for file in required_files:
        if not (shared / file).exists():
            errors.append(f"Missing: shared/nexus_common/{file}")
    
    # Check all apps
    apps = [
        "nexus-center",
        "nexus-shell-manager", 
        "nexus-installer",
        "nexus-update",
        "nexus-driver",
        "nexus-store",
        "nexus-backup",
        "nexus-gaming",
        "nexus-settings",
    ]
    
    for app in apps:
        app_path = root / app
        
        if not app_path.exists():
            errors.append(f"Missing app: {app}")
            continue
            
        if not (app_path / "pyproject.toml").exists():
            errors.append(f"Missing: {app}/pyproject.toml")
        
        if not (app_path / "README.md").exists():
            errors.append(f"Missing: {app}/README.md")
        
        src_path = app_path / "src"
        if not src_path.exists():
            errors.append(f"Missing: {app}/src")
            continue
        
        package_name = app.replace("-", "_")
        package_path = src_path / package_name
        
        if not package_path.exists():
            errors.append(f"Missing: {app}/src/{package_name}")
        elif not (package_path / "__init__.py").exists():
            errors.append(f"Missing: {app}/src/{package_name}/__init__.py")
    
    # Check Debian packaging
    debian = root / "debian"
    debian_files = ["control", "rules", "changelog", "compat"]
    
    for file in debian_files:
        if not (debian / file).exists():
            errors.append(f"Missing: debian/{file}")
    
    # Check install.d scripts
    install_d = debian / "install.d"
    if not install_d.exists():
        errors.append("Missing: debian/install.d/")
    else:
        scripts = list(install_d.glob("*.sh"))
        if len(scripts) < 3:
            warnings.append(f"Expected 3 install.d scripts, found {len(scripts)}")
    
    # Check tests
    tests = root / "tests"
    test_files = ["test_nexus_common.py", "test_debian_packaging.py", "test_project_structure.py"]
    
    for file in test_files:
        if not (tests / file).exists():
            errors.append(f"Missing: tests/{file}")
    
    # Check documentation
    docs = ["README.md", "ARCHITECTURE.md", "DEVELOPMENT.md", ".gitignore"]
    
    for file in docs:
        if not (root / file).exists():
            errors.append(f"Missing: {file}")
    
    # Print results
    print("=" * 60)
    print("NEXUS LINUX PROJECT VALIDATION")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ No critical errors found!")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("\n" + "=" * 60)
    
    return len(errors) == 0

if __name__ == "__main__":
    success = check_project()
    sys.exit(0 if success else 1)
