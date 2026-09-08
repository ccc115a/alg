# 排序與搜尋

排序是計算機科學中最基本的問題之一，也是最多故事的領域。從霍爾在莫斯科的靈感到全世界工程師被一個加號卡關 60 年，這些故事展示了「簡單」演算法背後的深邃智慧。

---

## 核心概念

- **比較排序下限**：任何基於比較的排序演算法，最壞情況至少需要 O(N log N)
- **非比較排序**：如 [radix-sort](../algorithms/radix-sort.md)，可以突破 O(N log N) 的限制
- **分治法**：[quick-sort](../algorithms/quick-sort.md) 是 [分治法](../concepts/divide-and-conquer.md) 的經典應用
- **隨機化**：隨機快速排序是 [Las Vegas 演算法](../concepts/randomization.md) 的代表

---

## 故事

| 演算法 | 年代 | 故事亮點 |
|--------|------|---------|
| [二元搜尋 Bug](../algorithms/binary-search-bug.md) | 1946–2006 | 一個加號讓全世界工程師卡關 60 年 |
| [快速排序](../algorithms/quick-sort.md) | 1960 | 莫斯科留學、翻譯字典、分治法 |
| [Fisher-Yates 洗牌](../algorithms/fisher-yates.md) | 1938/1964 | 保證絕對公平的洗牌 |
| [基數排序](../algorithms/radix-sort.md) | 1950s | 美國人口普查催生 |

---

## 相關概念

- [分治法](../concepts/divide-and-conquer.md)
- [隨機化](../concepts/randomization.md)
- [資料結構](../concepts/data-structures.md)
