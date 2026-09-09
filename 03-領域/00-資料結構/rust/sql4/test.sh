#!/usr/bin/env bash
# test.sh — sql4 CLI 自動測試
# 用法：./test.sh [path/to/sql4]
# 預設找 ./target/debug/sql4

set -uo pipefail

# ── 設定 ──────────────────────────────────────────────────────────────────
BIN="${1:-./target/debug/sql4}"
PASS=0
FAIL=0
SKIP=0

# 顏色
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
RESET="\033[0m"

# ── 輔助函式 ──────────────────────────────────────────────────────────────

# run_sql <sql...>  → 執行 SQL，回傳 stdout（去掉提示符與 banner）
run_sql() {
    printf '%s\n' "$@" ".quit" \
        | "$BIN" 2>&1 \
        | sed 's/^sql4> Error:/Error:/' \
        | grep -v "^sql4 v" \
        | grep -v "^Type .help" \
        | grep -v "^$" \
        | grep -v "^sql4>" \
        | grep -v "^   \.\.\.>" \
        | grep -v "^Bye" \
        || true
}

# assert_contains <label> <pattern> <actual>
assert_contains() {
    local label="$1" pattern="$2" actual="$3"
    if echo "$actual" | grep -q "$pattern" 2>/dev/null; then
        echo -e "${GREEN}PASS${RESET}  $label"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  $label"
        echo "       expect to contain: $pattern"
        echo "       got:"
        echo "$actual" | sed 's/^/         /'
        ((FAIL++))
    fi
}

# assert_not_contains <label> <pattern> <actual>
assert_not_contains() {
    local label="$1" pattern="$2" actual="$3"
    if ! echo "$actual" | grep -q "$pattern" 2>/dev/null; then
        echo -e "${GREEN}PASS${RESET}  $label"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  $label"
        echo "       expect NOT to contain: $pattern"
        echo "       got:"
        echo "$actual" | sed 's/^/         /'
        ((FAIL++))
    fi
}

# assert_line_count <label> <expected_n> <actual>
assert_line_count() {
    local label="$1" expected="$2" actual="$3"
    local count
    count=$(echo "$actual" | grep -c "^" || true)
    if [[ "$count" -eq "$expected" ]]; then
        echo -e "${GREEN}PASS${RESET}  $label"
        ((PASS++))
    else
        echo -e "${RED}FAIL${RESET}  $label"
        echo "       expected $expected lines, got $count"
        echo "$actual" | sed 's/^/         /'
        ((FAIL++))
    fi
}

section() {
    echo ""
    echo -e "${YELLOW}── $1 ──${RESET}"
}

# ── 前置檢查 ──────────────────────────────────────────────────────────────

if [[ ! -x "$BIN" ]]; then
    echo -e "${RED}ERROR${RESET}: binary not found: $BIN"
    echo "Run: cargo build"
    exit 1
fi

echo "sql4 CLI Test Suite"
echo "Binary: $BIN"
echo "=================================================="

# ── 1. DDL ────────────────────────────────────────────────────────────────
section "DDL"

OUT=$(run_sql "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);")
assert_contains "CREATE TABLE" "table created" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT);" \
    "CREATE TABLE users (id INTEGER, name TEXT);")
assert_contains "CREATE TABLE duplicate → error" "already exists" "$OUT"

OUT=$(run_sql "CREATE TABLE IF NOT EXISTS t (id INTEGER);")
assert_contains "CREATE TABLE IF NOT EXISTS" "table created" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t2 (id INTEGER);" \
    "DROP TABLE t2;")
assert_contains "DROP TABLE" "table dropped" "$OUT"

OUT=$(run_sql "DROP TABLE IF EXISTS ghost;")
assert_contains "DROP TABLE IF EXISTS (no-op)" "does not exist" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t3 (id INTEGER);" \
    "DROP TABLE t3;" \
    "DROP TABLE t3;")
assert_contains "DROP TABLE already gone → error" "does not exist" "$OUT"

# ── 2. INSERT ─────────────────────────────────────────────────────────────
section "INSERT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);")
assert_contains "INSERT basic" "1 row(s) inserted" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users (id, name, age) VALUES (1, 'Bob', 25);")
assert_contains "INSERT with column list" "1 row(s) inserted" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER, val TEXT);" \
    "INSERT INTO t VALUES (1,'a'), (2,'b'), (3,'c');")
assert_contains "INSERT multi-row" "3 row(s) inserted" "$OUT"

