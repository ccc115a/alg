# Skip List（跳表）

## 概述

跳表（Skip List）是一種機率資料結構，由 William Pugh 在 1990 年的論文《Skip Lists: A Probabilistic Alternative to Balanced Trees》中提出。跳表使用多層有序鏈結串列，實現了平均 O(log n) 的查詢、插入、刪除複雜度，同時比平衡樹更容易實作和並行化。

跳表的核心思想是：**用空間換時間，建立多層索引加速搜尋**。

## 結構

跳表的基本結構如下：

```
Level 3:  [HEAD] ──────────────────────────────▶ [NIL]
Level 2:  [HEAD] ────────────▶ [30] ─────────▶ [NIL]
Level 1:  [HEAD] ──▶ [10] ──▶ [30] ──▶ [40] ▶ [NIL]
Level 0:  [HEAD] ──▶ [10] ──▶ [20] ──▶ [30] ▶ [40] ──▶ [NIL]
```

- **Level 0**：最底層，包含所有元素的完整有序鏈結串列
- **Level 1, 2, 3**：稀疏索引，每層只包含部分元素
- **HEAD**：頭節點，指向各層的起始
- **NIL**：尾節點，標識鏈表結束

## 搜尋

在跳表中搜尋元素 30：

```
Level 2:  [HEAD] ────────────▶ [30] ─────────▶ [NIL]
                ↑           找到！
Level 1:  [HEAD] ──▶ [10] ──▶ [30] ──▶ [40] ▶ [NIL]
                ↑           找到！
Level 0:  [HEAD] ──▶ [10] ──▶ [20] ──▶ [30] ▶ [40] ──▶ [NIL]
                          ↑   ↑   ↑
                       遍歷 遍歷 找到
```

搜尋過程：
1. 從最高層（Level 2）開始
2. 在當前層向前移動，直到下一個節點的值 > 目標值
3. 下降到下一層
4. 重複直到 Level 0

## 插入

插入元素 25：

1. **決定層數**：使用隨機擲硬幣法（p=0.5），決定新節點的層數
   - 擲出正面，層數 +1
   - 擲出反面或達到最大層數，停止
   - 例如：擲出 3 次正面，層數為 3

2. **創建節點**：建立包含目標值的新節點

3. **更新指標**：在各層中更新指標，插入新節點

```
插入前：
Level 1:  [10] ──▶ [30]
                 ▲
插入後：     [25] ─┘
Level 1:  [10] ──▶ [25] ──▶ [30]
```

## 刪除

刪除元素 25：

1. **搜尋**：找到所有層中包含該元素的節點
2. **更新指標**：在各層中移除該節點，更新前後指標
3. **釋放記憶體**：回收節點記憶體

## 層數決定

跳表使用隨機化決定層數：

```rust
fn random_level(max_level: usize, p: f64) -> usize {
    let mut level = 1;
    let mut rng = rand::thread_rng();
    
    while level < max_level && rng.gen_bool(p) {
        level += 1;
    }
    
    level
}
```

- `p`：每層繼續向上的概率（通常為 0.5）
- `max_level`：最大層數（通常為 log(n)）

對於 n=1,000,000 個元素：
- `max_level` ≈ 20
- 期望層數 ≈ 2

## 複雜度分析

| 操作 | 平均複雜度 | 最壞複雜度 |
|------|------------|------------|
| 搜尋 | O(log n) | O(n) |
| 插入 | O(log n) | O(n) |
| 刪除 | O(log n) | O(n) |
| 空間 | O(n log n) | O(n log n) |

最壞情況發生在隨機層數選擇不幸，導致退化成普通鏈結串列。

## 與平衡樹的比較

| 特性 | Skip List | 平衡樹（如紅黑樹、AVL） |
|------|-----------|-------------------------|
| 實作難度 | 簡單 | 複雜（需要旋轉操作） |
| 並行化 | 容易（指標操作天然隔離） | 困難（需要鎖或復雜的並行演算法） |
| 記憶體 | 稍高（多層指標） | 較低 |
| 搜尋複雜度 | O(log n)（機率保證） | O(log n)（確定性） |
| 刪除/插入 | 局部修改 | 可能需要重新平衡 |

## Redis 的 ZSet

Redis 的有序集合（Sorted Set）使用跳表作為底層實現：

```python
# Redis ZADD
ZADD leaderboard 100 "Tom"
ZADD leaderboard 90 "Alice"

# Redis ZRANGE（按分數範圍查詢）
ZRANGE leaderboard 0 -1 REV
# ["Tom", "Alice"]
```

Redis 同時使用跳表和字典（Hash）來實現 ZSet：
- 字典：O(1) 的成員查詢
- 跳表：O(log n) 的範圍查詢和排名

## LevelDB 的 MemTable

LevelDB 和 RocksDB 的 MemTable（記憶體表）使用跳表作為主要實現：

```rust
pub struct MemTable {
    // 跳表作為內部結構
    table: SkipList<Vec<u8>, Vec<u8>>,
}
```

為什麼 LevelDB 選擇跳表而非 B-Tree？
1. **實作簡單**：跳表比 B-Tree 容易實作
2. **併發友好**：跳表易於實現無鎖並行版本（Lock-free）
3. **記憶體局部性**：跳表的節點指標更少，CPU 快取友好

## 在 db6 中的應用

db6 的 LSM 引擎使用跳表作為 MemTable 的實現：

```rust
pub struct LsmEngine {
    // 跳表實現的 MemTable
    memtable: SkipList<Vec<u8>, Vec<u8>>,
    // WAL、 SSTable 等其他元件...
}
```

跳表在 LSM 中的角色：
- **寫入緩衝**：新寫入的資料首先進入 MemTable
- **有序記憶體結構**：跳表保持鍵的有序，支持範圍掃描
- **WAL 的夥伴**：配合 Write-Ahead Log 提供 crash recovery

## 延伸閱讀

- Pugh, W. (1990). Skip Lists: A Probabilistic Alternative to Balanced Trees. Communications of the ACM.
- Redis Internals: https://github.com/redis/redis