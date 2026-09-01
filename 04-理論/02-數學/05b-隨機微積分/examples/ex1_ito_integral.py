"""
範例 1：伊藤積分
================
示範：∫₀ᵀ W(t) dW(t) = ½W(T)² - ½T

• 數值積分（左端點 Riemann-Ito）
• 與解析解比較
• Stratonovich 積分對比
• 期望值驗證（鞅性質）
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from stoc4py import ItoIntegral, ito_lemma_demo
from stoc4py.ito import quadratic_variation_demo
from stoc4py.plot import StochPlot
import matplotlib
import os; os.makedirs("./out", exist_ok=True)
matplotlib.use("Agg")

# ─── 1. 基礎 ∫ W dW 驗證 ─────────────────────────────────────────────────

print("=" * 60)
print("伊藤積分範例：∫₀ᵀ W(t) dW(t)")
print("=" * 60)

result = ito_lemma_demo(T=1.0, n_steps=50_000, n_paths=3, seed=2024)

t = result["t"]
W = result["W"]
ito_int = result["ito_integral"]
analytic = result["analytic"]

for i in range(W.shape[0]):
    final_ito = ito_int[i, -1]
    final_ana = analytic[i, -1]
    print(f"\n路徑 {i+1}:")
    print(f"  W(T)                   = {W[i, -1]:.6f}")
    print(f"  ∫ W dW  (數值)         = {final_ito:.6f}")
    print(f"  ½W²-½T  (解析)         = {final_ana:.6f}")
    print(f"  誤差                   = {abs(final_ito - final_ana):.6f}")

# ─── 2. 一般伊藤積分：∫ sin(W) dW ────────────────────────────────────────

print("\n" + "=" * 60)
print("∫₀¹ sin(W(t)) dW(t)  — Monte-Carlo 期望值驗證")
print("=" * 60)

ito_sin = ItoIntegral(integrand=lambda t, W: np.sin(W), seed=42)
mean_val, se = ito_sin.expected_value(T=1.0, n_steps=5000, n_paths=10000)
print(f"E[∫ sin(W) dW] = {mean_val:.6f}  ±{se:.6f}")
print(f"理論值 (鞅性質) = 0.000000")

# ─── 3. ∫ t dW（確定性被積函數）────────────────────────────────────────────

print("\n" + "=" * 60)
print("∫₀¹ t dW(t)  — Wiener 積分")
print("=" * 60)

ito_t = ItoIntegral(integrand=lambda t, W: t, seed=42)
mean_t, se_t = ito_t.expected_value(T=1.0, n_steps=5000, n_paths=10000)
print(f"E[∫ t dW]  = {mean_t:.6f}  ±{se_t:.6f}")
print(f"理論: E=0, Var=∫₀¹ t² dt = 1/3 ≈ {1/3:.6f}")

_, _, I_t = ito_t.compute(T=1.0, n_steps=5000, n_paths=5000)
var_t = float(np.var(I_t[:, -1]))
print(f"樣本方差 Var[∫ t dW]  = {var_t:.6f}")

# ─── 4. 二次變分驗證 ────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("二次變分驗證：[W, W]_T → T")
print("=" * 60)

qv_result = quadratic_variation_demo(T=1.0, n_steps=100_000)
qv_final = qv_result["quadratic_variation"][-1]
print(f"[W, W]_T (樣本) = {qv_final:.6f}")
print(f"理論值 T        = 1.000000")
print(f"一次變分（樣本）= {qv_result['first_variation'][-1]:.2f}  → ∞")

# ─── 5. 繪圖 ────────────────────────────────────────────────────────────────

print("\n繪製伊藤積分圖表...")
fig = StochPlot.ito_integral(result, filename="./out/ito_integral.png")
print("已儲存至 ./out/ito_integral.png")
print("\n✓ 伊藤積分範例完成")
