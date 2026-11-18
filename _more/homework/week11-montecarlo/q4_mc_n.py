# q4：蒙地卡羅法算 n 變數積分（超體積）
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import random

def mc_integral_n(f, low, high, n_samples=200000):
    """蒙地卡羅法求 n 維積分：在超方體 [low, high] 內均勻取樣"""
    n = len(low)
    volume = 1.0
    for i in range(n):
        volume *= high[i] - low[i]
    s = 0.0
    for _ in range(n_samples):
        x = [random.uniform(low[i], high[i]) for i in range(n)]
        s += f(x)
    return volume * s / n_samples

def test():
    f = lambda x: sum(xi * xi for xi in x)
    v2 = mc_integral_n(f, [0, 0], [1, 1])
    print("2 維 ∫ (x₁²+x₂²) ≈", round(v2, 4), "（正解 2/3）")
    assert abs(v2 - 2 / 3) < 0.02
    v5 = mc_integral_n(f, [0] * 5, [1] * 5)
    print("5 維 ∫ (x₁²+...+x₅²) ≈", round(v5, 4), "（正解 5/3）")
    assert abs(v5 - 5 / 3) < 0.05
    print("所有測試通過！")

if __name__ == "__main__":
    test()
