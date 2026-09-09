#!/usr/bin/env bash
# script.sh — btree CLI 完整示範腳本

set -uo pipefail

BIN="./target/debug/btree"

echo "=================================================="
echo "           B+Tree CLI 完整示範"
echo "=================================================="
echo ""

echo "--- 1. 插入資料 (insert) ---"
echo "insert <key> <value>"
echo "執行：insert 1 hello"
echo "執行：insert 2 world"
echo "執行：insert 3 btree"
echo "執行：insert 10 ten"
echo "執行：insert 20 twenty"
echo ""

echo "--- 2. 查詢單一 key (search) ---"
echo "search <key>"
echo "執行：search 1"
echo "執行：search 5  (不存在的 key)"
echo ""

echo "--- 3. 範圍查詢 (range) ---"
echo "range <start> <end>"
echo "執行：range 1 10"
echo ""

echo "--- 4. 刪除資料 (delete) ---"
echo "delete <key>"
echo "執行：delete 3"
echo "執行：search 3  (確認已刪除)"
echo ""

echo "--- 5. 顯示資料筆數 (len) ---"
echo "執行：len"
echo ""

echo "--- 6. 更新資料 (insert 同一 key) ---"
echo "執行：insert 1 updated_hello"
echo "執行：search 1"
echo ""

echo "--- 7. 磁碟模式 (disk) ---"
echo "執行：disk on /tmp/btree_demo.db"
echo "執行：insert 100 disk_value"
echo "執行：search 100"
echo "執行：flush"
echo "執行：quit"
echo ""

echo "=================================================="
echo "以下是實際執行結果："
echo "=================================================="

echo -e "insert 1 hello\ninsert 2 world\ninsert 3 btree\ninsert 10 ten\ninsert 20 twenty\nsearch 1\nsearch 5\nrange 1 10\ndelete 3\nsearch 3\nlen\ninsert 1 updated_hello\nsearch 1\ndisk on /tmp/btree_demo.db\ninsert 100 disk_value\nsearch 100\nflush\nquit" | "$BIN"

echo ""
echo "=================================================="
echo "示範完成！"
echo "=================================================="