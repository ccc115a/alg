# seed_expand_nondp.py — BLAST seed-and-expand

## 用途

以啟發式快速找出 query 與大型序列庫間的相似區段（HSP），
是 NCBI BLAST 核心流程的簡化版。

## 函式

| 函式 | 說明 |
|---|---|
| `blast_search(query, db, k=3, match=2, mismatch=-1, xdrop=2)` | 回傳 HSP 列表 `(q_start,q_end,db_start,db_end,score)` 依分數遞減 |
| `_extend_right(...)` / `_extend_left(...)` | 從 seed 往單側 X-drop 延伸 |

## 原理（三步流程）

1. **Seed（找種子）**
   把 db 的每個 k-mer 放進 hash table；掃過 query 的每個 k-mer 查表，
   得到所有「word hit」。
   依據：最佳本地比對中通常包含一個完全相同的短片段（高機率成立）。

2. **Extend（延伸）**
   從每個 hit 往左右延伸，累計分數（match 加、mismatch 減）。
   當前分數比目前最佳低超過 `xdrop` 就停止（X-drop 中止規則）。

3. **評分**
   對每個 HSP 記錄區間與總分，排序輸出。

## X-drop 延伸細節

```
cur += match（相同）或 mismatch（不同）
best = max(best, cur)
若 best - cur > xdrop → 停止
```

這是「貪心延伸 + 早停」，不保證延伸到全域最優結束點。

## 複雜度

- 建索引 O(m)、搜尋 O(n + m + hits·L)
- 實務上比 O(nm) 的 Smith-Waterman 快數十～數千倍

## 特性

- **不保證最優**：若最佳比對中沒有任何完全相同的 k-mer（高度突變），
  會漏掉；這是啟發式演算法的本質代價
- 分數通常與 Smith-Waterman 相同或非常接近（見 `main.py` 實測比值）
- 真實 BLAST 還有 BLOSUM 替換矩陣、低複雜度區 mask 等機制
