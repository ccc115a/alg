#!/bin/bash
set -e

cd "$(dirname "$0")"

cleanup() {
    echo "Stopping db6 server..."
    kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting db6 server..."
cargo run --bin server &
SERVER_PID=$!
sleep 3

for i in {1..10}; do
    curl -s http://localhost:50052/health > /dev/null 2>&1 && break
    sleep 1
done

cd python/db6py
echo "Installing db6py..."
uv pip install -e ".[websocket]" 2>/dev/null || uv pip install -e .

echo "Running pytest..."
uv run pytest tests/ -v --tb=short

echo "Done!"