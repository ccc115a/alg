"""
plot.py — 視覺化工具模組
"""

import numpy as np
import platform
import matplotlib
import matplotlib.font_manager as _fm

def _pick_cjk_fonts() -> list:
    """
    依作業系統自動選擇可用的 CJK 字型，確保中文在各平台正確顯示。
    macOS  → PingFang TC / Heiti TC
    Linux  → Noto Sans CJK / WenQuanYi
    Windows→ Microsoft JhengHei / YaHei
    """
    available = {f.name for f in _fm.fontManager.ttflist}
    candidates = {
        "Darwin": [
            "PingFang TC", "PingFang SC",
            "Heiti TC", "Heiti SC", "STHeiti",
            "Hiragino Sans GB", "Arial Unicode MS",
        ],
        "Linux": [
            "Noto Sans CJK TC", "Noto Sans CJK SC",
            "Noto Sans CJK JP",
            "WenQuanYi Zen Hei", "WenQuanYi Micro Hei",
        ],
        "Windows": [
            "Microsoft JhengHei", "Microsoft YaHei",
            "DFKai-SB", "MingLiU",
        ],
    }
    system = platform.system()
    ordered = candidates.get(system, []) + sum(
        [v for k, v in candidates.items() if k != system], []
    )
    chosen = [f for f in ordered if f in available]
    return chosen + ["DejaVu Sans"]

matplotlib.rcParams["font.family"] = _pick_cjk_fonts()
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from typing import Optional

PALETTE = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0",
           "#00BCD4", "#FF5722", "#607D8B"]
BG = "#0d1117"
TEXT = "#e6edf3"
GRID = "#21262d"


def _style(fig, axes=None):
    fig.patch.set_facecolor(BG)
    if axes is None:
        return
    for ax in (axes if hasattr(axes, "__iter__") else [axes]):
        ax.set_facecolor("#161b22")
        ax.tick_params(colors=TEXT, labelsize=9)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)
        ax.grid(color=GRID, linewidth=0.6, alpha=0.8)


