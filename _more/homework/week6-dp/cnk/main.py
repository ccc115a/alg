"""驗證 C(n,k) 的 DP 與遞迴結果一致，並計時比較重複子問題的代價。"""

import timeit

from dp_comb import comb_1d, comb_2d
from recurse_comb_nondp import comb_factorial, comb_recursive

CASES = [(5, 2), (10, 3), (20, 10), (30, 15), (50, 25), (100, 50), (200, 100)]


def check() -> None:
    from math import comb

    for n, k in CASES:
        gt = comb(n, k)
        assert comb_1d(n, k) == gt, f"1d DP 錯誤: C({n},{k})"
        assert comb_2d(n, k) == gt, f"2d DP 錯誤: C({n},{k})"
        if n <= 25:
            assert comb_recursive(n, k) == gt, f"遞迴錯誤: C({n},{k})"
        assert comb_factorial(n, k) == gt, f"階乘錯誤: C({n},{k})"
    print("正確性: 全部與 math.comb 一致")


if __name__ == "__main__":
    check()

    print("\n計時:")
    n, k = 500, 250
    t_1d = timeit.timeit(lambda: comb_1d(n, k), number=100) / 100
    t_2d = timeit.timeit(lambda: comb_2d(n, k), number=100) / 100
    t_fact = timeit.timeit(lambda: comb_factorial(n, k), number=100) / 100
    print(f"  DP 1D (O(nk) 時間/O(k) 空間) : {t_1d*1e6:10.1f} us")
    print(f"  DP 2D (O(nk) 時間/O(nk) 空間): {t_2d*1e6:10.1f} us")
    print(f"  階乘公式 (O(n) 用 math)      : {t_fact*1e6:10.1f} us")

    print("\n純遞迴 vs DP (小 n 示範重複子問題):")
    for nn in (10, 15, 20, 25, 28):
        t_rec = timeit.timeit(lambda: comb_recursive(nn, nn // 2), number=3) / 3
        t_dp = timeit.timeit(lambda: comb_1d(nn, nn // 2), number=1000) / 1000
        print(f"  n={nn:3} k={nn//2:3}  遞迴={t_rec*1000:10.3f} ms  DP={t_dp*1e6:8.2f} us")
