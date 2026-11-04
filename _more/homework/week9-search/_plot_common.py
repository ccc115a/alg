#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 各支 xxx_plot.py 共用的繪圖設定（中文字型等）
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

def setup_cjk():
    """找到系統上可用的中文字型並設為 matplotlib 預設字型"""
    candidates = ['PingFang TC', 'PingFang HK', 'Heiti TC',
                  'Noto Sans CJK TC', 'Noto Sans TC',
                  'Microsoft JhengHei', 'Arial Unicode MS']
    have = {f.name for f in fm.fontManager.ttflist}
    for c in candidates:
        if c in have:
            plt.rcParams['font.sans-serif'] = [c, 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            return c
    return None
