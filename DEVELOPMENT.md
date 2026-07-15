# Nexus Linux Development Guide

## Project Setup

### Prerequisites
- Python 3.11 or higher
- pip or pipenv
- Git
- Debian/Ubuntu build tools (for packaging)

### Initial Setup

```bash
git clone https://github.com/nexuslinux/nexus-linux.git
cd nexus-linux

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt
```

## Development Workflow

### Working on an Application Module

Each application has the structure:
```
nexus-{name}/
├── src/nexus_{name}/     # Source code
├── tests/                # Module tests
├── pyproject.toml        # Package configuration
└── README.md             # Module documentation
```

To develop a module:

1. **Install the shared library first** (every app depends on it):
   ```bash
   pip install -e ./shared
   ```

2. **Navigate to the module**:
   ```bash
   cd nexus-center
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

4. **Make changes** to files in `src/nexus_{name}/`

5. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Testing

Run all tests:
```bash
pytest tests/ -v
```

Run tests for a specific module:
```bash
pytest tests/test_nexus_common.py -v
```

Run with coverage:
```bash
pip install pytest-cov
pytest --cov=shared --cov=tests/ tests/
```

### Building Debian Package

```bash
# Install build dependencies
sudo apt-get install debhelper dh-python python3-setuptools

# Build package
dpkg-buildpackage -us -uc

# Or using legacy method
debian/rules build
debian/rules binary
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and small
- Write docstrings for public APIs

## Adding a New Feature

### Example: Adding a new tab to Nexus Center

1. **Create a new UI component** in `nexus-center/src/nexus_center/ui/`:
   ```python
   def create_my_feature_tab():
       """Create My Feature tab"""
       widget = QWidget()
       layout = QVBoxLayout()
       # ... build UI
       return widget
   ```

2. **Import and add to NexusCenterWindow**:
   ```python
   # In nexus-center/src/nexus_center/ui/main_window.py
   tabs.addTab(create_my_feature_tab(), "My Feature")
   ```

3. **Write tests**:
   ```python
   # In tests/ or nexus-center/tests/
   def test_my_feature_tab_creates():
       widget = create_my_feature_tab()
       assert widget is not None
   ```

4. **Update documentation**:
   - Update `ARCHITECTURE.md` if it's a major feature
   - Add comments to the code
   - Update `README.md` if needed

## Adding a New Module

1. **Create module directory**:
   ```bash
   mkdir nexus-{name}
   mkdir -p nexus-{name}/src/nexus_{name}
   mkdir nexus-{name}/tests
   ```

2. **Add pyproject.toml**:
   ```toml
   [project]
   name = "nexus-{name}"
   version = "0.1.0"
   description = "Brief description"
   requires-python = ">=3.11"
   ```

3. **Create package files**:
   ```bash
   touch nexus-{name}/src/nexus_{name}/__init__.py
   touch nexus-{name}/src/nexus_{name}/app.py
   touch nexus-{name}/src/nexus_{name}/main.py
   ```

4. **Add to APP_REGISTRY** in `shared/nexus_common/constants.py`

5. **Create tests** to validate the module structure

## Running Nexus Center

After setting up:

```bash
pip install -e ./shared -e ./nexus-center

# From anywhere, once installed:
nexus-center

# Or directly as a module:
python -m nexus_center.main
```

Note: Requires PySide6 to be installed:
```bash
pip install PySide6
```

## CI/CD Pipeline

GitHub Actions automatically:
1. Runs tests on push/pull request
2. Tests against Python 3.11 and 3.12
3. Runs linting checks
4. Validates Debian packaging

View workflow: `.github/workflows/ci.yml`

## Documentation

- **ARCHITECTURE.md**: High-level architecture and design
- **README.md**: Project overview and quick start
- **Module README.md files**: Individual module documentation
- **Docstrings**: In-code documentation

## Common Tasks

### Updating shared infrastructure
```bash
cd shared/nexus_common
# Make changes
# Run tests from root: pytest tests/test_nexus_common.py
```

### Adding a new desktop environment
1. Update `SUPPORTED_DESKTOPS` in `shared/nexus_common/constants.py`
2. Update tests if needed
3. Update documentation

### Debugging
```python
# Add to app.py or main.py:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- Keep UI responsive: use threading for long operations
- Cache configuration values
- Lazy-load heavy modules
- Monitor startup time

## Security Guidelines

- Don't hardcode credentials
- Use secure methods for privileged operations
- Validate user input
- Keep dependencies updated
- Avoid shell injection vulnerabilities

## Reporting Issues

- Use GitHub Issues
- Include Python version, OS, and steps to reproduce
- Attach relevant logs and error messages
- Try to isolate the issue to one component

## License

This project is licensed under the MIT License. See LICENSE file.
