# lsm/bloom.rs — Bloom Filter

## 理論基礎

**Bloom Filter (布隆過濾器)** 是一種**機率性資料結構 (probabilistic data structure)**，用於判斷一個元素是否屬於某個集合。

### 特性

- **保證不存在** — 如果回傳 false，元素一定不在集合中
- **可能誤判存在** — 如果回傳 true，元素可能不在集合中 (false positive)
- **無法刪除** — 標準 Bloom Filter 不支援刪除操作
- **空間效率極高** — 使用位元陣列而非完整資料

### 運作原理

1. 插入元素時，使用 k 個雜湊函數計算 k 個位元位置，將其設為 1
2. 查詢元素時，檢查 k 個位元位置是否全部為 1
3. 若任一位元為 0 → 元素一定不存在
4. 若全部為 1 → 元素可能存在（有誤判率）

### 實作

```rust
fn hash(&self, key: &[u8], seed: usize) -> usize {
    let mut hasher = DefaultHasher::new();
    key.hash(&mut hasher);
    seed.hash(&mut hasher);  // 不同 seed 產生不同雜湊
    (hasher.finish() as usize) % self.capacity
}
```

使用 3 個雜湊函數 (`self.hashes = 3`)，在誤判率與計算開銷間取得平衡。

## 在 LSM 中的角色

在查詢時，先透過 Bloom Filter 判斷 SSTable 中是否可能包含該鍵。如果 Bloom Filter 回傳 false，則跳過該 SSTable，避免不必要的磁碟讀取。

## 相關資源

- `lsm/engine.rs` — Bloom Filter 在查詢流程中的使用
- `lsm/sstable.rs` — 被加速的目標
