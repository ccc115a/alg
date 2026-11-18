# q2：蒙地卡羅法算單變數積分
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import math
import random

def mc_integral_1d(f, a, b, n=100000):
    """蒙地卡羅法求 ∫_a^b f(x) dx"""
    s = sum(f(random.uniform(a, b)) for _ in range(n))
    return (b - a) * s / n

def test():
    f = lambda x: x * x
    print("∫₀¹ x² dx (n=1000)   ≈", mc_integral_1d(f, 0, 1, 1000), "（正解 1/3）")
    print("∫₀¹ x² dx (n=100000) ≈", mc_integral_1d(f, 0, 1, 100000), "（正解 1/3）")
    print("∫₀^π sin x dx ≈", mc_integral_1d(math.sin, 0, math.pi, 100000), "（正解 2）")
    est = mc_integral_1d(f, 0, 1, 100000)
    assert abs(est - 1 / 3) < 0.01
    print("所有測試通過！")

if __name__ == "__main__":
    test()
