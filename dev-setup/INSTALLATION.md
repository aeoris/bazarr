# Bazarr Installation Guide for Linux

This guide covers modern Python installation methods for Bazarr on Linux distributions like Ubuntu, Debian, and other DEB-based systems.

## Prerequisites

Ensure you have Python 3.8 or higher installed:

```bash
python3 --version
```

## Installation Methods

### Method 1: Virtual Environment (Recommended for Development)

Virtual environments provide isolation and prevent conflicts with system packages.

#### Step 1: Create a Virtual Environment

```bash
# Create a virtual environment
python3 -m venv ~/.venv/bazarr

# Activate it
source ~/.venv/bazarr/bin/activate
```

#### Step 2: Install Bazarr

From the repository root:

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Or install normally
pip install .

# For PostgreSQL support
pip install ".[postgres]"

# For both PostgreSQL and dev tools
pip install ".[dev,postgres]"
```

#### Step 3: Run Bazarr

```bash
# Using the entry point
bazarr

# Or using the module
python -m bazarr

# With custom config directory
bazarr -c /path/to/config

# With custom port
bazarr -p 8765
```

To deactivate the virtual environment:

```bash
deactivate
```

### Method 2: pipx (Recommended for End Users)

`pipx` installs applications in isolated environments automatically.

#### Step 1: Install pipx

```bash
# Ubuntu/Debian
sudo apt install pipx

# Or via pip
python3 -m pip install --user pipx

# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### Step 2: Install Bazarr

From the repository root:

```bash
pipx install .
```

Or from a release:

```bash
pipx install bazarr[postgres]
```

#### Step 3: Run Bazarr

```bash
# Using the command
bazarr

# With options
bazarr -c ~/.bazarr -p 6767

# View help
bazarr --help
```

To update Bazarr:

```bash
pipx upgrade bazarr
```

### Method 3: System-wide Installation (Not Recommended)

This method installs Bazarr globally. It's not recommended as it may conflict with system packages.

```bash
sudo pip3 install .
sudo pip3 install ".[postgres]"
```

Run with:

```bash
bazarr
```

## Configuration

### Data Directory

By default, Bazarr stores configuration and data in one of these locations:

- **Development installations**: `./data` (relative to repository root)
- **pip/pipx installations**: `~/.bazarr` (in your home directory)

You can override this with the `-c` option:

```bash
bazarr -c /custom/data/path
```

Ensure the directory exists and is writable:

```bash
mkdir -p /custom/data/path
```

### Environment Variables

- `NO_UPDATE=true`: Disable auto-update functionality
- `NO_CLI=true`: Disable CLI argument parsing (for containerized deployments)

Example:

```bash
NO_UPDATE=true bazarr -c ~/.bazarr
```

## Uninstallation

### Virtual Environment

```bash
# Deactivate
deactivate

# Remove the directory
rm -rf ~/.venv/bazarr
```

### pipx

```bash
pipx uninstall bazarr
```

### System-wide

```bash
sudo pip3 uninstall bazarr
```

## Systemd Service (Optional)

Create a systemd service to run Bazarr automatically on boot.

### Step 1: Create service file

```bash
sudo nano /etc/systemd/system/bazarr.service
```

### Step 2: Add service configuration

Replace `<USERNAME>` and `/path/to/venv` with your values:

```ini
[Unit]
Description=Bazarr - Subtitle Manager for Sonarr and Radarr
After=network.target syslog.target

[Service]
Type=simple
User=<USERNAME>
Group=<USERNAME>
WorkingDirectory=/home/<USERNAME>

# For virtual environment
ExecStart=/home/<USERNAME>/.venv/bazarr/bin/bazarr -c /home/<USERNAME>/.bazarr

# Or for pipx
# ExecStart=/home/<USERNAME>/.local/bin/bazarr -c /home/<USERNAME>/.bazarr

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 3: Enable and start service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable bazarr

# Start the service
sudo systemctl start bazarr

# Check status
sudo systemctl status bazarr

# View logs
sudo journalctl -u bazarr -f
```

## Integration with Sonarr and Radarr

Bazarr requires Sonarr and Radarr to be running and accessible. Configure the following in Bazarr's web interface:

1. **Sonarr URL**: e.g., `http://localhost:8989`
2. **Radarr URL**: e.g., `http://localhost:7878`
3. **API Keys**: Obtain from your Sonarr and Radarr instances

## Troubleshooting

### Command not found: bazarr

Ensure the installation completed successfully:

```bash
# For virtual environment
which bazarr  # Should show path in venv
source ~/.venv/bazarr/bin/activate

# For pipx
which bazarr  # Should show ~/.local/bin/bazarr
export PATH="$HOME/.local/bin:$PATH"
```

### Permission denied errors

Ensure your data directory is writable:

```bash
ls -la ~/.bazarr
chmod u+rwx ~/.bazarr
```

### Port already in use

Use a different port:

```bash
bazarr -p 6768
```

Or find and stop the process using port 6767:

```bash
lsof -i :6767
kill -9 <PID>
```

### Python version incompatible

Bazarr requires Python 3.8+. Check your version:

```bash
python3 --version
```

Update Python if needed:

```bash
sudo apt update
sudo apt upgrade python3
```

## Support

- **Documentation**: https://wiki.bazarr.media
- **Discord**: https://discord.gg/MH2e2eb
- **Issues**: https://github.com/morpheus65535/bazarr/issues
