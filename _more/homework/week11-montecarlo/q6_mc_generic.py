# q6：蒙地卡羅法做 n 變數積分 integral_mc(f, low, high)
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import random

def integral_mc(f, low, high, n_samples=500000):
    """蒙地卡羅法求 n 維積分，n = len(low) = len(high)"""
    n = len(low)
    volume = 1.0
    for i in range(n):
        volume *= high[i] - low[i]
    total = 0.0
    for _ in range(n_samples):
        x = [low[i] + random.random() * (high[i] - low[i]) for i in range(n)]
        total += f(x)
    return volume * total / n_samples

def test():
    f = lambda x: sum(xi * xi for xi in x)
    for n in [1, 2, 5, 100]:
        est = integral_mc(f, [0] * n, [1] * n)
        exact = n / 3
        print(f"{n:3d} 維 ∫(x₁²+...+x_{n}²) ≈ {est:.4f} （正解 {exact:.4f}）")
        assert abs(est - exact) < abs(exact) * 0.05
    print("所有測試通過！")

if __name__ == "__main__":
    test()
