#!/bin/bash
set -x

echo "=== Testing db6 Examples ==="

EXAMPLES=(
    "kv_basic"
    "sql_basic"
    "fts_basic"
    "memory_engine"
    "btree_engine"
    "lsm_engine"
    "multi_engine"
)

PASS=0
FAIL=0

for ex in "${EXAMPLES[@]}"; do
    echo ""
    echo "--- Testing $ex ---"
    if cargo run --example "$ex" 2>&1; then
        echo "PASS: $ex"
        ((PASS++))
    else
        echo "FAIL: $ex"
        ((FAIL++))
    fi
done

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo "All examples passed!"
    exit 0
else
    echo "Some examples failed!"
    exit 1
fi