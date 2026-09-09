#!/bin/bash
set -e

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <new_version> [commit_message]"
    echo "Example: $0 5.3.0 \"Add WebSocket support\""
    exit 1
fi

NEW_VERSION="$1"
COMMIT_MSG="${2:-}"

if [ -n "$COMMIT_MSG" ]; then
    COMMIT_MSG="v${NEW_VERSION}: ${COMMIT_MSG}"
else
    COMMIT_MSG="v${NEW_VERSION}"
fi
NAME="db6"

# 驗證版本格式
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be in format major.minor.patch (e.g. 5.3.0)"
    exit 1
fi

echo "=== Checking current version on crates.io ==="
PUBLISHED=$(curl -s "https://crates.io/api/v1/crates/${NAME}" | grep -o '"max_version":"[^"]*"' | cut -d'"' -f4)

if [ -n "$PUBLISHED" ]; then
    echo "Published version: $PUBLISHED"
    if [ "$NEW_VERSION" = "$PUBLISHED" ]; then
        echo "Error: version $NEW_VERSION is already published"
        exit 1
    fi
    # 比較版本號（用 sort -V）
    HIGHER=$(echo -e "$PUBLISHED\n$NEW_VERSION" | sort -V | tail -1)
    if [ "$HIGHER" != "$NEW_VERSION" ]; then
        echo "Error: $NEW_VERSION is not higher than published $PUBLISHED"
        exit 1
    fi
else
    echo "No published version found (first publish)"
fi

echo "=== Updating Cargo.toml version to $NEW_VERSION ==="
awk -v v="$NEW_VERSION" '/^\[package\]/ { pkg=1 } pkg && /^version = / { sub(/version = "[^"]*"/, "version = \"" v "\""); pkg=0 } 1' Cargo.toml > Cargo.toml.tmp && mv Cargo.toml.tmp Cargo.toml

echo "=== Updating db6py version to $NEW_VERSION ==="
awk -v v="$NEW_VERSION" '/^version = / { sub(/version = "[^"]*"/, "version = \"" v "\"") } 1' python/db6py/pyproject.toml > python/db6py/pyproject.toml.tmp && mv python/db6py/pyproject.toml.tmp python/db6py/pyproject.toml

echo "=== Updating db6nodejs version to $NEW_VERSION ==="
awk -v v="$NEW_VERSION" '/^  "version"/ { sub(/"[0-9]+\.[0-9]+\.[0-9]+"/, "\"" v "\"") } 1' nodejs/db6nodejs/package.json > nodejs/db6nodejs/package.json.tmp && mv nodejs/db6nodejs/package.json.tmp nodejs/db6nodejs/package.json

echo "=== Running tests ==="
cargo test

echo "=== Committing to git ==="
git add -A
git commit -m "$COMMIT_MSG"
git push

echo "=== Publishing to crates.io ==="
cargo publish

echo "=== Publishing db6py to PyPI ==="
./python/db6py/pub.sh

echo "=== Publishing db6nodejs to npm ==="
./nodejs/db6nodejs/pub.sh

echo "=== ${NEW_VERSION} published successfully ==="