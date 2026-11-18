# q5：黎曼積分法做 n 變數積分 integral(f, low, high)
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import itertools
import random

CELL_CAP = 1_000_000

def integral(f, low, high):
    """黎曼積分法求 n 維積分，n = len(low) = len(high)。
    每維切 k 段（k^n 不超過 CELL_CAP）；當 k=1 時退化為隨機取樣。"""
    n = len(low)
    k = max(1, int(round(CELL_CAP ** (1.0 / n))))
    widths = [high[i] - low[i] for i in range(n)]
    volume = 1.0
    for w in widths:
        volume *= w

    if k == 1:
        samples = 200000
        total = 0.0
        for _ in range(samples):
            x = [low[i] + random.random() * widths[i] for i in range(n)]
            total += f(x)
        return volume * total / samples

    dv = volume / (k ** n)
    total = 0.0
    for cell in itertools.product(range(k), repeat=n):
        mid = [low[i] + (cell[i] + 0.5) * widths[i] / k for i in range(n)]
        total += f(mid)
    return total * dv

def test():
    f = lambda x: sum(xi * xi for xi in x)
    for n in [1, 2, 5, 100]:
        est = integral(f, [0] * n, [1] * n)
        exact = n / 3
        print(f"{n:3d} 維 ∫(x₁²+...+x_{n}²) ≈ {est:.4f} （正解 {exact:.4f}）")
        assert abs(est - exact) < abs(exact) * 0.05
    print("所有測試通過！")

if __name__ == "__main__":
    test()
