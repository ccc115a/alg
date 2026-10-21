"""動態規劃解法：C(n, k) 組合數。

狀態定義
    dp[i][j] = C(i, j) = 從 i 個取出 j 個的組合數。

轉移方程（Pascal 公式）
    C(n, k) = C(n-1, k-1) + C(n-1, k)
    初值 C(i, 0) = C(i, i) = 1

空間可壓縮成一維（只用上一列更新當前列）：
    dp[j] = dp[j] + dp[j-1]，從 j = min(i, k) 倒著更新。

複雜度：時間 O(nk)、空間 O(k)（壓縮後）。
"""

from __future__ import annotations


def comb_2d(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = 1
        for j in range(1, min(i, k) + 1):
            dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
    return dp[n][k]


def comb_1d(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    dp = [0] * (k + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(min(i, k), 0, -1):
            dp[j] += dp[j - 1]
    return dp[k]


if __name__ == "__main__":
    for n, k in [(5, 2), (10, 3), (30, 15), (100, 50)]:
        print(f"C({n},{k}) = {comb_1d(n, k)}")
