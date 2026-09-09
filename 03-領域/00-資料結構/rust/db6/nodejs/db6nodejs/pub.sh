#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ -n "$1" ]; then
    VERSION="$1"
    node -e "const pkg=require('./package.json'); pkg.version='$VERSION'; require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2)+'\n');"
    echo "Version updated to v$VERSION"
else
    VERSION=$(grep '^  "version":' package.json | sed 's/.*"version": "\(.*\)".*/\1/')
fi
echo "Publishing db6nodejs v$VERSION to npm..."

# Clean
rm -rf dist/ build/

# Publish
npm publish

echo "Published db6nodejs v$VERSION to npm!"