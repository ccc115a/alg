# 資料結構

演算法的基礎容器。選擇正確的資料結構往往決定效率——同樣的問題，用錯容器可能從 O(1) 退化到 O(N)。

## 核心特性

- **存取模式**：依需求選擇循序、隨機、或依鍵值存取。
- **平衡搜尋樹**：以樹的結構維持 O(log N) 的搜尋、插入、刪除。
- **機率型結構**：以小的錯誤率或隨機性換取空間與常數時間。
- **基礎結構**：動態陣列、連結串列等幾乎是所有複雜結構的起點。

## 經典演算法

- [B-Tree](../algorithms/b-tree.md) — 磁碟與資料庫的平衡樹
- [紅黑樹](../algorithms/red-black-tree.md) — 近似平衡，Linux 核心的自選
- [跳過表](../algorithms/skip-list.md) — 用機率逼近平衡樹
- [Bloom Filter](../algorithms/bloom-filter.md) — 寧可錯殺不可放過的濾波器
- [連結串列](../algorithms/linked-list.md) — 一行程式碼改變世界

## 相關概念

- [隨機化](randomization.md) — 跳過表、Bloom Filter 都倚賴機率與隨機性