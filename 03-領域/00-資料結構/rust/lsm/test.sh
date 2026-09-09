#!/usr/bin/env bash
# test.sh — LSM-Tree 測試腳本

set -uo pipefail

BIN="./target/debug/lsm"
PASS=0
FAIL=0

GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

section() {
    echo ""
    echo -e "${GREEN}── $1 ──${RESET}"
}

echo "=== LSM-Tree Test Suite ==="
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
    if echo "$OUT" | grep -q "put <key>"; then
        echo -e "${GREEN}PASS${RESET}  CLI help works"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  CLI help failed"
        ((FAIL++))
    fi

    OUT=$(echo -e "put hello world\nget hello\nquit" | "$BIN" 2>&1)
    echo "$OUT" | grep -q "world" && {
        echo -e "${GREEN}PASS${RESET}  Put and get work"
        ((PASS++))
    } || {
        echo -e "${RED}FAIL${RESET}  Put and get failed"
        ((FAIL++))
    }

    OUT=$(echo -e "put a 1\nput b 2\nput c 3\nscan a c\nquit" | "$BIN" 2>&1)
    echo "$OUT" | grep -q "a -> 1" && echo "$OUT" | grep -q "b -> 2" && {
        echo -e "${GREEN}PASS${RESET}  Scan works"
        ((PASS++))
    } || {
        echo -e "${RED}FAIL${RESET}  Scan failed"
        ((FAIL++))
    }

    OUT=$(echo -e "put delkey value\ndelete delkey\nget delkey\nquit" | "$BIN" 2>&1)
    echo "$OUT" | grep -q "找不到" && {
        echo -e "${GREEN}PASS${RESET}  Delete works"
        ((PASS++))
    } || {
        echo -e "${RED}FAIL${RESET}  Delete failed"
        ((FAIL++))
    }

    OUT=$(echo -e "put upkey old\nput upkey new\nget upkey\nquit" | "$BIN" 2>&1)
    echo "$OUT" | grep -q "new" && ! echo "$OUT" | grep -q "old" && {
        echo -e "${GREEN}PASS${RESET}  Update works"
        ((PASS++))
    } || {
        echo -e "${RED}FAIL${RESET}  Update failed"
        ((FAIL++))
    }

    OUT=$(echo -e "put k1 v1\nput k2 v2\nstats\nquit" | "$BIN" 2>&1)
    echo "$OUT" | grep -q "key數量：2" && {
        echo -e "${GREEN}PASS${RESET}  Stats work"
        ((PASS++))
    } || {
        echo -e "${RED}FAIL${RESET}  Stats failed"
        ((FAIL++))
    }
fi

section "Transaction Tests"

OUT=$(echo -e "begin\nput txkey txvalue\nget txkey\ncommit\nget txkey\nquit" | "$BIN" 2>&1)
echo "$OUT" | grep -q "交易已開始" && echo "$OUT" | grep -q "交易已提交" && echo "$OUT" | grep -q "txvalue" && {
    echo -e "${GREEN}PASS${RESET}  Transaction commit works"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${RESET}  Transaction commit failed"
    ((FAIL++))
}

OUT=$(echo -e "begin\nput rollbackkey rollbackvalue\nrollback\nget rollbackkey\nquit" | "$BIN" 2>&1)
echo "$OUT" | grep -q "交易已rollback" && echo "$OUT" | grep -q "找不到" && {
    echo -e "${GREEN}PASS${RESET}  Transaction rollback works"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${RESET}  Transaction rollback failed"
    ((FAIL++))
}

section "Batch Operations"

OUT=$(echo -e "batch k1 v1 k2 v2 k3 v3\nget k1\nget k2\nget k3\nquit" | "$BIN" 2>&1)
echo "$OUT" | grep -q "v1" && echo "$OUT" | grep -q "v2" && echo "$OUT" | grep -q "v3" && {
    echo -e "${GREEN}PASS${RESET}  Batch put works"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${RESET}  Batch put failed"
    ((FAIL++))
}

section "Disk Persistence"

rm -f /tmp/lsm_test.db
OUT=$(echo -e "disk /tmp/lsm_test.db\nput diskkey diskvalue\nflush\nquit" | "$BIN" 2>&1)
echo "$OUT" | grep -q "磁碟模式" && [[ -f /tmp/lsm_test.db/wal.log ]] && {
    echo -e "${GREEN}PASS${RESET}  Disk mode creates files"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${RESET}  Disk mode failed"
    ((FAIL++))
}

section "Disk Recovery"

rm -rf /tmp/lsm_recover_test
OUT=$(echo -e "disk /tmp/lsm_recover_test\nput rec1 val1\nput rec2 val2\ncommit\nflush\nquit" | "$BIN" 2>&1)
OUT=$(echo -e "disk /tmp/lsm_recover_test\nget rec1\nget rec2\nquit" | "$BIN" 2>&1)
echo "$OUT" | grep -q "val1" && echo "$OUT" | grep -q "val2" && {
    echo -e "${GREEN}PASS${RESET}  Disk persistence and recovery work"
    ((PASS++))
} || {
    echo -e "${RED}FAIL${RESET}  Disk persistence and recovery failed"
    ((FAIL++))
}
rm -rf /tmp/lsm_recover_test /tmp/lsm_test.db

section "Range Delete"

OUT=$(echo -e "put rda 1\nput rdb 2\nput rdc 3\nput rdd 4\nrange_delete rdb rdd\nget rda\nget rdb\nget rdc\nget rdd\nquit" | "$BIN" 2>&1)
NOT_FOUND_COUNT=$(echo "$OUT" | grep -c "找不到" || true)
if echo "$OUT" | grep -q "找到：1" && echo "$OUT" | grep -q "找到：4" && [[ $NOT_FOUND_COUNT -eq 2 ]]; then
    echo -e "${GREEN}PASS${RESET}  Range delete works"
    ((PASS++))
else
    echo -e "${RED}FAIL${RESET}  Range delete failed (not found count: $NOT_FOUND_COUNT)"
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