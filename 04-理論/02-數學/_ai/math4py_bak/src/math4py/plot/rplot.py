"""R-style plotting functions for math4py.

仿 R 的 plot(), hist(), boxplot(), pdf(), png(), dev.off() 等函式，
提供熟悉的 R 使用者介面。底層使用 matplotlib，但包裝成 R 風格 API。
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Union, List, Tuple, Dict, Any

# 預設輸出目錄
# 從 rplot.py: plot/ -> math4py/ -> src/ -> (專案根目錄 math4py/) -> out
_OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "out")

# 調色板
_PALETTE = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0",
           "#00BCD4", "#FF5722", "#607D8B"]

# 全域設備設定（仿 R 的 device 概念）
_device = None      # None = 螢幕, "pdf", "png"
_device_params = {}  # 存放設備參數
_active_fig = None  # 追蹤目前圖形


def pdf(filename, width=7, height=7):
    """打開 PDF 設備（仿 R pdf()）。

    設定後的繪圖會輸出到 PDF 檔案，可連續繪圖多個圖到同一個 PDF。

    Args:
        filename: 輸出檔名
        width: 寬度（英吋）
        height: 高度（英吋）

    Examples:
        pdf("output.pdf")
        plot(x, y)
        plot(z, w)
        dev_off()
    """
    global _device, _device_params
    _device = "pdf"
    _device_params = {"filename": filename, "width": width, "height": height}


def png(filename, width=7, height=7, dpi=150):
    """打開 PNG 設備（仿 R png()）。

    Args:
        filename: 輸出檔名
        width: 寬度（英吋）
        height: 高度（英吋）
        dpi: 解析度

    Examples:
        png("output.png", dpi=300)
        hist(data)
        dev_off()
    """
    global _device, _device_params
    _device = "png"
    _device_params = {"filename": filename, "width": width, "height": height, "dpi": dpi}


def dev_off():
    """關閉當前設備（仿 R dev.off()），恢復螢幕輸出。

    關閉 PDF/PNG 設備，之後的繪圖會顯示在螢幕上。
    """
    global _device, _device_params, _active_fig
    if _active_fig is not None and _device is not None:
        # 儲存目前開啟的圖形
        _save_current_figure()
    _device = None
    _device_params = {}
    _active_fig = None


def _save_current_figure():
    """儲存當前圖形到檔案。"""
    global _active_fig
    if _active_fig is None:
        return
    if _device is None:
        # 螢幕模式，不需要在這裡儲存
        return
    os.makedirs(_OUT_DIR, exist_ok=True)
    
    filepath = _device_params.get("filename")
    if not os.path.dirname(filepath):
        filepath = os.path.join(_OUT_DIR, filepath)
    
    if _device == "pdf":
        _active_fig.savefig(
            filepath,
            format="pdf",
            bbox_inches="tight"
        )
    elif _device == "png":
        _active_fig.savefig(
            filepath,
            format="png",
            dpi=_device_params.get("dpi", 150),
            bbox_inches="tight"
        )
    plt.close(_active_fig)
    _active_fig = None


def _new_figure():
    """建立新圖形，處理設備切換。"""
    global _active_fig
    
    # 如果有開啟的圖形且正在寫入檔案，先儲存
    if _active_fig is not None and _device is not None:
        _save_current_figure()
    
    if _device is None:
        # 螢幕輸出
        return plt.subplots()
    else:
        # 檔案輸出
        figsize = (_device_params.get("width", 7), _device_params.get("height", 7))
        fig = plt.figure(figsize=figsize)
        return fig, fig.add_subplot(111)


def plot(x, y=None, type="p", main="", xlab="", ylab="",
         col="blue", pch="o", lty=1, lwd=1,
         xlim=None, ylim=None, axes=True, **kwargs):
    """泛型繪圖函數（仿 R plot()）。

    Args:
        x: x 軸資料，或單一資料（此時 y 為 None）
        y: y 軸資料（可選）
        type: 圖形類型
            "p" = 散點圖（points）
            "l" = 折線圖（lines）
            "b" = 點線圖（both points and lines）
        main: 標題（支援中文）
        xlab: x 軸標籤（支援中文）
        ylab: y 軸標籤（支援中文）
        col: 顏色
        pch: 點的形狀
        lty: 線的樣式（1=實線, 2=虛線, ...）
        lwd: 線的寬度
        xlim: x 軸範圍 (xmin, xmax)
        ylim: y 軸範圍 (ymin, ymax)
        axes: 是否顯示座標軸
        **kwargs: 其他傳給 matplotlib 的參數

    Examples:
        plot(x, y)                    # 散點圖
        plot(x, y, type="l")           # 折線圖
        plot(x)                        # 時間序列圖
    """
    fig, ax = _new_figure()
    global _active_fig
    _active_fig = fig

    if y is None:
        y = np.asarray(x)
        x = np.arange(len(y))
        type = type if type != "p" else "l"

    x = np.asarray(x)
    y = np.asarray(y)

    linestyles = {1: "solid", 2: "dashed", 3: "dotted"}
    ls = linestyles.get(lty, "solid")

    if type == "p":
        ax.scatter(x, y, c=col, marker=pch, **kwargs)
    elif type == "l":
        ax.plot(x, y, color=col, linestyle=ls, linewidth=lwd, **kwargs)
    elif type == "b":
        ax.plot(x, y, color=col, linestyle=ls, linewidth=lwd, **kwargs)
        ax.scatter(x, y, c=col, marker=pch, **kwargs)
    else:
        raise ValueError(f"Unknown type: {type}")

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if not axes:
        ax.axis("off")

    plt.tight_layout()
    
    if _device is None:
        plt.show()
    # 若正在寫入檔案，等待 dev_off() 時才儲存


def hist(x, breaks=10, main="", xlab="", col="skyblue",
         border="black", freq=True, **kwargs):
    """直方圖（仿 R hist()）。

    Args:
        x: 資料
        breaks: 區間數或區間點
        main: 標題（支援中文）
        xlab: x 軸標籤（支援中文）
        col: 柱狀顏色
        border: 邊框顏色
        freq: True=頻率, False=密度
        **kwargs: 其他傳給 matplotlib 的參數
    """
    fig, ax = _new_figure()
    global _active_fig
    _active_fig = fig
    
    x = np.asarray(x)
    ax.hist(x, bins=breaks, color=col, edgecolor=border,
            density=not freq, **kwargs)

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    ax.set_ylabel("Frequency" if freq else "Density")

    plt.tight_layout()
    
    if _device is None:
        plt.show()


def boxplot(*data, names=None, main="", xlab="", ylab="", col="skyblue", **kwargs):
    """盒鬚圖（仿 R boxplot()）。

    Args:
        *data: 多組資料
        names: 每組資料的名稱
        main: 標題（支援中文）
        xlab: x 軸標籤
        ylab: y 軸標籤
        col: 盒體顏色
        **kwargs: 其他傳給 matplotlib 的參數
    """
    fig, ax = _new_figure()
    global _active_fig
    _active_fig = fig
    
    data = [np.asarray(d) for d in data]
    bp = ax.boxplot(data, tick_labels=names, patch_artist=True, **kwargs)
    for box in bp["boxes"]:
        box.set_facecolor(col)

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)

    plt.tight_layout()
    
    if _device is None:
        plt.show()


def qqnorm(x, main="Q-Q Plot", xlab="Theoretical Quantiles",
          ylab="Sample Quantiles", col="blue", **kwargs):
    """Q-Q 圖（仿 R qqnorm()），用於檢驗常態性。

    Args:
        x: 資料
        main: 標題（支援中文）
        xlab: x 軸標籤
        ylab: y 軸標籤
        col: 點的顏色
        **kwargs: 其他傳給 matplotlib 的參數
    """
    from math4py.statistics.distributions import qnorm
    
    fig, ax = _new_figure()
    global _active_fig
    _active_fig = fig
    
    x = np.asarray(x)
    x_sorted = np.sort(x)
    n = len(x_sorted)

    p = (np.arange(1, n+1) - 0.5) / n
    theoretical = qnorm(p, mean=0, sd=1)
    sample = (x_sorted - x_sorted.mean()) / x_sorted.std()

    ax.scatter(theoretical, sample, c=col, **kwargs)
    min_val = min(theoretical.min(), sample.min())
    max_val = max(theoretical.max(), sample.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", alpha=0.5)

    if main:
        ax.set_title(main, fontsize=14)
    if xlab:
        ax.set_xlabel(xlab)
    if ylab:
        ax.set_ylabel(ylab)

    plt.tight_layout()
    
if _device is None:
        plt.show()