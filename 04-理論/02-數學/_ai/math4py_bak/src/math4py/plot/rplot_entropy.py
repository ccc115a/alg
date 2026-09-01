"""R-style entropy plotting functions for math4py.

資訊論視覺化（仿 R 風格，無 class）。
"""

import numpy as np
import matplotlib.pyplot as plt
import os as _os
from . import rplot


def plot_entropy(p, base=2, main="Entropy", xlab="Outcome", ylab="Probability",
               col="skyblue", **kwargs):
    """繪製熵長條圖。

    Args:
        p: 機率分佈
        base: 對數底數
        main: 標題（支援中文）
        xlab: x 軸標籤
        ylab: y 軸標籤
        col: 顏色
        **kwargs: 其他傳給 matplotlib 的參數
    """
    from math4py.statistics.entropy import entropy

    fig, ax = plt.subplots()
    rplot._active_fig = fig

    p = np.asarray(p)
    n = len(p)
    indices = np.arange(n)

    ax.bar(indices, p, color=col, edgecolor="black", **kwargs)
    ax.text(0.5, 0.95, f"H = {entropy(p, base):.4f} bits",
            transform=ax.transAxes, ha="center", fontsize=12)

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)
    ax.set_xticks(indices)

    plt.tight_layout()

    if rplot._device is None:
        plt.show()
    else:
        rplot._save_current_figure()


def plot_kl(p, q, base=2, main="KL Divergence",
           xlab="Outcome", ylab="Probability",
           col1="skyblue", col2="orange", **kwargs):
    """視覺化 KL 散度。

    Args:
        p: 真實分佈
        q: 近似分佈
        base: 對數底數
        main: 標題（支援中文）
        xlab: x 軸標籤
        ylab: y 軸標籤
        col1: p 分佈顏色
        col2: q 分佈顏色
        **kwargs: 其他傳給 matplotlib 的參數
    """
    from math4py.statistics.entropy import kl_divergence

    fig, ax = plt.subplots()
    rplot._active_fig = fig

    p = np.asarray(p)
    q = np.asarray(q)
    n = len(p)
    indices = np.arange(n)
    width = 0.35

    ax.bar(indices - width/2, p, width, color=col1, label="P (true)", **kwargs)
    ax.bar(indices + width/2, q, width, color=col2, label="Q (approx)", **kwargs)
    kl = kl_divergence(p, q, base)
    ax.text(0.5, 0.95, f"D_KL(P||Q) = {kl:.4f}",
            transform=ax.transAxes, ha="center", fontsize=12)

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)
    ax.set_xticks(indices)
    ax.legend()

    plt.tight_layout()

    if rplot._device is None:
        plt.show()
    else:
        rplot._save_current_figure()