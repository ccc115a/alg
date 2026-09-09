#!/bin/bash
set -x

echo "=== Building db6 ==="
cargo build

echo "=== Running tests ==="
cargo test

echo "=== Test complete ==="