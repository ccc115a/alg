"""
plot.py — 視覺化工具模組
R 風格繪圖 + 隨機過程視覺化
"""

import numpy as np
import platform
import matplotlib
import matplotlib.font_manager as _fm

def _pick_cjk_fonts() -> list:
    available = {f.name for f in _fm.fontManager.ttflist}
    candidates = {
        "Darwin": ["PingFang TC", "PingFang SC", "Heiti TC", "Heiti SC", "STHeiti", "Hiragino Sans GB", "Arial Unicode MS"],
        "Linux": ["Noto Sans CJK TC", "Noto Sans CJK SC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "WenQuanYi Micro Hei"],
        "Windows": ["Microsoft JhengHei", "Microsoft YaHei", "DFKai-SB", "MingLiU"],
    }
    system = platform.system()
    ordered = candidates.get(system, []) + sum([v for k, v in candidates.items() if k != system], [])
    chosen = [f for f in ordered if f in available]
    return chosen + ["DejaVu Sans"]

matplotlib.rcParams["font.family"] = _pick_cjk_fonts()
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

# R-style plotting functions
from .rplot import (
    plot, hist, boxplot, qqnorm,
    pdf, png, dev_off,
)

# R-style entropy plotting functions
from .rplot_entropy import (
    plot_entropy,
    plot_kl,
)

# R-style stochastic plotting functions
from .rplot_stochastic import (
    brownian_motion,
    ito_integral_plot,
    options_plot,
)
