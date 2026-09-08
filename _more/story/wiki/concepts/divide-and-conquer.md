# 分治法 (Divide and Conquer)

將大問題分解為小問題，遞迴求解後合併結果。三大步驟：**Divide**（分割）、**Conquer**（求解）、**Combine**（合併）。許多經典演算法的時間複雜度因此達到 O(N log N) 或更好。

## 核心特性

- **分解**：將問題切成數個規模更小的子問題，彼此獨立。
- **遞迴**：對每個子問題套用相同解法，直到規模小到可直接求解。
- **合併**：將子問題的解組合成原始問題的解。
- 複雜度通常可用主定理（Master Theorem）分析，常見形式為 O(N log N)。

## 經典演算法

- [快速排序](../algorithms/quick-sort.md) — 經典 O(N log N) 排序
- [FFT](../algorithms/fft.md) — 將多項式乘法分解為奇偶兩半
- [Graham Scan](../algorithms/graham-scan.md) — 依極角排序再掃描求凸包

## 相關概念

- [動態規劃](dynamic-programming.md) — 差異在於子問題是否重疊（DP 的子問題重疊，分治則獨立）
- [貪婪演算法](greedy.md) — 貪婪不回頭，分治則窮盡子問題