# ── 3. SELECT ─────────────────────────────────────────────────────────────
section "SELECT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users;")
assert_contains "SELECT *" "Alice" "$OUT"
assert_contains "SELECT * all rows" "(3 rows)" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "SELECT name, age FROM users;")
assert_contains "SELECT projection (data)" "Alice" "$OUT"
assert_not_contains "SELECT projection no id" "| id" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users WHERE id = 2;")
assert_contains "SELECT WHERE eq" "Bob" "$OUT"
assert_contains "SELECT WHERE eq one row" "(1 row)" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users WHERE age > 28;")
assert_contains "SELECT WHERE gt" "Alice" "$OUT"
assert_contains "SELECT WHERE gt Carol" "Carol" "$OUT"
assert_not_contains "SELECT WHERE gt excludes Bob" "Bob" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users WHERE age BETWEEN 25 AND 30;")
assert_contains "SELECT BETWEEN" "Alice" "$OUT"
assert_contains "SELECT BETWEEN Bob" "Bob" "$OUT"
assert_not_contains "SELECT BETWEEN no Carol" "Carol" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users WHERE name LIKE 'A%';")
assert_contains "SELECT LIKE" "Alice" "$OUT"
assert_not_contains "SELECT LIKE excludes others" "Bob" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users WHERE id IN (1, 3);")
assert_contains "SELECT IN" "Alice" "$OUT"
assert_contains "SELECT IN Carol" "Carol" "$OUT"
assert_not_contains "SELECT IN no Bob" "Bob" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users ORDER BY age ASC;")
# Bob(25) 應排第一
assert_contains "SELECT ORDER BY ASC (Bob first)" "Bob" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users ORDER BY age DESC LIMIT 2;")
assert_contains "SELECT LIMIT" "Carol" "$OUT"
assert_contains "SELECT LIMIT 2 rows" "(2 rows)" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT * FROM users ORDER BY id ASC LIMIT 2 OFFSET 1;")
assert_contains "SELECT LIMIT OFFSET" "Bob" "$OUT"
assert_not_contains "SELECT LIMIT OFFSET no Alice" "Alice" "$OUT"

# ── 4. 聚合函式 ───────────────────────────────────────────────────────────
section "Aggregate Functions"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT COUNT(*) FROM users;")
assert_contains "COUNT(*)" "3" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "INSERT INTO users VALUES (3, 'Carol', 35);" \
    "SELECT MAX(age), MIN(age) FROM users;")
assert_contains "MAX(age)" "35" "$OUT"
assert_contains "MIN(age)" "25" "$OUT"

# ── 5. UPDATE ─────────────────────────────────────────────────────────────
section "UPDATE"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "UPDATE users SET age = 99 WHERE id = 1;" \
    "SELECT age FROM users WHERE id = 1;")
assert_contains "UPDATE basic" "99" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "UPDATE users SET age = 0;" \
    "SELECT * FROM users WHERE age != 0;")
assert_contains "UPDATE all rows" "(0 rows)" "$OUT"

# ── 6. DELETE ─────────────────────────────────────────────────────────────
section "DELETE"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "DELETE FROM users WHERE id = 1;" \
    "SELECT * FROM users;")
assert_not_contains "DELETE WHERE" "Alice" "$OUT"
assert_contains "DELETE WHERE keeps others" "Bob" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT, age INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice', 30);" \
    "INSERT INTO users VALUES (2, 'Bob', 25);" \
    "DELETE FROM users;" \
    "SELECT * FROM users;")
assert_contains "DELETE all" "(0 rows)" "$OUT"

# ── 7. JOIN ───────────────────────────────────────────────────────────────
section "JOIN"

OUT=$(run_sql \
    "CREATE TABLE users (id INTEGER, name TEXT);" \
    "CREATE TABLE orders (oid INTEGER, uid INTEGER, amount INTEGER);" \
    "INSERT INTO users VALUES (1, 'Alice');" \
    "INSERT INTO users VALUES (2, 'Bob');" \
    "INSERT INTO orders VALUES (1, 1, 100);" \
    "INSERT INTO orders VALUES (2, 1, 200);" \
    "INSERT INTO orders VALUES (3, 2, 50);" \
    "SELECT * FROM users JOIN orders ON users.id = orders.uid;")
assert_contains "INNER JOIN" "Alice" "$OUT"
assert_contains "INNER JOIN row count" "(3 rows)" "$OUT"

# ── 8. 交易 ───────────────────────────────────────────────────────────────
section "Transaction"

OUT=$(run_sql \
    "BEGIN;" \
    "CREATE TABLE t (id INTEGER);" \
    "INSERT INTO t VALUES (1);" \
    "COMMIT;" \
    "SELECT * FROM t;")
assert_contains "BEGIN/COMMIT" "1" "$OUT"

OUT=$(run_sql "ROLLBACK;")
assert_contains "ROLLBACK" "rolled back" "$OUT"

