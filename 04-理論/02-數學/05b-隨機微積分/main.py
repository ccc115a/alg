"""
main.py — 執行全部三個範例並輸出圖表
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import subprocess
import os; os.makedirs("./out", exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── 執行三個範例 ──────────────────────────────────────────────────────────────
for ex in ["ex1_ito_integral", "ex2_brownian_motion", "ex3_black_scholes"]:
    script = os.path.join(os.path.dirname(__file__), "examples", f"{ex}.py")
    subprocess.run([sys.executable, script], check=True)

# ── 組合成一張總覽圖 ─────────────────────────────────────────────────────────
from PIL import Image  # type: ignore

files = [
    "./out/ito_integral.png",
    "./out/brownian_motion_detail.png",
    "./out/black_scholes_options.png",
]

imgs = [Image.open(f) for f in files]
widths = [im.width for im in imgs]
heights = [im.height for im in imgs]

max_w = max(widths)
total_h = sum(heights) + 20 * len(imgs)

canvas = Image.new("RGB", (max_w, total_h), color=(13, 17, 23))
y_off = 0
for im in imgs:
    x_off = (max_w - im.width) // 2
    canvas.paste(im, (x_off, y_off))
    y_off += im.height + 20

out_path = "./out/stochastic_calculus_overview.png"
canvas.save(out_path, dpi=(150, 150))
print(f"\n總覽圖已儲存：{out_path}")
