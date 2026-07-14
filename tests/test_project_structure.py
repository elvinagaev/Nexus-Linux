from pathlib import Path


def test_all_app_modules_have_pyproject():
    """Ensure all application modules have pyproject.toml"""
    root = Path(__file__).resolve().parents[1]
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
        assert app_path.exists(), f"App directory {app} missing"
        assert (app_path / "pyproject.toml").exists(), f"Missing pyproject.toml in {app}"
        assert (app_path / "README.md").exists(), f"Missing README.md in {app}"


def test_all_app_modules_have_src_structure():
    """Ensure all application modules have proper src/ structure"""
    root = Path(__file__).resolve().parents[1]
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
        src_path = root / app / "src"
        assert src_path.exists(), f"Missing src/ in {app}"
        
        # Each src should have a package directory
        package_name = app.replace("-", "_")
        package_path = src_path / package_name
        assert package_path.exists(), f"Missing {package_name} package in {app}/src"
        assert (package_path / "__init__.py").exists(), f"Missing __init__.py in {package_name}"


def test_debian_structure_exists():
    """Ensure Debian packaging structure is in place"""
    root = Path(__file__).resolve().parents[1]
    debian_path = root / "debian"
    
    required_files = [
        "control",
        "changelog",
        "rules",
        "compat",
    ]
    
    for file in required_files:
        assert (debian_path / file).exists(), f"Missing debian/{file}"


def test_debian_install_scripts_exist():
    """Ensure first-boot install.d scripts exist"""
    root = Path(__file__).resolve().parents[1]
    install_d = root / "debian" / "install.d"
    
    assert install_d.exists(), "Missing debian/install.d/"
    
    # Should have at least base setup script
    scripts = list(install_d.glob("*.sh"))
    assert len(scripts) > 0, "No install.d scripts found"


def test_shared_module_structure():
    """Ensure shared module has all components"""
    root = Path(__file__).resolve().parents[1]
    shared = root / "shared" / "nexus_common"
    
    required_files = [
        "__init__.py",
        "base.py",
        "constants.py",
    ]
    
    for file in required_files:
        assert (shared / file).exists(), f"Missing {file} in shared/nexus_common"


def test_github_workflow_exists():
    """Ensure CI/CD workflow is configured"""
    root = Path(__file__).resolve().parents[1]
    workflow = root / ".github" / "workflows" / "ci.yml"
    
    assert workflow.exists(), "Missing .github/workflows/ci.yml"
