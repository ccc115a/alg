# 2. blast — DNA 相似字串搜尋

## 問題

給定一條 query DNA 與一個大型序列資料庫，找出與 query 最相似的區段
（本地比對 / local alignment）。

## 解法一：Smith-Waterman 動態規劃（`smith_waterman_dp.py`）

### 原理

本地比對的精確最優解。允許比對從任意位置開始、任意位置結束，
中途可插入 gap，取全表最高分為答案。

### 狀態與轉移

- `H[i][j]` = 以 `a[i-1]`、`b[j-1]` 結尾的最佳本地比對分數
- `H[i][j] = max(0, H[i-1][j-1]+s(a[i-1],b[j-1]), H[i-1][j]+gap, H[i][j-1]+gap)`
- 從最大值格子回溯得區間；`0` 為「重新開始」，是本地比對的關鍵

### 複雜度

- 時間 **O(nm)**、空間 **O(nm)**
- 兩條 10kb 序列需 10^8 格，人眼可接受；全資料庫掃描（n×總長）不可行

## 解法二：BLAST seed-and-expand（非 DP，`seed_expand_nondp.py`）

### 原理

NCBI BLAST（1990）的啟發式三步：

1. **Seed**：把 query 的每個 k-mer 建 hash，找資料庫中的相同短片段（word hit）
2. **Extend**：從 hit 往兩側延伸，只要累計分數仍上升就繼續（X-drop 中止）
3. **評分**：對每個 HSP（high-scoring segment pair）打分、排序輸出

### 複雜度

- 索引 O(m)，搜尋 ~O(n + m + hits·L)，實務上比 O(nm) 快數個數量級

## 比較

| | Smith-Waterman (DP) | BLAST seed-expand |
|---|---|---|
| 正確性 | **保證最優**本地比對 | 啟發式，通常接近最優，不保證 |
| 時間 | O(nm) | 近線性，實務快 100~10000x |
| 應用 | 小序列、精確需求 | 全基因組資料庫搜尋（事實標準） |

**結論**：DP 給出數學上最優解但無法擴展到海量資料；
BLAST 用「種子必然在最佳比對中出現」的機率性質換速度，
是「精確演算法 vs 啟發式」的經典取捨。此專題中我們實作簡化版 X-drop，
真實 BLAST 還有 substitution matrix（BLOSUM）、低複雜度區過濾等。

## 執行

```bash
python3 main.py
```
