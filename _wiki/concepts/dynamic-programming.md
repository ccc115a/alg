# 動態規劃 (Dynamic Programming)

核心是「記憶化」（Memoization）：把子問題的答案存起來，避免重複計算。由馮紐曼框架化，貝爾曼命名（貝爾曼還故意取了個好聽的名字以取悅國防部贊助人）。

## 核心特性

- **最優子結構**：全局最優解可由子問題的最優解組合而成。
- **重疊子問題**：同一子問題會被反覆遇到，因此值得記憶化。
- **狀態轉移**：用轉移方程式描述狀態之間的遞迴關係。
- 通常以表格（bottom-up）或遞迴加記憶（top-down）實作。

## 經典演算法

- [Floyd-Warshall](../algorithms/floyd-warshall.md) — 全點對最短路徑
- [Levenshtein](../algorithms/levenshtein.md) — 字串編輯距離
- [Bellman-Ford](../algorithms/bellman-ford.md) — 可處理負權邊的最短路徑

## 相關概念

- [分治法](divide-and-conquer.md) — 兩者都拆解子問題，差別在於子問題是否重疊
- [貪婪演算法](greedy.md) — 貪婪是 DP 的特例：每步只挑最優而不回頭