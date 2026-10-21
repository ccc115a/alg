# dp_match.py — 動態規劃 regex 比對

## 用途

以 DP 判斷字串 `s` 是否完全匹配 pattern `p`（支援 `.` 與 `*`）。

## 函式

| 函式 | 說明 |
|---|---|
| `is_match(s, p)` | `s` 是否完全匹配 `p`（fullmatch） |
| `find_matches(text, pattern)` | 回傳所有「有前綴完全匹配 pattern」的起始位置 |
| `_match_prefix(s, start, p)` | 前綴匹配輔助（掃到任一 `dp[i][m]==True` 即可） |

支援語法：字元、`.`（任意字元）、`*`（前驅 atom 零次或多次）。

## 狀態定義

```
dp[i][j] = s 的前 i 個字元 是否 完全匹配 p 的前 j 個 pattern
```

## 轉移方程

**情形 1：`p[j-1]` 是普通字元或 `.`**

```
dp[i][j] = dp[i-1][j-1] and (p[j-1]=='.' or p[j-1]==s[i-1])
```

**情形 2：`p[j-1] == '*'`**，令前驅 token = `p[j-2]`（`*` 前必有 atom）

```
dp[i][j] = dp[i][j-2]                          # 零次：直接跳過 token*
         or (token 匹配 s[i-1] and dp[i-1][j]) # ≥1 次：吃一個字元，`*` 留著
```

「吃一個字元後 `*` 留著」是關鍵——讓 `a*` 能延伸任意長度。

## 初值

```
dp[0][0] = True
dp[0][j] = dp[0][j-2]  若 p[j-1]=='*'   # 空字串匹配 "a*b*c*" 型 pattern
dp[i][0] = False (i>0)
```

## 複雜度

- 時間 **O(nm)**、空間 **O(nm)**（可用 rolling array 壓成 O(m)）

## 特性

- 程式題經典（LeetCode #10）
- 不支援 `|` 與 `()`（那需要 NFA 或更複雜的分段 DP）
- 任何 DP 都可改寫成等價的自動機——見 `nfa_nondp.py`
