#!/bin/bash
set -e
set -x

echo "===== Test 1: Direct execution ====="
EXPECTED=$(node factorial.js)
echo "$EXPECTED"

echo ""
echo "===== Test 2: Single interpretation ====="
ACTUAL1=$(node js0i.js factorial.js)
echo "$ACTUAL1"

if [ "$EXPECTED" = "$ACTUAL1" ]; then
  echo "PASS: Single interpretation matches direct execution"
else
  echo "FAIL: Single interpretation differs"
  echo "Expected: $EXPECTED"
  echo "Got:      $ACTUAL1"
  exit 1
fi

echo ""
echo "===== Test 3: Self-interpretation ====="
ACTUAL2=$(node js0i.js js0i.js factorial.js)
echo "$ACTUAL2"

if [ "$EXPECTED" = "$ACTUAL2" ]; then
  echo "PASS: Self-interpretation matches direct execution"
else
  echo "FAIL: Self-interpretation differs"
  echo "Expected: $EXPECTED"
  echo "Got:      $ACTUAL2"
  exit 1
fi

echo ""
echo "All tests passed!"
