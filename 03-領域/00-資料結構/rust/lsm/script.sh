#!/usr/bin/env bash
# script.sh — LSM-Tree CLI 完整示範腳本

set -uo pipefail

BIN="./target/debug/lsm"

echo "=================================================="
echo "         LSM-Tree CLI 完整示範"
echo "=================================================="
echo ""

echo "--- 1. 寫入資料 (put) ---"
echo "put <key> <value>"
echo "執行：put hello world"
echo "執行：put key1 value1"
echo "執行：put key2 value2"
echo ""

echo "--- 2. 讀取資料 (get) ---"
echo "get <key>"
echo "執行：get hello"
echo "執行：get missing"
echo ""

echo "--- 3. 刪除資料 (delete) ---"
echo "delete <key>"
echo "執行：delete key1"
echo "執行：get key1  (確認刪除)"
echo ""

echo "--- 4. 範圍查詢 (scan) ---"
echo "scan <start> <end>"
echo "執行：scan a z"
echo ""

echo "--- 5. 批次寫入 (batch) ---"
echo "batch <k1> <v1> <k2> <v2> ..."
echo "執行：batch b1 v1 b2 v2 b3 v3"
echo "執行：get b1"
echo "執行：get b2"
echo ""

echo "--- 6. 範圍刪除 (range_delete) ---"
echo "range_delete <start> <end>"
echo "執行：put rda 1"
echo "執行：put rdb 2"
echo "執行：put rdc 3"
echo "執行：put rdd 4"
echo "執行：range_delete rdb rdd"
echo "執行：get rda  (確認存在)"
echo "執行：get rdb  (確認刪除)"
echo "執行：get rdc  (確認刪除)"
echo "執行：get rdd  (確認存在)"
echo ""

echo "--- 7. 更新資料 (put 同一 key) ---"
echo "執行：put hello new_world"
echo "執行：get hello"
echo ""

echo "--- 8. 顯示統計 (stats) ---"
echo "執行：stats"
echo ""

echo "--- 9. 交易測試 (begin/commit) ---"
echo "執行：begin"
echo "執行：put txkey txvalue"
echo "執行：get txkey  (交易內可讀到)"
echo "執行：commit"
echo "執行：get txkey  (提交後仍可讀到)"
echo ""

echo "--- 10. 交易回滾 (rollback) ---"
echo "執行：begin"
echo "執行：put rollbackkey rollbackvalue"
echo "執行：rollback"
echo "執行：get rollbackkey  (應該找不到)"
echo ""

echo "--- 11. 磁碟模式 (disk) ---"
echo "執行：disk /tmp/lsm_demo.db"
echo "執行：put diskkey diskvalue"
echo "執行：flush"
echo "執行：quit"
echo ""

echo "=================================================="
echo "以下是實際執行結果："
echo "=================================================="

echo -e "put hello world\nput key1 value1\nput key2 value2\nget hello\nget missing\ndelete key1\nget key1\nscan a z\nbatch b1 v1 b2 v2 b3 v3\nget b1\nget b2\nput rda 1\nput rdb 2\nput rdc 3\nput rdd 4\nrange_delete rdb rdd\nget rda\nget rdb\nget rdc\nget rdd\nput hello new_world\nget hello\nstats\nbegin\nput txkey txvalue\nget txkey\ncommit\nget txkey\nbegin\nput rollbackkey rollbackvalue\nrollback\nget rollbackkey\ndisk /tmp/lsm_demo.db\nput diskkey diskvalue\nflush\nquit" | "$BIN"

echo ""
echo "=================================================="
echo "示範完成！"
echo "=================================================="

rm -rf /tmp/lsm_demo.db 2>/dev/null