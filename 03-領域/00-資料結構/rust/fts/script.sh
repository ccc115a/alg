#!/bin/bash
set -x

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJ_DIR"

echo "=== 1. cargo build ==="
cargo build 2>&1 || exit 1

echo "=== 2. Startup: 載入 100 筆文件 ==="
output=$(echo ":quit" | cargo run 2>&1)
echo "$output" | grep -q "載入 100 筆文件" || { echo "FAIL: 文件數量錯誤"; exit 1; }
echo "$output" | grep -q "索引" || { echo "FAIL: 缺少詞項統計"; exit 1; }
echo "PASS"

echo "=== 3. Empty input ==="
output=$(printf "\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "FTS 全文檢索系統" || { echo "FAIL: 空輸入崩潰"; exit 1; }
echo "PASS"

echo "=== 4. CJK 單詞搜尋 (OR) ==="
output=$(printf "人工智慧\n:quit\n" | cargo run 2>&1)
count=$(echo "$output" | grep -c "找到.*筆結果")
echo "$output" | grep -q "人工智慧" || { echo "FAIL: 未找到 CJK 結果"; exit 1; }
echo "PASS ($count 次搜尋)"

echo "=== 5. CJK AND 搜尋（多詞交集） ==="
output=$(printf "區塊鏈 金融\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "區塊鏈技術正在改變金融產業的樣貌" || { echo "FAIL: AND 結果錯誤"; exit 1; }
echo "PASS"

echo "=== 6. CJK AND 應排除不完整文件 ==="
output=$(printf "區塊鏈 金融 啤酒\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "沒有符合結果" || { echo "FAIL: AND 未排除不完整文件"; exit 1; }
echo "PASS"

echo "=== 7. OR 模式切換 ==="
output=$(printf ":or\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "OR>" || { echo "FAIL: OR 提示符未出現"; exit 1; }
echo "$output" | grep -q "切換為 OR 模式" || { echo "FAIL: 未顯示模式切換"; exit 1; }
echo "PASS"

echo "=== 8. OR 模式搜尋（任一詞匹配） ==="
output=$(printf ":or\n咖啡 太空梭\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "咖啡" || { echo "FAIL: OR 模式未找到咖啡"; exit 1; }
echo "PASS"

echo "=== 9. AND → OR 模式切換 ==="
output=$(printf ":or\n:and\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "切換為 AND 模式" || { echo "FAIL: 模式切換失效"; exit 1; }
echo "$output" | grep -q "AND>" || { echo "FAIL: AND 提示符未出現"; exit 1; }
echo "PASS"

echo "=== 10. 英文搜尋（ASCII） ==="
output=$(printf "Docker\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "容器化技術" || { echo "FAIL: 英文搜尋未找到結果"; exit 1; }
echo "PASS"

echo "=== 11. 不分大小寫 ==="
r1=$(printf "docker\n:quit\n" | cargo run 2>&1)
r2=$(printf "Docker\n:quit\n" | cargo run 2>&1)
c1=$(echo "$r1" | grep -c "\[")
c2=$(echo "$r2" | grep -c "\[")
[ "$c1" -eq "$c2" ] || { echo "FAIL: 大小寫結果不一致 ($c1 vs $c2)"; exit 1; }
echo "PASS"

echo "=== 12. 數字搜尋 ==="
output=$(printf "5G\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "5G 網路" || { echo "FAIL: 數字搜尋未找到"; exit 1; }
echo "PASS"

echo "=== 13. 混合 CJK + 英文搜尋 ==="
output=$(printf "CRISPR 基因\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "基因編輯技術" || { echo "FAIL: 混合搜尋未找到"; exit 1; }
echo "PASS"

echo "=== 14. 不存在的查詢 ==="
output=$(printf "zzzzzzzzzz\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "沒有符合結果" || { echo "FAIL: 不存在的查詢未回傳空"; exit 1; }
echo "PASS"

echo "=== 15. OR 模式多詞匹配 + 排序 ==="
output=$(printf ":or\n機器學習 深度學習 人工智慧\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "機器學習是人工智慧的重要分支" || { echo "FAIL: OR 多詞未找到最佳匹配"; exit 1; }
echo "PASS"

echo "=== 16. AND 模式多詞: 三個詞交集 ==="
output=$(printf "機器學習 人工智慧 深度學習\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "沒有符合結果" || { echo "FAIL: 三詞 AND 應無交集"; exit 1; }
echo "PASS"

echo "=== 17. 英文短語搜尋 ==="
output=$(printf "Fintech\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "金融科技正在顛覆傳統銀行業" || { echo "FAIL: Fintech 未找到"; exit 1; }
echo "PASS"

echo "=== 18. 長 CJK 字串搜尋（多個 bigram） ==="
output=$(printf "自然語言處理\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "自然語言處理技術讓機器能夠理解人類語言" || { echo "FAIL: 長 CJK 未找到"; exit 1; }
echo "PASS"

echo "=== 19. 邊界 case: 雙字元 CJK (bigram) ==="
output=$(printf "人工\n:quit\n" | cargo run 2>&1)
echo "$output" | grep -q "人工智慧" || { echo "FAIL: bigram 未找到"; exit 1; }
echo "PASS"

echo "=== 20. :quit 指令 ==="
echo ":q" | cargo run 2>&1 && echo "PASS" || { echo "FAIL: :q 退出失敗"; exit 1; }

echo ""
echo "=== 全部 20 項測試通過 ==="
