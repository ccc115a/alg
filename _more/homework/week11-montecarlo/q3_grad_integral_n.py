# q3：n 變數數值微分（梯度）與數值積分（超體積）
# AI 聲明：本程式由 AI（opencode + GLM）協助產生，經人工檢視修改。

import itertools

def gradient(f, x, h=1e-6):
    """中央差分求 n 變數函數在 x 點的梯度"""
    n = len(x)
    g = []
    for i in range(n):
        xp = list(x); xp[i] += h
        xm = list(x); xm[i] -= h
        g.append((f(xp) - f(xm)) / (2 * h))
    return g

def integral_grid(f, low, high, k=50):
    """n 維中點黎曼和：每維切 k 段，共 k^n 個格子"""
    n = len(low)
    widths = [high[i] - low[i] for i in range(n)]
    dv = 1.0
    for w in widths:
        dv *= w / k
    total = 0.0
    for cell in itertools.product(range(k), repeat=n):
        mid = [low[i] + (cell[i] + 0.5) * widths[i] / k for i in range(n)]
        total += f(mid)
    return total * dv

def test():
    f = lambda x: sum(xi * xi for xi in x)
    g = gradient(f, [1, 2, 3])
    print("∇(x₁²+x₂²+x₃²) 在 (1,2,3) =", [round(v, 6) for v in g], "（正解 [2,4,6]）")
    assert abs(g[0] - 2) < 1e-4 and abs(g[1] - 4) < 1e-4 and abs(g[2] - 6) < 1e-4
    v2 = integral_grid(f, [0, 0], [1, 1], k=200)
    print("∫_[0,1]² (x₁²+x₂²) dA ≈", round(v2, 4), "（正解 2/3）")
    assert abs(v2 - 2 / 3) < 1e-3
    v3 = integral_grid(f, [0, 0, 0], [1, 1, 1], k=100)
    print("∫_[0,1]³ (x₁²+x₂²+x₃²) dV ≈", round(v3, 4), "（正解 1）")
    assert abs(v3 - 1) < 1e-2
    print("所有測試通過！")

if __name__ == "__main__":
    test()
