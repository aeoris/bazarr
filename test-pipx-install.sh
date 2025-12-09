#!/bin/bash
# Test script to validate Bazarr pipx installation
# Usage: bash test-pipx-install.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/tmp/bazarr-test-venv"
PIPX_HOME="/tmp/bazarr-test-pipx"

echo "============================================================"
echo "Bazarr pipx Installation Test"
echo "============================================================"
echo

# Cleanup function
cleanup() {
    echo
    echo "Cleaning up test environments..."
    rm -rf "$VENV_DIR" "$PIPX_HOME"
    echo "Done."
}

trap cleanup EXIT

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check for pipx or install it
if ! command -v pipx &> /dev/null; then
    echo "✗ pipx not found. Install with: sudo apt-get install pipx"
    echo "  (Or use pip: python3 -m pip install pipx)"
    exit 1
fi
echo "✓ pipx found: $(pipx --version)"
echo

# Test 1: Validate pyproject.toml
echo "Test 1: Validating pyproject.toml..."
python3 << 'PYEOF'
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
    
assert config['project']['name'] == 'bazarr', "Name mismatch"
assert 'bazarr' in config['project']['scripts'], "No bazarr script entry"
assert config['project']['scripts']['bazarr'] == 'bazarr.cli:main', "Entry point incorrect"
print("✓ pyproject.toml is valid")
PYEOF
echo

# Test 2: Create virtual environment and test installation
echo "Test 2: Testing pip install in virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Upgrade pip first
pip install --quiet --upgrade pip setuptools wheel

# Install the package
pip install --quiet -e ".[postgres,dev]"

# Test imports
python3 << 'PYEOF'
from bazarr.cli import main
from bazarr.launcher import main as launcher_main
from bazarr.app.get_args import args
print("✓ All module imports successful")
PYEOF

# Test entry point
if bazarr --help > /dev/null 2>&1; then
    echo "✓ 'bazarr' command is accessible"
else
    echo "✗ 'bazarr' command not found"
    exit 1
fi

deactivate
echo

# Test 3: Test pipx installation (if pipx is available)
if command -v pipx &> /dev/null; then
    echo "Test 3: Testing pipx install..."
    
    # Create a temporary PIPX_HOME
    export PIPX_HOME="$PIPX_HOME"
    export PIPX_BIN_DIR="$PIPX_HOME/bin"
    mkdir -p "$PIPX_BIN_DIR"
    
    # Install via pipx
    pipx install --force-reinstall -q "$PROJECT_DIR" 2>&1 | grep -v "^WARNING" || true
    
    # Test the installed command
    if "$PIPX_BIN_DIR/bazarr" --help > /dev/null 2>&1; then
        echo "✓ pipx installation successful"
        echo "✓ 'bazarr' command is executable"
    else
        echo "✗ pipx installation failed or command not accessible"
        exit 1
    fi
    echo
fi

echo "============================================================"
echo "✓ All tests passed!"
echo "============================================================"
echo
echo "Installation methods:"
echo "  1. Virtual environment: python3 -m venv venv && source venv/bin/activate && pip install -e .[postgres,dev]"
echo "  2. pipx: pipx install . (from repository root)"
echo "  3. System-wide: sudo pip3 install ."
echo
echo "Running Bazarr:"
echo "  - With entry point: bazarr -c ~/.bazarr"
echo "  - As module: python3 -m bazarr -c ~/.bazarr"
echo "  - Development: bazarr --dev -c ./data"
echo