class StochPlot:
    """靜態工具類別：提供各類隨機微積分視覺化方法。"""

    # ──────────────────────────────────────────────────────────────────────
    # 布朗運動
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def brownian_motion(
        t, paths, title="布朗運動路徑", figsize=(14, 9), filename=None
    ):
        n_paths = paths.shape[0]
        fig = plt.figure(figsize=figsize, facecolor=BG)
        gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

        # ── (A) 路徑圖 ───────────────────────────────────────────────────
        ax1 = fig.add_subplot(gs[0, :])
        for i in range(min(n_paths, 50)):
            alpha = 0.55 if n_paths > 10 else 0.85
            ax1.plot(t, paths[i], lw=0.9, alpha=alpha,
                     color=PALETTE[i % len(PALETTE)])
        mu_path = paths.mean(axis=0)
        std_path = paths.std(axis=0)
        ax1.plot(t, mu_path, "w--", lw=1.8, label="樣本均值")
        ax1.fill_between(t, mu_path - std_path, mu_path + std_path,
                         alpha=0.15, color="white", label="±1σ")
        ax1.axhline(0, color="#aaa", lw=0.7, ls=":")
        ax1.set_xlabel("時間 t")
        ax1.set_ylabel("W(t)")
        ax1.set_title(title, fontsize=13, fontweight="bold")
        ax1.legend(loc="upper left", fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax1)

        # ── (B) 終點分布 ─────────────────────────────────────────────────
        ax2 = fig.add_subplot(gs[1, 0])
        finals = paths[:, -1]
        ax2.hist(finals, bins=40, color=PALETTE[0], alpha=0.8,
                 edgecolor="#333", density=True)
        T_val = t[-1]
        x_range = np.linspace(finals.min(), finals.max(), 200)
        from scipy import stats as sp_stats
        ax2.plot(x_range,
                 sp_stats.norm.pdf(x_range, 0, np.sqrt(T_val)),
                 "r-", lw=2, label=f"N(0,{T_val:.1f})")
        ax2.set_xlabel("W(T)")
        ax2.set_ylabel("密度")
        ax2.set_title("終點分布（理論 vs 樣本）")
        ax2.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax2)

        # ── (C) 二次變分 vs t ─────────────────────────────────────────────
        ax3 = fig.add_subplot(gs[1, 1])
        dt = t[1] - t[0]
        dW = np.diff(paths, axis=1)
        qv_mean = (dW ** 2).cumsum(axis=1).mean(axis=0)
        ax3.plot(t[1:], qv_mean, color=PALETTE[2], lw=1.8, label="樣本二次變分")
        ax3.plot(t, t, "r--", lw=1.5, label="理論值 t")
        ax3.set_xlabel("t")
        ax3.set_ylabel("[W]_t")
        ax3.set_title("二次變分 [W]_t → t")
        ax3.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax3)

        plt.suptitle("標準布朗運動（Wiener Process）分析",
                     fontsize=14, color=TEXT, y=1.01, fontweight="bold")
        plt.tight_layout()
        if filename:
            fig.savefig(filename, dpi=150, bbox_inches="tight",
                        facecolor=BG)
        return fig

    # ──────────────────────────────────────────────────────────────────────
    # 伊藤積分
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def ito_integral(result: dict, figsize=(14, 10), filename=None):
        t = result["t"]
        W = result["W"]
        ito = result["ito_integral"]
        analytic = result["analytic"]
        strat = result["stratonovich"]
        corr = result["ito_correction"]

        n_paths = W.shape[0]
        fig = plt.figure(figsize=figsize, facecolor=BG)
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

        # ── (A) 布朗路徑 ─────────────────────────────────────────────────
        ax1 = fig.add_subplot(gs[0, :2])
        for i in range(n_paths):
            ax1.plot(t, W[i], lw=1.2, alpha=0.8,
                     color=PALETTE[i % len(PALETTE)], label=f"W_{i+1}(t)")
        ax1.set_xlabel("t"); ax1.set_ylabel("W(t)")
        ax1.set_title("布朗運動路徑 W(t)")
        ax1.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax1)

        # ── (B) 伊藤 vs 解析 ─────────────────────────────────────────────
        ax2 = fig.add_subplot(gs[0, 2])
        for i in range(n_paths):
            ax2.plot(t, ito[i], lw=1.2, alpha=0.85,
                     color=PALETTE[i], label=f"∫W dW (數值)")
            ax2.plot(t, analytic[i], "--", lw=1.2, alpha=0.85,
                     color=PALETTE[i + n_paths] if i + n_paths < len(PALETTE) else "white",
                     label="½W²-½t (解析)")
        ax2.set_xlabel("t"); ax2.set_ylabel("積分值")
        ax2.set_title("∫₀ᵗ W dW vs 解析解")
        ax2.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax2)

        # ── (C) 誤差 ─────────────────────────────────────────────────────
        ax3 = fig.add_subplot(gs[1, 0])
        for i in range(n_paths):
            err = ito[i] - analytic[i]
            ax3.plot(t, err, lw=1.0, alpha=0.8, color=PALETTE[i])
        ax3.axhline(0, color="#aaa", lw=0.7, ls=":")
        ax3.set_xlabel("t"); ax3.set_ylabel("數值誤差")
        ax3.set_title("數值積分誤差（≈ O(√dt)）")
        _style(fig, ax3)

        # ── (D) 伊藤 vs Stratonovich ──────────────────────────────────────
        ax4 = fig.add_subplot(gs[1, 1])
        for i in range(n_paths):
            ax4.plot(t, ito[i], lw=1.2, color=PALETTE[0],
                     label="伊藤積分（左端點）")
            ax4.plot(t, strat[i], lw=1.2, color=PALETTE[1],
                     alpha=0.85, label="Stratonovich（中點）")
        ax4.plot(t, corr, "w--", lw=1.2, label="½t（修正差）")
        ax4.set_xlabel("t"); ax4.set_ylabel("積分值")
        ax4.set_title("伊藤 vs Stratonovich")
        ax4.legend(fontsize=7, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax4)

        # ── (E) 說明文字 ─────────────────────────────────────────────────
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.set_xlim(0, 1); ax5.set_ylim(0, 1); ax5.axis("off")
        text = (
            "伊藤引理核心公式\n\n"
            "f(W) = W²\n\n"
            "df = 2W dW + dt\n\n"
            "⟹  ∫₀ᵀ W dW\n"
            "   = ½W(T)² - ½T\n\n"
            "伊藤修正項：½T\n"
            "（來自 dW² = dt）\n\n"
            "Stratonovich:\n"
            "∫₀ᵀ W ∘ dW = ½W(T)²\n"
            "（無修正項）"
        )
        ax5.text(0.05, 0.95, text, transform=ax5.transAxes,
                 fontsize=9.5, color=TEXT, va="top",
                 fontfamily="monospace",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#1c2128",
                           edgecolor=PALETTE[0], lw=1.5))
        _style(fig, ax5)

        plt.suptitle("伊藤積分：∫₀ᵀ W(t) dW(t) = ½W(T)² - ½T",
                     fontsize=14, color=TEXT, fontweight="bold")
        plt.tight_layout()
        if filename:
            fig.savefig(filename, dpi=150, bbox_inches="tight", facecolor=BG)
        return fig

    # ──────────────────────────────────────────────────────────────────────
    # Black-Scholes / 期權比較
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def options_comparison(
        bs_result, am_result, t_paths, S_paths,
        figsize=(16, 11), filename=None
    ):
        fig = plt.figure(figsize=figsize, facecolor=BG)
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

        K = am_result["K"]
        S0 = am_result["S0"]
        T = am_result["T"]
        r = am_result["r"]

        # ── (A) GBM 路徑 ─────────────────────────────────────────────────
        ax1 = fig.add_subplot(gs[0, :2])
        for i in range(min(S_paths.shape[0], 30)):
            ax1.plot(t_paths, S_paths[i], lw=0.7, alpha=0.5,
                     color=PALETTE[i % len(PALETTE)])
        ax1.axhline(K, color="gold", lw=1.5, ls="--", label=f"K={K}")
        ax1.axhline(S0, color="white", lw=1.0, ls=":", alpha=0.6, label=f"S₀={S0}")
        ax1.set_xlabel("時間（年）"); ax1.set_ylabel("股價 S(t)")
        ax1.set_title("幾何布朗運動：股價路徑（GBM）")
        ax1.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax1)

        # ── (B) Put 收益圖 ───────────────────────────────────────────────
        ax2 = fig.add_subplot(gs[0, 2])
        S_range = np.linspace(max(1, K * 0.4), K * 1.8, 300)
        eu_payoff = np.maximum(K - S_range, 0) * np.exp(-r * T)
        ax2.plot(S_range, eu_payoff, color=PALETTE[0], lw=2,
                 label="歐式 Put 到期收益（折現）")
        ax2.axvline(K, color="gold", lw=1.2, ls="--", label=f"K={K}")
        ax2.fill_between(S_range, eu_payoff, alpha=0.15, color=PALETTE[0])
        ax2.set_xlabel("S(T)"); ax2.set_ylabel("折現收益")
        ax2.set_title("Put 到期收益結構")
        ax2.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax2)

        # ── (C) 美式 vs 歐式 Put 價格 vs S ─────────────────────────────
        ax3 = fig.add_subplot(gs[1, :2])
        S_vals = np.linspace(K * 0.5, K * 1.5, 60)
        eu_prices, am_prices_tree = [], []
        from .options import BlackScholes, AmericanOption
        for sv in S_vals:
            eu_prices.append(
                BlackScholes(sv, K, T, r, am_result["sigma"]).price("put").price
            )
            am_prices_tree.append(
                AmericanOption(sv, K, T, r, am_result["sigma"]).binomial_tree("put", 200)
            )
        eu_prices = np.array(eu_prices)
        am_prices_tree = np.array(am_prices_tree)

        intrinsic = np.maximum(K - S_vals, 0)
        ax3.plot(S_vals, am_prices_tree, color=PALETTE[1], lw=2.0,
                 label="美式 Put（二項樹）")
        ax3.plot(S_vals, eu_prices, color=PALETTE[0], lw=2.0,
                 label="歐式 Put（BS 解析）", ls="--")
        ax3.plot(S_vals, intrinsic, color="gold", lw=1.5, ls=":",
                 label="內涵價值 max(K-S,0)")
        ax3.fill_between(S_vals, eu_prices, am_prices_tree,
                         alpha=0.25, color=PALETTE[2],
                         label="提前執行溢價")
        ax3.axvline(K, color="gray", lw=1.0, ls="--")
        ax3.set_xlabel("現貨價格 S")
        ax3.set_ylabel("期權價格")
        ax3.set_title("美式 Put vs 歐式 Put（價格 vs 現貨）")
        ax3.legend(fontsize=8, facecolor=BG, labelcolor=TEXT)
        _style(fig, ax3)

        # ── (D) Delta vs S ─────────────────────────────────────────────
        ax4 = fig.add_subplot(gs[1, 2])
        deltas = [BlackScholes(sv, K, T, r, am_result["sigma"]).price("put").delta
                  for sv in S_vals]
        ax4.plot(S_vals, deltas, color=PALETTE[3], lw=2)
        ax4.axhline(-0.5, color="white", lw=0.8, ls=":", alpha=0.6)
        ax4.axvline(K, color="gray", lw=1.0, ls="--")
        ax4.set_xlabel("S"); ax4.set_ylabel("Δ")
        ax4.set_title("Delta（歐式 Put）")
        _style(fig, ax4)

        # ── (E) 數值摘要表 ───────────────────────────────────────────────
        ax5 = fig.add_subplot(gs[2, :2])
        ax5.axis("off")
        eep = am_result.get("early_exercise_premium", 0)
        summary = [
            ["指標", "歐式（英國期權）", "美式（美國期權）"],
            ["定價方法", "Black-Scholes 解析", "LSM + 二項樹"],
            ["Put 價格",
             f"${am_result['eu_put']:.4f}",
             f"${am_result['am_put_lsm']:.4f} (LSM)\n${am_result['am_put_tree']:.4f} (Tree)"],
            ["Call 價格",
             f"${am_result['eu_call']:.4f}",
             f"${am_result['am_call_tree']:.4f} (Tree)"],
            ["提前執行溢價", "—", f"${eep:.4f}"],
            ["Put-Call Parity", "✓ 嚴格成立", "⚠ 不成立（美式）"],
            ["執行時間", "僅到期日", "任意時間點"],
        ]
        table = ax5.table(
            cellText=summary[1:],
            colLabels=summary[0],
            loc="center",
            cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.6)
        for (r_idx, c_idx), cell in table.get_celld().items():
            cell.set_facecolor("#1c2128" if r_idx % 2 == 0 else "#161b22")
            cell.set_edgecolor(GRID)
            cell.set_text_props(color=TEXT)
            if r_idx == 0:
                cell.set_facecolor("#21262d")
                cell.set_text_props(color=PALETTE[0], fontweight="bold")
        ax5.set_title("美式 vs 歐式期權比較摘要", color=TEXT, fontsize=11)
        _style(fig, ax5)

        # ── (F) Vega / Gamma / Theta Greeks ──────────────────────────────
        ax6 = fig.add_subplot(gs[2, 2])
        greeks_name = ["Delta", "Gamma×100", "Theta×365", "Vega×100"]
        res = BlackScholes(S0, K, T, r, am_result["sigma"]).price("put")
        greeks_val = [
            abs(res.delta),
            res.gamma * 100,
            abs(res.theta) * 365,
            res.vega * 100,
        ]
        bars = ax6.barh(greeks_name, greeks_val,
                        color=PALETTE[:4], alpha=0.85)
        ax6.set_xlabel("值（標準化）")
        ax6.set_title(f"歐式 Put Greeks（S={S0}, K={K}）")
        for bar, val in zip(bars, greeks_val):
            ax6.text(bar.get_width() + 0.01 * max(greeks_val), bar.get_y() + bar.get_height() / 2,
                     f"{val:.3f}", va="center", color=TEXT, fontsize=8)
        _style(fig, ax6)

        plt.suptitle("Black-Scholes 模型：英國期權（歐式）vs 美國期權（美式）",
                     fontsize=14, color=TEXT, fontweight="bold", y=1.01)
        plt.tight_layout()
        if filename:
            fig.savefig(filename, dpi=150, bbox_inches="tight", facecolor=BG)
        return fig
