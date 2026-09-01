"""Example 2: Brownian Motion - math4py.stochastic.calculus"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
os.makedirs("./out", exist_ok=True)

from math4py.stochastic.calculus import BrownianMotion, OrnsteinUhlenbeck, BrownianBridge
# from math4py.stochastic.calculus.plot import StochPlot, _style, PALETTE, BG, TEXT, GRID
from math4py.plot import StochPlot, _style, PALETTE, BG, TEXT, GRID

# ─── 1. 標準布朗運動 ────────────────────────────────────────────────────────

print("=" * 60)
print("布朗運動（Wiener Process）")
print("=" * 60)

bm = BrownianMotion(mu=0.0, sigma=1.0, seed=2024)
t, paths = bm.simulate(T=1.0, n_steps=10_000, n_paths=200)

print(f"路徑數：{paths.shape[0]},  時間步：{paths.shape[1]-1}")
print(f"終點均值（樣本）：{paths[:, -1].mean():.6f}  （理論：0）")
print(f"終點標準差（樣本）：{paths[:, -1].std():.6f}  （理論：{1.0:.6f}）")

# 驗證二次變分
t_qv, qv = bm.quadratic_variation(T=1.0, n_steps=100_000)
print(f"二次變分 [W]_T = {qv[-1]:.6f}  （理論：T=1）")

# 自相關
print(f"\nCov(W(0.3), W(0.7)) = {bm.autocorrelation(0.3, 0.7):.4f}  （理論：min(0.3,0.7)=0.3）")

# ─── 2. 帶漂移的布朗運動 ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("帶漂移布朗運動：dX = μdt + σdW")
print("=" * 60)

for mu, sigma in [(0.5, 0.3), (0.0, 1.0), (-0.3, 0.5)]:
    bm_drift = BrownianMotion(mu=mu, sigma=sigma, seed=42)
    t_d, paths_d = bm_drift.simulate(T=2.0, n_steps=5000, n_paths=1000)
    final_mean = paths_d[:, -1].mean()
    theory_mean = mu * 2.0
    print(f"μ={mu:+.1f}, σ={sigma:.1f} → E[X(2)] 樣本={final_mean:.4f}, 理論={theory_mean:.4f}")

# ─── 3. Ornstein-Uhlenbeck ───────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Ornstein-Uhlenbeck（均值回歸）過程")
print("=" * 60)

ou = OrnsteinUhlenbeck(mu=2.0, theta=1.5, sigma=0.5, X0=0.0, seed=42)
t_ou, paths_ou = ou.simulate(T=10.0, n_steps=5000, n_paths=500)

print(f"穩態均值（理論）：{ou.stationary_mean():.4f}")
print(f"穩態均值（樣本，後半段）：{paths_ou[:, paths_ou.shape[1]//2:].mean():.4f}")
print(f"穩態方差（理論）：{ou.stationary_variance():.4f}")
print(f"穩態方差（樣本，後半段）：{paths_ou[:, paths_ou.shape[1]//2:].var():.4f}")

# ─── 4. 布朗橋 ──────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("布朗橋（Brownian Bridge）: B(0)=0, B(1)=0")
print("=" * 60)

bb = BrownianBridge(a=0.0, b=0.0, seed=42)
t_bb, paths_bb = bb.simulate(T=1.0, n_steps=5000, n_paths=200)
print(f"B(0)：{paths_bb[:, 0].mean():.8f}  （應為 0）")
print(f"B(1)：{paths_bb[:, -1].mean():.8f}  （應為 0）")
print(f"B(0.5) 標準差：{paths_bb[:, paths_bb.shape[1]//2].std():.6f}  （理論：0.5）")

# ─── 5. 繪圖：綜合 4 種過程 ───────────────────────────────────────────────────

print("\n繪製布朗運動綜合圖...")

fig = plt.figure(figsize=(16, 12), facecolor=BG)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

# ── (A) 標準布朗運動 ─────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
for i in range(min(30, paths.shape[0])):
    ax1.plot(t, paths[i], lw=0.7, alpha=0.4, color=PALETTE[i % len(PALETTE)])
mean_p = paths.mean(axis=0)
std_p = paths.std(axis=0)
ax1.plot(t, mean_p, "w-", lw=1.8, label="樣本均值")
ax1.fill_between(t, mean_p - 2*std_p, mean_p + 2*std_p,
                 alpha=0.12, color="white", label="±2σ 帶")
ax1.fill_between(t, np.sqrt(t), -np.sqrt(t),
                 alpha=0.08, color="cyan", label="理論 ±√t")
ax1.set_title("標準布朗運動 W(t)", color=TEXT)
ax1.set_xlabel("t"); ax1.set_ylabel("W(t)")
ax1.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
_style(fig, ax1)

# ── (B) Ornstein-Uhlenbeck ─────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
for i in range(min(20, paths_ou.shape[0])):
    ax2.plot(t_ou, paths_ou[i], lw=0.7, alpha=0.5,
             color=PALETTE[i % len(PALETTE)])
ax2.axhline(ou.mu, color="gold", lw=1.8, ls="--", label=f"均值 μ={ou.mu}")
var_th = ou.stationary_variance()
ax2.fill_between(t_ou,
                 ou.mu - 2*np.sqrt(var_th),
                 ou.mu + 2*np.sqrt(var_th),
                 alpha=0.12, color="gold", label="±2σ（穩態）")
ax2.set_title(f"O-U 過程 (θ={ou.theta}, μ={ou.mu}, σ={ou.sigma})", color=TEXT)
ax2.set_xlabel("t"); ax2.set_ylabel("X(t)")
ax2.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
_style(fig, ax2)

# ── (C) 布朗橋 ──────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
for i in range(min(30, paths_bb.shape[0])):
    ax3.plot(t_bb, paths_bb[i], lw=0.8, alpha=0.5,
             color=PALETTE[i % len(PALETTE)])
# 理論標準差：sqrt(t(1-t))
std_bb_th = np.sqrt(t_bb * (1 - t_bb))
ax3.fill_between(t_bb, -2*std_bb_th, 2*std_bb_th,
                 alpha=0.15, color="white", label="±2√(t(1-t))")
ax3.set_title("布朗橋 B(0)=B(1)=0", color=TEXT)
ax3.set_xlabel("t"); ax3.set_ylabel("B(t)")
ax3.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
_style(fig, ax3)

# ── (D) 二次變分 + 終點分布 ─────────────────────────────────────────────
from scipy import stats as sp_stats

ax4 = fig.add_subplot(gs[1, 1])
# 多條路徑的二次變分
n_qv = 5
bm_qv = BrownianMotion(seed=999)
for i in range(n_qv):
    t_q, qv_path = bm_qv.quadratic_variation(T=1.0, n_steps=10_000)
    ax4.plot(t_q, qv_path, lw=0.9, alpha=0.7,
             color=PALETTE[i], label=f"[W]_t 路徑{i+1}")
ax4.plot(t_q, t_q, "w--", lw=2, label="理論值 t")
ax4.set_title("二次變分 [W]_t → t（驗證）", color=TEXT)
ax4.set_xlabel("t"); ax4.set_ylabel("[W]_t")
ax4.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
_style(fig, ax4)

plt.suptitle("布朗運動：標準 / O-U / 布朗橋 / 二次變分",
             fontsize=14, color=TEXT, fontweight="bold")
plt.tight_layout()
fig.savefig("./out/brownian_motion.png", dpi=150, bbox_inches="tight", facecolor=BG)

# 同時也用 StochPlot 生成標準路徑圖
bm2 = BrownianMotion(seed=7)
t2, paths2 = bm2.simulate(T=1.0, n_steps=5000, n_paths=100)
fig2 = StochPlot.brownian_motion(t2, paths2, filename="./out/brownian_motion_detail.png")

print("已儲存至 ./out/brownian_motion.png")
print("已儲存至 ./out/brownian_motion_detail.png")
print("\n✓ 布朗運動範例完成")
