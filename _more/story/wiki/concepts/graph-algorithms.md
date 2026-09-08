# 圖論演算法

處理由節點與邊組成的結構。圖是許多真實系統的抽象模型——道路、網路、社交關係都可視為圖，因此圖論的經典問題無處不在。

## 核心特性

- **最短路徑**：找出兩節點間代價最小的路徑。
- **最小生成樹**：以最少總權重連接所有節點。
- **連通性**：判斷圖中節點之間是否可達。
- **拓撲排序**：將有向無環圖排成線性順序。

## 經典演算法

- [Dijkstra](../algorithms/dijkstra.md) — 單源最短路徑（非負權）
- [Bellman-Ford](../algorithms/bellman-ford.md) — 可處理負權邊的最短路徑
- [Floyd-Warshall](../algorithms/floyd-warshall.md) — 全點對最短路徑
- [A*](../algorithms/a-star.md) — 加入啟發式加速的最短路徑
- [MST](../algorithms/mst.md) — 最小生成樹
- [拓撲排序](../algorithms/topological-sort.md) — 依賴關係的線性化解

## 相關概念

- [貪婪演算法](greedy.md) — Dijkstra、MST 都是貪心思想
- [動態規劃](dynamic-programming.md) — Bellman-Ford、Floyd-Warshall 都是 DP
- [網路協定](networking.md) — 網際網路底層的演算法多為圖論