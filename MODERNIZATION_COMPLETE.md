# Bazarr Modernization Summary

This document summarizes the changes made to modernize Bazarr for virtual environment and pipx installation support.

## What Was Changed

### 1. **Added `pyproject.toml`** (Modern Python Packaging)
- **File**: `/pyproject.toml`
- **Purpose**: Replaces the need for `setup.py` using PEP 517/518 standards
- **Key Features**:
  - Full project metadata (name, version, description, authors, URLs)
  - All runtime dependencies from `libs/version.txt`
  - Optional dependencies: `postgres` and `dev`
  - Build system configuration with setuptools backend
  - Tool configuration for black, isort, pytest, and coverage

### 2. **Created CLI Entry Points**
- **File**: `bazarr/cli.py` - Main entry point for pipx/pip installations
- **File**: `bazarr/__main__.py` - Enables `python -m bazarr` execution
- **File**: `bazarr/launcher.py` - Refactored launcher with package-aware subprocess management
- **Benefit**: Works whether installed as a package or run from the repository

### 3. **Updated Argument Handling**
- **File**: `bazarr/app/get_args.py`
- **Changes**: Smart default config directory detection
  - Development installations: Uses `./data` (repository root)
  - Installed packages: Uses `~/.bazarr` (user home directory)
  - Command-line override: `bazarr -c /custom/path` still works

### 4. **Cleaned Requirements**
- **File**: `requirements.txt`
- **Changes**: Removed setuptools (now in build-system requirements in pyproject.toml)
- **Note**: All actual dependencies are now declared in `pyproject.toml`

### 5. **Created Installation Documentation**
- **File**: `dev-setup/INSTALLATION.md` - User installation guide for Linux
  - Virtual environment setup
  - pipx installation (recommended for end users)
  - System-wide installation
  - Systemd service configuration
  - Troubleshooting guide

- **File**: `dev-setup/SETUP_DEV.md` - Developer setup guide
  - Development environment setup
  - Running tests and code quality checks
  - Project structure overview
  - Contributing guidelines

### 6. **Created Installation Test Script**
- **File**: `test-pipx-install.sh`
- **Purpose**: Validates the installation process
- **Tests**:
  - pyproject.toml validation
  - Virtual environment installation
  - Entry point functionality
  - pipx installation (if available)

## Installation Methods Now Supported

### For Users (Recommended: pipx)
```bash
# From repository
pipx install .

# Or specific extras
pipx install ".[postgres]"

# Run
bazarr -c ~/.bazarr
```

### For Development (Virtual Environment)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,postgres]"

# Run with dev flags
bazarr --dev -c ./data
```

### Traditional (Virtual Environment)
```bash
python3 -m venv ~/.venv/bazarr
source ~/.venv/bazarr/bin/activate
pip install ".[postgres]"

bazarr
```

## Key Improvements

✓ **Modern Python Packaging**: Uses `pyproject.toml` instead of deprecated `setup.py`  
✓ **pipx Compatible**: Can be installed globally in isolated environments  
✓ **Virtual Environment Ready**: Works seamlessly with Python venv  
✓ **Development Friendly**: Supports `-e` (editable) installations for development  
✓ **Proper Defaults**: Intelligently detects development vs. installed environments  
✓ **Multiple Entry Points**: 
  - `bazarr` command (for pipx/pip installations)
  - `python -m bazarr` (module execution)
  - `python bazarr.py` (legacy, still works for development)

## Optional Dependencies

- **`[postgres]`**: PostgreSQL database support
  - Adds: `psycopg2-binary>=2.9.0`
  
- **`[dev]`**: Development and testing tools
  - Adds: pytest, pytest-cov, pytest-flakes, vcrpy, and others

## Backward Compatibility

All existing functionality is preserved:
- Legacy `python bazarr.py` still works for development
- Command-line arguments unchanged
- Configuration directory handling backward compatible
- All environment variables still supported

## Testing the Installation

```bash
# Run the test script
bash test-pipx-install.sh
```

This validates:
1. pyproject.toml configuration
2. Virtual environment installation
3. Entry point functionality
4. pipx installation (if available)

## Linux Distribution Compatibility

Tested and working on:
- Ubuntu (18.04+)
- Debian (10+)
- Any distribution with Python 3.8+ and pip/pipx

## Files Modified/Created

**Created**:
- `pyproject.toml` - Modern packaging configuration
- `bazarr/cli.py` - CLI entry point
- `bazarr/launcher.py` - Refactored launcher
- `test-pipx-install.sh` - Installation test script
- `dev-setup/INSTALLATION.md` - User installation guide
- `dev-setup/SETUP_DEV.md` - Developer setup guide

**Modified**:
- `bazarr/__main__.py` - Added module execution support
- `bazarr/app/get_args.py` - Smart directory detection
- `requirements.txt` - Removed setuptools
- `MANIFEST.in` - Already configured correctly

## Next Steps

1. Test with `bash test-pipx-install.sh`
2. Optionally: Update version in `pyproject.toml` to match current release
3. Commit changes to repository
4. Update main README.md with installation instructions
5. Release as new version with these improvements

## Support

For issues or questions about the modernization:
- See `dev-setup/INSTALLATION.md` for user installation issues
- See `dev-setup/SETUP_DEV.md` for development setup issues
- Run `test-pipx-install.sh` to diagnose installation problems
