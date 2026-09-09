#!/bin/bash
set -e

cd "$(dirname "$0")"

VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Publishing db6py v$VERSION to PyPI..."

# Clean
rm -rf dist/ build/ *.egg-info

# Install build tools
uv pip install build twine

# Build
echo "Building..."
python3 -m build

# Upload to PyPI
echo "Uploading to PyPI..."
python3 -m twine upload dist/*

echo "Published db6py v$VERSION to PyPI!"