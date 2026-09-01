"""R-style stochastic plotting functions for math4py.

隨機過程繪圖（仿 R 風格，無 class）。
"""

import numpy as np
import matplotlib.pyplot as plt
from . import rplot


_PALETTE = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0",
           "#00BCD4", "#FF5722", "#607D8B"]


def brownian_motion(t, paths, title="布朗運動路徑", figsize=(14, 9)):
    """繪製布朗運動路徑圖。

    Args:
        t: 時間陣列
        paths: 布朗路徑 (n_paths x n_steps)
        title: 標題
        figsize: 圖形大小
    """
    fig, ax = plt.subplots(figsize=figsize)
    rplot._active_fig = fig
    n_paths = paths.shape[0]
    for i in range(min(n_paths, 50)):
        alpha = 0.55 if n_paths > 10 else 0.85
        ax.plot(t, paths[i], lw=0.9, alpha=alpha, color=_PALETTE[i % len(_PALETTE)])
    mu_path = paths.mean(axis=0)
    std_path = paths.std(axis=0)
    ax.plot(t, mu_path, "w--", lw=1.8, label="樣本均值")
    ax.fill_between(t, mu_path - std_path, mu_path + std_path, alpha=0.15, color="white", label="±1σ")
    ax.axhline(0, color="#aaa", lw=0.7, ls=":")
    ax.set_xlabel("時間 t")
    ax.set_ylabel("W(t)")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()

    if rplot._device is None:
        plt.show()
    else:
        rplot._save_current_figure()


def ito_integral_plot(result: dict, figsize=(14, 10)):
    """繪製伊藤積分圖。

    Args:
        result: 伊藤積分結果字典 (包含 t, W, ito_integral, analytic)
        figsize: 圖形大小
    """
    t = result["t"]
    W = result["W"]
    ito = result["ito_integral"]
    analytic = result["analytic"]

    fig, axes = plt.subplots(2, 2, figsize=figsize)
    rplot._active_fig = fig

    ax1 = axes[0, 0]
    for i in range(W.shape[0]):
        ax1.plot(t, W[i], lw=1.2, alpha=0.8, color=_PALETTE[i % len(_PALETTE)])
    ax1.set_xlabel("t")
    ax1.set_ylabel("W(t)")
    ax1.set_title("布朗運動路徑 W(t)")

    ax2 = axes[0, 1]
    for i in range(min(W.shape[0], 3)):
        ax2.plot(t, ito[i], lw=1.2, alpha=0.85, color=_PALETTE[i], label="數值")
        ax2.plot(t, analytic[i], "--", lw=1.2, alpha=0.85, color="white", label="解析")
    ax2.set_xlabel("t")
    ax2.set_ylabel("積分值")
    ax2.set_title("伊藤積分 vs 解析")
    ax2.legend(fontsize=7)

    ax3 = axes[1, 0]
    for i in range(min(W.shape[0], 3)):
        err = ito[i] - analytic[i]
        ax3.plot(t, err, lw=1.0, alpha=0.8, color=_PALETTE[i])
    ax3.axhline(0, color="#aaa", lw=0.7, ls=":")
    ax3.set_xlabel("t")
    ax3.set_ylabel("數值誤差")
    ax3.set_title("數值積分誤差")

    ax4 = axes[1, 1]
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis("off")
    text = "伊藤引理\n\nf(W) = W²\ndf = 2W dW + dt\n\n∫₀ᵀ W dW\n= ½W(T)² - ½T"
    ax4.text(0.05, 0.95, text, transform=ax4.transAxes, fontsize=9.5, va="top", fontfamily="monospace")

    plt.tight_layout()

    if rplot._device is None:
        plt.show()
    else:
        rplot._save_current_figure()


def options_plot(bs_result, am_result, t_paths, S_paths, figsize=(16, 11)):
    """繪製期權比較圖。

    Args:
        bs_result: Black-Scholes 結果
        am_result: 美式期權結果
        t_paths: 時間陣列
        S_paths: 股價路徑
        figsize: 圖形大小
    """
    from math4py.stochastic.calculus.options import BlackScholes

    K = am_result["K"]
    S0 = am_result["S0"]
    T = am_result["T"]
    r = am_result["r"]

    fig, axes = plt.subplots(2, 3, figsize=figsize)
    rplot._active_fig = fig

    ax1 = axes[0, 0]
    for i in range(min(S_paths.shape[0], 30)):
        ax1.plot(t_paths, S_paths[i], lw=0.7, alpha=0.5, color=_PALETTE[i % len(_PALETTE)])
    ax1.axhline(K, color="gold", lw=1.5, ls="--", label=f"K={K}")
    ax1.set_xlabel("時間")
    ax1.set_ylabel("股價")
    ax1.set_title("GBM 路徑")
    ax1.legend(fontsize=8)

    ax2 = axes[0, 1]
    S_range = np.linspace(max(1, K * 0.4), K * 1.8, 300)
    eu_payoff = np.maximum(K - S_range, 0) * np.exp(-r * T)
    ax2.plot(S_range, eu_payoff, color=_PALETTE[0], lw=2)
    ax2.axvline(K, color="gold", lw=1.2, ls="--")
    ax2.set_xlabel("S(T)")
    ax2.set_ylabel("折現收益")
    ax2.set_title("Put 到期收益")

    ax3 = axes[0, 2]
    S_vals = np.linspace(K * 0.5, K * 1.5, 60)
    eu_prices = [BlackScholes(sv, K, T, r, am_result["sigma"]).price("put").price for sv in S_vals]
    ax3.plot(S_vals, eu_prices, color=_PALETTE[0], lw=2)
    ax3.set_xlabel("S")
    ax3.set_ylabel("價格")
    ax3.set_title("歐式 Put 價格")

    ax4 = axes[1, 0]
    deltas = [BlackScholes(sv, K, T, r, am_result["sigma"]).price("put").delta for sv in S_vals]
    ax4.plot(S_vals, deltas, color=_PALETTE[3], lw=2)
    ax4.set_xlabel("S")
    ax4.set_ylabel("Δ")
    ax4.set_title("Delta")

    ax5 = axes[1, 1]
    ax5.axis("off")
    summary = [["指標", "歐式", "美式"], ["定價", "BS", "LSM"], ["Put", f"${am_result['eu_put']:.2f}", f"${am_result['am_put_tree']:.2f}"]]
    ax5.table(cellText=summary[1:], colLabels=summary[0], loc="center", cellLoc="center")
    ax5.set_title("期權比較")

    ax6 = axes[1, 2]
    res = BlackScholes(S0, K, T, r, am_result["sigma"]).price("put")
    greeks = [abs(res.delta), res.gamma * 100, abs(res.theta) * 365, res.vega * 100]
    ax6.barh(["Δ", "Γ×100", "Θ×365", "ν×100"], greeks, color=_PALETTE[:4])
    ax6.set_title("Greeks")

    plt.tight_layout()

    if rplot._device is None:
        plt.show()
    else:
        rplot._save_current_figure()