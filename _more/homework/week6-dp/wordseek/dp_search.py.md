# dp_search.py — Edit Distance DP 模糊搜尋

## 用途

以編輯距離 DP 在字典中找與 query「最像」的單字（模糊搜尋/拼寫檢查）。

## 函式

| 函式 | 說明 |
|---|---|
| `edit_distance(a, b)` | 兩字串的編輯距離（Levenshtein） |
| `fuzzy_search(query, dictionary, max_dist=2)` | 回傳 `(距離, 單字)` 列表，距離遞增 |

## 原理

編輯距離 = 把 A 變成 B 所需的最少「插入/刪除/取代」次數。
距離越小越相似；`fuzzy_search` 對字典中每個候選算一次，取最小。

## 狀態定義

```
dp[i][j] = a 的前 i 字元 變成 b 的前 j 字元 的最少操作數
```

## 轉移方程

```
dp[i][j] = dp[i-1][j-1]                          若 a[i-1]==b[j-1]（免費用）
         = 1 + min( dp[i-1][j],                  刪除 a[i-1]
                    dp[i][j-1],                  插入 b[j-1]
                    dp[i-1][j-1] )               取代
```

## 初值

```
dp[i][0] = i   # 全刪除
dp[0][j] = j   # 全插入
```

## 長度剪枝

`abs(len(word) - len(query)) > max_dist` → 直接跳過，
避免對明顯不可能的候選做 O(nm) 計算。

## 複雜度

- 每候選 **O(|q|·|c|)**、全部 **O(Σ|c|·|q|)**
- 可再用 n-gram 倒排索引先粗篩再精算

## 特性

- 保證找到編輯距離最小的候選（全域最優）
- 只能做模糊匹配；「精確」搜尋用 Boyer-Moore 快得多（見 `boyer_moore_nondp.py`）
- DNA 的近似比對（blast 題的 Smith-Waterman）可視為編輯距離的加權推广
