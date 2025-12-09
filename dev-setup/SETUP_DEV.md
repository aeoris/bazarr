# Bazarr Development Setup for Linux

This guide helps developers set up a local development environment for Bazarr.

## Quick Start

### Using Virtual Environment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/morpheus65535/bazarr.git
cd bazarr

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev,postgres]"

# 4. Run Bazarr
bazarr --dev -c ./data

# 5. Access web UI
# Navigate to http://localhost:6767
```

### Using Docker Compose (Alternative)

```bash
# Navigate to dev setup directory
cd dev-setup

# Run test setup
bash test-setup.sh

# Start services
docker compose up

# Access web UI
# Navigate to http://localhost:6767 (backend)
# Navigate to http://localhost:5173 (frontend dev server)
```

## Development Workflow

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=bazarr tests/

# Run specific test file
pytest tests/test_file.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Lint with flake8 (via pytest-flakes)
pytest --flakes

# Style check with PEP8 (via pytest-pep8)
pytest --pep8

# Format with black (if installed)
black bazarr/

# Sort imports with isort (if installed)
isort bazarr/
```

### Debug Mode

```bash
# Enable debug logging
bazarr --debug -c ./data

# With custom port
bazarr --debug -p 8765 -c ./data
```

### Database Revision

If you make database changes:

```bash
# Create a new migration
bazarr --create-db-revision -c ./data
```

## Project Structure

```
bazarr/
├── bazarr/              # Main package
│   ├── app/             # Flask application and config
│   ├── api/             # REST API endpoints
│   ├── subtitles/       # Subtitle management
│   ├── sonarr/          # Sonarr integration
│   ├── radarr/          # Radarr integration
│   ├── plex/            # Plex integration
│   ├── languages/       # Language handling
│   ├── utilities/       # Utility functions
│   ├── main.py          # Application entry point
│   ├── launcher.py      # Subprocess launcher
│   └── cli.py           # CLI entry point for pipx
├── bazarr.py            # Development launcher (legacy)
├── frontend/            # Vue.js frontend
├── migrations/          # Database migrations
├── libs/                # Third-party libraries
├── custom_libs/         # Custom library patches
├── dev-setup/           # Docker development setup
├── pyproject.toml       # Modern Python packaging
├── requirements.txt     # Runtime dependencies
└── README.md            # Project README
```

## Common Tasks

### Adding Dependencies

1. Update `pyproject.toml`:
   ```toml
   dependencies = [
       # ... existing deps
       "new-package>=1.0.0",
   ]
   ```

2. Or use pip install with `-e`:
   ```bash
   pip install new-package
   pip freeze > requirements.txt
   ```

3. Reinstall in editable mode:
   ```bash
   pip install -e ".[dev,postgres]"
   ```

### Database Queries

Access the database via Flask shell:

```bash
# Enter Flask shell
export FLASK_APP=bazarr.app
flask shell

# Then in Python shell:
from bazarr.app.database import database, Movie, Episode
movies = database.session.query(Movie).all()
```

### API Testing

Use curl or a tool like Postman:

```bash
# Get available subtitles
curl http://localhost:6767/api/subtitles

# Get system status
curl http://localhost:6767/api/system/status
```

## Troubleshooting

### Import errors with custom_libs

Make sure you're in the virtual environment:

```bash
source venv/bin/activate
python -c "import bazarr"
```

### Database locked errors

Delete the database and restart:

```bash
rm -f data/bazarr.db
bazarr -c ./data
```

### Port conflicts

Use a different port:

```bash
bazarr -p 8765 -c ./data
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test: `pytest`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/my-feature`
6. Submit a pull request

## Resources

- **Wiki**: https://wiki.bazarr.media
- **Discord**: https://discord.gg/MH2e2eb
- **GitHub**: https://github.com/morpheus65535/bazarr
- **Issue Tracker**: https://github.com/morpheus65535/bazarr/issues
