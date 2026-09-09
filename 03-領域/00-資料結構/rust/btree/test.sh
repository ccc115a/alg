#!/usr/bin/env bash
# test.sh — btree 測試腳本
# 用法：./test.sh [path/to/btree]

set -uo pipefail

BIN="${1:-./target/debug/btree}"
PASS=0
FAIL=0

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

section() {
    echo ""
    echo -e "${GREEN}── $1 ──${RESET}"
}

echo "=== B+Tree Test Suite ==="
echo "Binary: $BIN"
echo "=================================================="

section "Unit Tests (cargo test)"

if cargo test --manifest-path "$(dirname "$0")/Cargo.toml" 2>&1; then
    echo -e "${GREEN}PASS${RESET}  All unit tests passed"
    ((PASS++))
else
    echo -e "${RED}FAIL${RESET}  Unit tests failed"
    ((FAIL++))
fi

section "Build Check"

if cargo build --manifest-path "$(dirname "$0")/Cargo.toml" 2>&1; then
    echo -e "${GREEN}PASS${RESET}  Build successful"
    ((PASS++))
else
    echo -e "${RED}FAIL${RESET}  Build failed"
    ((FAIL++))
fi

section "CLI Smoke Test"

if [[ ! -x "$BIN" ]]; then
    echo -e "${RED}FAIL${RESET}  Binary not found: $BIN"
    ((FAIL++))
else
    echo -e "${GREEN}PASS${RESET}  Binary exists"
    ((PASS++))
    
    OUT=$(echo -e "help\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "insert"; then
        echo -e "${GREEN}PASS${RESET}  CLI help works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  CLI help failed"
        ((FAIL++))
    fi
    
    OUT=$(echo -e "insert 1 hello\nsearch 1\nlen\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "hello"; then
        echo -e "${GREEN}PASS${RESET}  Insert and search work"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  Insert and search failed"
        ((FAIL++))
    fi
    
    OUT=$(echo -e "insert 10 value10\ninsert 20 value20\ninsert 5 value5\nrange 5 15\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "value5" && echo "$OUT" | grep -q "value10"; then
        echo -e "${GREEN}PASS${RESET}  Range search works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  Range search failed"
        ((FAIL++))
    fi
    
    OUT=$(echo -e "insert 100 old\ninsert 100 new\nsearch 100\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "new" && ! echo "$OUT" | grep -q "old"; then
        echo -e "${GREEN}PASS${RESET}  Update works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  Update failed"
        ((FAIL++))
    fi
    
    OUT=$(echo -e "insert 50 deleteme\ndelete 50\nsearch 50\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "找不到"; then
        echo -e "${GREEN}PASS${RESET}  Delete works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  Delete failed"
        ((FAIL++))
    fi
fi

section "Disk Persistence Test"

OUT=$(echo -e "disk on /tmp/btree_test.db\ninsert 1 diskval\nflush\nquit" | "$BIN" 2>&1)
if [[ -f /tmp/btree_test.db ]]; then
    echo -e "${GREEN}PASS${RESET}  Disk mode creates file"
    ((PASS++))
    
    OUT=$(echo -e "disk on /tmp/btree_test.db\nsearch 1\nquit" | "$BIN" 2>&1)
    if echo "$OUT" | grep -q "diskval"; then
        echo -e "${GREEN}PASS${RESET}  Disk persistence works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  Disk persistence failed"
        ((FAIL++))
    fi
    
    rm -f /tmp/btree_test.db /tmp/btree_test.sql4wal
else
    echo -e "${RED}FAIL${RESET}  Disk mode failed"
    ((FAIL++))
fi

echo ""
echo "=================================================="
TOTAL=$((PASS + FAIL))
echo -e "Results: ${GREEN}${PASS} passed${RESET}, ${RED}${FAIL} failed${RESET} / ${TOTAL} total"

if [[ $FAIL -gt 0 ]]; then
    exit 1
else
    echo -e "${GREEN}All tests passed!${RESET}"
    exit 0
fi