# coding=utf-8
"""CLI entry point for Bazarr when installed as a package."""

import sys

# Import the main script logic
from bazarr.launcher import main

if __name__ == '__main__':
    sys.exit(main())
