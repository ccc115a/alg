# boyer_moore_nondp.py — Boyer-Moore 精確單字搜尋

## 用途

在大字串中找 pattern 精確出現的所有位置。經典的「精確搜尋極致」演算法。

## 函式

| 函式 | 說明 |
|---|---|
| `boyer_moore(text, pattern)` | 回傳所有出現的起始位置 |
| `_build_suffix(pattern)` | 好後綴表 |
| `_is_border(pattern, i)` | `p[i:]` 是否為 pattern 的前綴 border |

## 原理

與直覺的「逐字元比對」不同，BM **從 pattern 右端往左比**，
失配時根據兩個啟發式計算跳量，取較大者：

### 1. 壞字元規則 (Bad Character)

失配字元 `x = text[s+j]`。若 `x` 在 pattern 中出現過，
下一比對起點至少可跳到「`x` 在 pattern 最右位置」對齊：

```
skip_bc = j - bad[x]     （bad[x] 未定義時 = -1，跳 j+1）
```

### 2. 好後綴規則 (Good Suffix)

已匹配的後綴 `p[j+1:]` 在 pattern 其他位置的出現：
- 若好後綴在別處出現 → 對齊該位置
- 若好後綴的後綴是 pattern 的前綴（border）→ 對齊開頭

```
skip_bs = good[j]
```

`good[i]` 由 suffix 表 + border 檢查預先算出。

### 最終跳量

```
s += max(1, skip_bc, skip_bs)
```

## 預處理

- `bad` 哈希表：O(m·σ) 或 O(m)
- `suffix` + `good` 表：O(m²)（最壞）或 O(m·σ)

## 複雜度

- 預處理 O(m²)、搜尋平均 **O(n/m)**、最壞 O(n·m)
- 平均比 naive O(nm) 快一個數量级以上（尤其 pattern 長、字母大時）

## 與 DP 的分工

BM 做的是**精確匹配**；若要容忍錯字（模糊定位），BM 無法處理，
必須用 edit distance DP（見 `dp_search.py`）。
兩者解決 word search 的不同變體。

## 已知限制

- 本實作的 good 表用簡化 border 判斷，對某些 pattern 非最緊跳量
  （仍正確，只是跳得保守）；工業級實現（如 Crochemore-Perrin）
  的 good 表更精緻
- CPython 的 `str.find` 用 C 實作的 Two-Way 演算法，純 Python BM
  在速度上打不贏它是常數問題，不是演算法問題
