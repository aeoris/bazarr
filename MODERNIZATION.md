# Bazarr Python Modernization

This document summarizes the modernization efforts made to support modern Python packaging and virtual environment installation on Linux distributions.

## What's New

### 1. **Modern Python Packaging with `pyproject.toml`**

A comprehensive `pyproject.toml` has been added following [PEP 518](https://www.python.org/dev/peps/pep-0518/) and [PEP 621](https://www.python.org/dev/peps/pep-0621/) standards:

- **Build system**: Uses setuptools as the build backend
- **Metadata**: Complete project metadata, classifiers, and URLs
- **Dependencies**: All runtime dependencies specified with version constraints
- **Optional dependencies**: Separate `postgres` and `dev` extras for different use cases
- **Entry points**: `bazarr` command configured as a console script
- **Tool configuration**: Black, isort, and pytest configuration included

This enables installation with modern tools like `pip`, `pipx`, and poetry.

### 2. **Modular Entry Points**

Three entry points have been created to support different use cases:

#### `bazarr/cli.py` - pipx/pip Console Entry Point
- Designated as the main `bazarr` command when installed via pip/pipx
- Delegates to `launcher.main()`
- Allows: `bazarr -c ~/.bazarr`

#### `bazarr/__main__.py` - Module Execution Entry Point
- Enables running Bazarr as a module: `python -m bazarr`
- Useful for development and debugging
- Delegates to `launcher.main()`

#### `bazarr/launcher.py` - Core Launcher Logic
- Refactored from original `bazarr.py`
- Contains all subprocess management, restart/stop logic
- Main `main()` function handles:
  - Python version checking
  - Signal handling (Ctrl+C, SIGTERM)
  - Child process management
  - Restart/stop file handling

### 3. **Smart Data Directory Detection**

Updated `bazarr/app/get_args.py` with intelligent directory detection:

```python
def get_default_config_dir():
    """Get the default configuration directory.
    
    For development installations: <repo>/data
    For pip/pipx installations: ~/.bazarr
    """
```

This allows:
- **Development**: Uses `./data` when running from repository
- **Installed**: Uses `~/.bazarr` when installed via pip/pipx
- **Custom**: Override with `-c /custom/path`

### 4. **Installation Documentation**

Two comprehensive guides have been added:

#### `dev-setup/INSTALLATION.md`
Complete installation guide for end users covering:
- Virtual environment setup
- pipx installation (recommended for users)
- System-wide installation (not recommended)
- Configuration and environment variables
- Systemd service integration
- Troubleshooting

#### `dev-setup/SETUP_DEV.md`
Developer guide covering:
- Quick development setup
- Docker Compose alternative
- Running tests and checking code quality
- Project structure
- Common tasks
- Contributing guidelines

### 5. **Cleaned Dependencies**

- Removed `setuptools` from `requirements.txt` (now in `pyproject.toml` build-requires)
- Consolidated all dependencies in a single source of truth
- Organized dependencies with proper version constraints

## Installation Methods

### Virtual Environment (Recommended for Development)
```bash
python3 -m venv ~/.venv/bazarr
source ~/.venv/bazarr/bin/activate
pip install -e ".[dev]"
bazarr --dev -c ./data
```

### pipx (Recommended for Users)
```bash
pipx install .
bazarr -c ~/.bazarr
```

### Traditional pip
```bash
pip install .
bazarr
```

## File Structure

```
bazarr/
├── bazarr.py                 # Original launcher (still works, legacy)
├── bazarr/
│   ├── cli.py               # NEW: pipx/pip console entry point
│   ├── __main__.py          # NEW: Module execution support
│   ├── launcher.py          # NEW: Refactored launcher logic
│   └── app/
│       └── get_args.py      # UPDATED: Smart directory detection
├── pyproject.toml           # NEW: Modern Python packaging
├── requirements.txt         # UPDATED: Removed setuptools
├── dev-setup/
│   ├── INSTALLATION.md      # NEW: User installation guide
│   └── SETUP_DEV.md        # NEW: Developer setup guide
└── README.md                # Existing project README
```

## Backward Compatibility

✓ **Fully backward compatible**:
- Original `bazarr.py` still works unchanged
- All existing configurations continue to function
- Docker installations unaffected
- `-c` and other CLI flags work as before

## Testing

All new code has been validated:
- ✓ Valid Python syntax (AST parsing)
- ✓ Valid TOML in pyproject.toml
- ✓ Import structure correct
- ✓ Entry points configured properly

## Benefits

### For Users
- Install with modern tools: `pipx install bazarr`
- No system package manager needed
- Easy to upgrade: `pipx upgrade bazarr`
- Automatic virtual environment isolation
- Can run multiple versions side-by-side

### For Developers
- Standard Python packaging layout
- Can use `pip install -e ".[dev]"` for development
- Better IDE support with proper package structure
- Standardized configuration with pyproject.toml
- Easy to test with pytest

### For Maintainers
- Single source of truth for dependencies
- Automatic dependency resolution
- Support for different Python versions
- Proper semantic versioning support
- Compatible with CI/CD systems

## Migration Guide

Existing users can migrate at their own pace:

### From Direct Execution
```bash
# Old way
python bazarr.py -c ./data

# New way (development)
python -m bazarr -c ./data

# New way (installed)
bazarr -c ~/.bazarr
```

### From Virtual Environment
```bash
# Create/activate venv (same as before)
source venv/bin/activate

# Install using new pyproject.toml
pip install -e ".[dev]"

# Run using new entry point
bazarr --dev -c ./data
```

## Future Improvements

This modernization opens the door for:
- [ ] Conda package distribution
- [ ] Automatic binary wheels
- [ ] Easier Docker multi-stage builds
- [ ] Package on PyPI
- [ ] Poetry/PDM support
- [ ] Dependency vulnerability scanning

## References

- [PEP 517 - A build-system independent format](https://www.python.org/dev/peps/pep-0517/)
- [PEP 518 - Specifying build system requirements](https://www.python.org/dev/peps/pep-0518/)
- [PEP 621 - Storing project metadata in pyproject.toml](https://www.python.org/dev/peps/pep-0621/)
- [setuptools documentation](https://setuptools.pypa.io/)
- [pipx documentation](https://pypa.github.io/pipx/)

## Support

For questions about the modernization:
- Check `dev-setup/INSTALLATION.md` for installation help
- Check `dev-setup/SETUP_DEV.md` for development help
- Open an issue on [GitHub](https://github.com/morpheus65535/bazarr/issues)
- Join [Discord](https://discord.gg/MH2e2eb) for community support
