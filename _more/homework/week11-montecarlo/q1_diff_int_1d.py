# q1：單變數數值微分與積分
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import math

def diff(f, x, h=1e-5):
    """中央差分求 f'(x)"""
    return (f(x + h) - f(x - h)) / (2 * h)

def integral_midpoint(f, a, b, n=10000):
    """中點黎曼和求 ∫_a^b f(x) dx"""
    h = (b - a) / n
    return h * sum(f(a + (i + 0.5) * h) for i in range(n))

def integral_simpson(f, a, b, n=1000):
    """辛普森法求 ∫_a^b f(x) dx（n 必須為偶數）"""
    if n % 2 == 1:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 == 1 else 2)
    return s * h / 3

def test():
    f = lambda x: x * x
    print("f(x)=x^2, f'(2) =", diff(f, 2), "（正解 4）")
    print("∫₀¹ x² dx (midpoint) =", integral_midpoint(f, 0, 1), "（正解 1/3）")
    print("∫₀¹ x² dx (simpson)  =", integral_simpson(f, 0, 1), "（正解 1/3）")
    print("∫₀^π sin x dx =", integral_simpson(math.sin, 0, math.pi), "（正解 2）")
    assert abs(diff(f, 2) - 4) < 1e-6
    assert abs(integral_simpson(f, 0, 1) - 1 / 3) < 1e-9
    assert abs(integral_simpson(math.sin, 0, math.pi) - 2) < 1e-9
    print("所有測試通過！")

if __name__ == "__main__":
    test()