# ── 9. 字串函式 ───────────────────────────────────────────────────────────
section "String Functions"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER, name TEXT);" \
    "INSERT INTO t VALUES (1, 'Alice');" \
    "SELECT UPPER(name) FROM t;")
assert_contains "UPPER()" "ALICE" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER, name TEXT);" \
    "INSERT INTO t VALUES (1, 'Alice');" \
    "SELECT LOWER(name) FROM t;")
assert_contains "LOWER()" "alice" "$OUT"

# ── 10. 點指令 ────────────────────────────────────────────────────────────
section "Dot Commands"

OUT=$(run_sql ".help")
assert_contains ".help" "tables" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER);" \
    ".tables")
assert_contains ".tables" "t" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE products (id INTEGER, name TEXT, price REAL);" \
    ".schema products")
assert_contains ".schema" "INTEGER" "$OUT"
assert_contains ".schema columns" "name" "$OUT"

# ── 11. FTS 全文檢索 ──────────────────────────────────────────────────────
section "Full-Text Search (FTS)"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE articles USING fts5(title, body);" \
    "INSERT INTO articles VALUES ('Rust Programming', 'Fast and memory safe systems language');" \
    "INSERT INTO articles VALUES ('Python Basics', 'Easy to learn scripting language');" \
    "INSERT INTO articles VALUES ('資料庫設計', '關聯式資料庫的基本概念與正規化');" \
    "SELECT * FROM articles WHERE articles MATCH 'rust';")
assert_contains "FTS English search" "Rust Programming" "$OUT"
assert_not_contains "FTS English search excludes others" "Python" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE articles USING fts5(title, body);" \
    "INSERT INTO articles VALUES ('Rust Programming', 'Fast and memory safe');" \
    "INSERT INTO articles VALUES ('Python Basics', 'Easy scripting');" \
    "SELECT * FROM articles WHERE articles MATCH 'rust AND memory';")
assert_contains "FTS AND" "Rust Programming" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE articles USING fts5(title, body);" \
    "INSERT INTO articles VALUES ('Rust Programming', 'Fast systems language');" \
    "INSERT INTO articles VALUES ('Python Basics', 'Easy scripting');" \
    "INSERT INTO articles VALUES ('Go Concurrency', 'Concurrent systems');" \
    "SELECT * FROM articles WHERE articles MATCH 'rust OR python';")
assert_contains "FTS OR" "Rust Programming" "$OUT"
assert_contains "FTS OR Python" "Python" "$OUT"
assert_not_contains "FTS OR no Go" "Go Concurrency" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE docs USING fts5(title, body);" \
    "INSERT INTO docs VALUES ('資料庫', '關聯式資料庫設計原則');" \
    "INSERT INTO docs VALUES ('程式語言', 'Rust 程式語言介紹');" \
    "SELECT * FROM docs WHERE docs MATCH '資料';")
assert_contains "FTS CJK search" "資料庫" "$OUT"
assert_not_contains "FTS CJK excludes others" "程式語言" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE docs USING fts5(title, body);" \
    "INSERT INTO docs VALUES ('日本語テスト', 'データベースとプログラミング');" \
    "SELECT * FROM docs WHERE docs MATCH 'デー';")
assert_contains "FTS Japanese bigram (デー)" "日本語" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE docs USING fts5(title, body);" \
    "INSERT INTO docs VALUES ('Rust lang', 'Fast memory safe systems');" \
    "SELECT * FROM docs WHERE docs MATCH 'memory AND safe';")
assert_contains "FTS AND search (memory AND safe)" "Rust" "$OUT"

OUT=$(run_sql \
    "CREATE VIRTUAL TABLE docs USING fts5(title, body);" \
    "INSERT INTO docs VALUES ('Rust lang', 'systems language');" \
    "SELECT * FROM docs WHERE docs MATCH 'javascript';")
assert_contains "FTS no result" "(0 rows)" "$OUT"

# ── 12. IS NULL ───────────────────────────────────────────────────────────
section "NULL Handling"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER, val TEXT);" \
    "INSERT INTO t VALUES (1, NULL);" \
    "INSERT INTO t VALUES (2, 'hello');" \
    "SELECT * FROM t WHERE val IS NULL;")
assert_contains "IS NULL" "(1 row)" "$OUT"

OUT=$(run_sql \
    "CREATE TABLE t (id INTEGER, val TEXT);" \
    "INSERT INTO t VALUES (1, NULL);" \
    "INSERT INTO t VALUES (2, 'hello');" \
    "SELECT * FROM t WHERE val IS NOT NULL;")
assert_contains "IS NOT NULL" "hello" "$OUT"

# ── 結果摘要 ──────────────────────────────────────────────────────────────

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