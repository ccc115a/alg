# Swisstable

Swisstable 是一個基於 **Swiss Table** 雜湊演算法的 Rust 實作專案。

## Swiss Table 演算法

Swiss Table 是由 Google 開發的高效能雜湊表演算法，主要特點包括：

- **快取友好**：使用連續記憶體區塊儲存雜湊槽位，減少快取 miss
- **SIMD 加速**：可利用 SIMD 指令集平行比較多個雜湊槽位
- **低負載因子**：透過 6-bit 彈性位元組（flexible byte）存儲金鑰群組（group）的中繼資料
- **開放定址**：所有元素儲存於單一陣列中

## 與 Rust hashbrown 的關係

本專案參考 Rust 語言的 [hashbrown](https://github.com/rust-lang/hashbrown) 函式庫實作，該庫同樣採用 Swiss Table 演算法。

## 主要模組

- `SwisstableMap<K, V>`：基於 Swiss Table 的鍵值對映射結構
- `SwisstableSet<T>`：基於 Swiss Table 的集合結構

## 效能特性

| 特性 | 說明 |
|------|------|
| 時間複雜度 | 平均 O(1) 查詢、插入、刪除 |
| 空間利用率 | 負載因子約 87.5% |
| 迭代順序 | 不保證特定順序 |
| 執行緒安全 | 需外部同步機制 |

## 用途

- 作為資料庫索引結構（參考 sql4 專案）
- 高效能鍵值儲存
- 取代標準 HashMap/HashSet