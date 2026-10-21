"""非動態規劃解法：C(n, k) 純遞迴（無記憶化）。

原理
    直接用定義式的遞迴分解：
        C(n, k) = C(n-1, k-1) + C(n-1, k)
    或組合定義 C(n, k) = n! / (k!(n-k)!)（以遞迴求階乘）。

    未加 memo 的遞迴會重複計算大量相同的子問題
    （C(5,2) 同時需要 C(4,1)、C(4,2)，而它們又各自展開……），
    樹狀展開節點數是 O(2^n) 級。

複雜度：時間 O(2^n)、空間 O(n)（遞迴深度）。
這正是「需要動態規劃」的教科書例子：重疊子問題 + 最優子結構。
"""

from __future__ import annotations

import math


def comb_recursive(n: int, k: int) -> int:
    """純遞迴，直接反映 Pascal 公式。"""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    return comb_recursive(n - 1, k - 1) + comb_recursive(n - 1, k)


def comb_factorial(n: int, k: int) -> int:
    """用階乘公式（遞迴求階乘，這裡用 math 以免重複實作）。"""
    if k < 0 or k > n:
        return 0
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))


if __name__ == "__main__":
    for n, k in [(5, 2), (10, 3), (20, 10)]:
        print(f"C({n},{k}) = {comb_recursive(n, k)}")
