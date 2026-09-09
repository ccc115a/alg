#!/bin/bash
set -x

cd "$(dirname "$0")"

cargo run --example basic
cargo run --example word_count
cargo run --example phonebook

echo "All examples completed successfully!"