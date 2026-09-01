"""
範例 3：Black-Scholes 模型
============================
英國期權（歐式 European）vs 美國期權（美式 American）

• 歐式 Put/Call 解析定價（BS 公式）
• Greeks（Delta, Gamma, Theta, Vega, Rho）
• Put-Call Parity 驗證
• 美式期權 LSM 定價
• 提前執行溢價計算
• 隱含波動率
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib
import os; os.makedirs("./out", exist_ok=True)
matplotlib.use("Agg")

from math4py.stochastic import BlackScholes, AmericanOption
from math4py.plot import StochPlot

# ─── 參數設定 ────────────────────────────────────────────────────────────────

S0    = 100.0   # 現貨價格
K     = 100.0   # 履約價（平值）
T     = 1.0     # 到期 1 年
r     = 0.05    # 無風險利率 5%
sigma = 0.20    # 波動率 20%

print("=" * 65)
print("Black-Scholes 模型參數")
print("=" * 65)
print(f"  S₀ = {S0},  K = {K},  T = {T}年,  r = {r:.0%},  σ = {sigma:.0%}")

# ─── 1. 歐式期權（英國期權）解析定價 ─────────────────────────────────────────

print("\n" + "=" * 65)
print("【英國期權 / 歐式期權】Black-Scholes 解析解")
print("=" * 65)

bs = BlackScholes(S=S0, K=K, T=T, r=r, sigma=sigma)

call_res = bs.price("call")
put_res  = bs.price("put")

print("\n  歐式 Call:")
print(f"    d₁ = {call_res.d1:.6f}")
print(f"    d₂ = {call_res.d2:.6f}")
print(f"    價格  = {call_res.price:.6f}")
print(f"    Delta = {call_res.delta:.6f}")
print(f"    Gamma = {call_res.gamma:.6f}")
print(f"    Theta = {call_res.theta:.6f}（每日）")
print(f"    Vega  = {call_res.vega:.6f}（每1%波動）")
print(f"    Rho   = {call_res.rho:.6f}（每1%利率）")

print("\n  歐式 Put:")
print(f"    d₁ = {put_res.d1:.6f}")
print(f"    d₂ = {put_res.d2:.6f}")
print(f"    價格  = {put_res.price:.6f}")
print(f"    Delta = {put_res.delta:.6f}")
print(f"    Gamma = {put_res.gamma:.6f}")
print(f"    Theta = {put_res.theta:.6f}（每日）")
print(f"    Vega  = {put_res.vega:.6f}（每1%波動）")
print(f"    Rho   = {put_res.rho:.6f}（每1%利率）")

# ─── 2. Put-Call Parity 驗證 ─────────────────────────────────────────────────

print("\n" + "=" * 65)
print("Put-Call Parity 驗證（歐式）")
print("  C - P = S·e^{-qT} - K·e^{-rT}")
print("=" * 65)

parity = bs.parity_check()
print(f"  Call                  = {parity['call']:.8f}")
print(f"  Put                   = {parity['put']:.8f}")
print(f"  C - P                 = {parity['C-P']:.8f}")
print(f"  S·e⁻ᵠᵀ - K·e⁻ʳᵀ      = {parity['S·e⁻ᵠᵀ-K·e⁻ʳᵀ']:.8f}")
print(f"  誤差                  = {parity['parity_error']:.2e}  ✓" if parity["parity_error"] < 1e-8 else "  ⚠ 誤差過大")

# ─── 3. Monte-Carlo vs 解析 比較 ─────────────────────────────────────────────

print("\n" + "=" * 65)
print("Monte-Carlo 定價 vs Black-Scholes 解析解")
print("=" * 65)

mc_call, se_call = bs.monte_carlo("call", n_paths=200_000, seed=42)
mc_put,  se_put  = bs.monte_carlo("put",  n_paths=200_000, seed=42)

print(f"  Call  BS解析={call_res.price:.6f}  MC={mc_call:.6f} ±{se_call:.6f}")
print(f"  Put   BS解析={put_res.price:.6f}   MC={mc_put:.6f}  ±{se_put:.6f}")

# ─── 4. 隱含波動率 ─────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("隱含波動率（從市場價格逆算）")
print("=" * 65)

market_prices_call = [10.0, 12.5, 15.0, 8.0]
for mp in market_prices_call:
    iv = bs.implied_volatility(mp, "call")
    print(f"  Call 市場價={mp:.1f}  →  IV = {iv:.4%}")

# ─── 5. 美式期權（美國期權）─────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("【美國期權 / 美式期權】定價")
print("  方法：Longstaff-Schwartz LSM + CRR 二項樹")
print("=" * 65)

am = AmericanOption(S=S0, K=K, T=T, r=r, sigma=sigma)

# LSM
am_put_price, am_put_se = am.lsm("put", n_paths=50_000, n_steps=50, seed=42)
am_call_price, am_call_se = am.lsm("call", n_paths=50_000, n_steps=50, seed=42)

# 二項樹
am_put_tree  = am.binomial_tree("put",  n_steps=500)
am_call_tree = am.binomial_tree("call", n_steps=500)

print(f"\n  美式 Put：")
print(f"    LSM        = {am_put_price:.6f}  ±{am_put_se:.6f}")
print(f"    二項樹     = {am_put_tree:.6f}")
print(f"    歐式 BS    = {put_res.price:.6f}")
print(f"    提前執行溢價 = {am_put_price - put_res.price:.6f}")

print(f"\n  美式 Call（無股利時理論上不提前執行）：")
print(f"    LSM        = {am_call_price:.6f}  ±{am_call_se:.6f}")
print(f"    二項樹     = {am_call_tree:.6f}")
print(f"    歐式 BS    = {call_res.price:.6f}")
print(f"    提前執行溢價 = {am_call_price - call_res.price:.6f}  （≈0 驗證）")

# ─── 6. 不同參數下的美式溢價 ─────────────────────────────────────────────────

print("\n" + "=" * 65)
print("提前執行溢價 vs 波動率（Put）")
print("=" * 65)
print(f"  {'σ':>6}  {'歐式 Put':>10}  {'美式 Put (Tree)':>16}  {'溢價':>8}")
for sig in [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]:
    eu = BlackScholes(S0, K, T, r, sig).price("put").price
    am_t = AmericanOption(S0, K, T, r, sig).binomial_tree("put", 300)
    print(f"  {sig:>6.0%}  {eu:>10.4f}  {am_t:>16.4f}  {am_t-eu:>8.4f}")

# ─── 7. 繪圖 ────────────────────────────────────────────────────────────────

print("\n繪製 Black-Scholes 比較圖...")

t_paths, S_paths = bs.simulate_paths(n_paths=50, n_steps=252, seed=42)

am_summary = {
    "K": K, "S0": S0, "T": T, "r": r, "sigma": sigma,
    "eu_put":      put_res.price,
    "eu_call":     call_res.price,
    "am_put_lsm":  am_put_price,
    "am_put_tree": am_put_tree,
    "am_call_tree": am_call_tree,
    "early_exercise_premium": am_put_price - put_res.price,
}

fig = StochPlot.options_comparison(
    bs_result={"call": call_res, "put": put_res},
    am_result=am_summary,
    t_paths=t_paths,
    S_paths=S_paths,
    filename="./out/black_scholes_options.png",
)
print("已儲存至 ./out/black_scholes_options.png")
print("\n✓ Black-Scholes 範例完成")
