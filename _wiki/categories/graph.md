# 圖論與最短路徑

圖論演算法是計算機科學中最具故事性的領域。從咖啡館裡的靈感到父子檔的合作，從「教學生的小練習」到擊敗世界棋王，這些故事展示了點與線之間的無限可能。

---

## 核心概念

- **最短路徑**：[dijkstra](../algorithms/dijkstra.md)（非負權重）、[bellman-ford](../algorithms/bellman-ford.md)（支援負權重）、[floyd-warshall](../algorithms/floyd-warshall.md)（全對）
- **最小生成樹**：[mst](../algorithms/mst.md) — 貪婪策略的勝利
- **拓撲排序**：[topological-sort](../algorithms/topological-sort.md) — 依賴關係的排程
- **啟發式搜尋**：[a-star](../algorithms/a-star.md) — 結合 Dijkstra 與預估距離

---

## 故事

| 演算法 | 年代 | 故事亮點 |
|--------|------|---------|
| [Dijkstra](../algorithms/dijkstra.md) | 1956 | 咖啡館 20 分鐘、論文被拒、Google Maps |
| [Bellman-Ford](../algorithms/bellman-ford.md) | 1955–1958 | 父子檔、負權重邊、命名後悔 |
| [Floyd-Warshall](../algorithms/floyd-warshall.md) | 1962 | 「小練習」變成經典 |
| [A*](../algorithms/a-star.md) | 1968 | 機票存根背面的公式 |
| [MST](../algorithms/mst.md) | 1950s | 貪心策略 100% 最優 |
| [拓撲排序](../algorithms/topological-sort.md) | 1960s | npm、make 的隱形英雄 |

---

## 相關概念

- [貪婪演算法](../concepts/greedy.md)
- [動態規劃](../concepts/dynamic-programming.md)
- [網路協定](../concepts/networking.md)（路由使用圖論）
