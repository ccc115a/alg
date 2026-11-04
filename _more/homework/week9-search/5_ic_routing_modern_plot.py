#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 5（進階動畫）：PathFinder 可協商擠塞繞線 + Q-learning 軌跡
#
#   前半部：每一輪談判的畫面
#     A B C D = 接腳，1 2 3 4 = 各 net 的線
#     *       = 兩條 net 共用但未超載的格子
#     紅框     = 這一輪「超載」的格子（談判要解决的問題）
#
#   後半部：Q-learning（強化學習）訓練完成的 policy，逐步走出最短路
#     綠色線 = agent 一路貪心走的軌跡
#
# 執行：python3 5_ic_routing_modern_plot.py

import heapq
import random
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from _plot_common import setup_cjk
setup_cjk()

# ---------- PathFinder 的格子與 net ----------
GRID_C = [
    "....#.....",
    "....#.....",
    "....#.....",
    "..........",
    "....#.....",
    "..........",
    "....#.....",
    "....#.....",
]
NCR_NETS = [('A', (0, 0), (0, 9)),
            ('B', (2, 0), (2, 9)),
            ('C', (4, 0), (4, 9)),
            ('D', (6, 0), (6, 9))]
CAP = {(y, x): 2 for y in range(8) for x in range(10) if GRID_C[y][x] == '.'}
ROWS, COLS = len(GRID_C), len(GRID_C[0])
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def dijkstra(start, goal, cost_fn):
    g = {start: 0}
    parent = {start: None}
    pq = [(0, start)]
    while pq:
        d, cur = heapq.heappop(pq)
        if d > g[cur]:
            continue
        if cur == goal:
            path, at = [], cur
            while at:
                path.append(at); at = parent[at]
            return path[::-1]
        y, x = cur
        for dy, dx in DIRS:
            n = (y + dy, x + dx)
            if 0 <= n[0] < ROWS and 0 <= n[1] < COLS and GRID_C[n[0]][n[1]] == '.':
                nd = d + cost_fn(n)
                if n not in g or nd < g[n]:
                    g[n] = nd
                    parent[n] = cur
                    heapq.heappush(pq, (nd, n))
    return None

# ---------- 有錄影功能的 PathFinder ----------
cur = {}
history = Counter()
p_fac = 1.0
round_frames = []        # (round, routes dict, overflow dict, 說明文字)
demand = Counter()

def record(rnd, note):
    demand_cur = Counter()
    for name, path in cur.items():
        demand_cur.update(path)
    ov = {c: demand_cur[c] - CAP[c] for c in demand_cur if demand_cur[c] > CAP[c]}
    round_frames.append((rnd, {n: list(p) for n, p in cur.items()}, ov, note))

for rnd in range(1, 41):
    for name, start, goal in NCR_NETS:
        if rnd == 1:
            path = dijkstra(start, goal, lambda c: 1)
            cur[name] = path
            demand.update(path)
        else:
            for c in cur[name]:
                demand[c] -= 1
            def cost(c):
                return 1 + p_fac * demand[c] + history[c]
            path = dijkstra(start, goal, cost)
            cur[name] = path
            demand.update(path)
    ov = {c: demand[c] - CAP[c] for c in demand if demand[c] > CAP[c]}
    note = (f"第 {rnd} 輪（未談判）：超載 {len(ov)} 格" if rnd == 1
            else f"第 {rnd} 輪：超載 {len(ov)} 格")
    record(rnd, note)
    if not ov:
        break
    for c in ov:
        history[c] += demand[c] - CAP[c]
    p_fac *= 2

# ---------- Q-learning（學好的 policy 走路的示意） ----------
GRID = [
    "..........",
    "..........",
    "....#.....",
    "..........",
    "....#.....",
    "....#.....",
    "..........",
    "..........",
]
Q_START, Q_GOAL = (7, 0), (0, 9)
Q_PATH = [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (6, 4), (5, 4),
          (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (4, 9), (3, 9),
          (2, 9), (1, 9), (0, 9)]     # 16 步 = BFS 最短

# ---------- 動畫 ----------
fig, ax = plt.subplots(figsize=(6.4, 5.6))
ax.set_xlim(-0.5, COLS - 0.5); ax.set_ylim(ROWS - 0.5, -0.5)
ax.set_xticks([]); ax.set_yticks([])
title = ax.set_title('PathFinder 協商擠塞繞線', fontsize=12)

def ncr_base():
    g = [[0 if GRID_C[y][x] == '#' else 1 for x in range(COLS)]
         for y in range(ROWS)]
    return g

def update(i):
    n_rounds = len(round_frames)
    ncr_phase = i < n_rounds
    for t in ncr_pins:
        t.set_visible(ncr_phase)
    for t in ncr_pins:
        t.set_visible(ncr_phase)
    for t in q_pins:
        t.set_visible(not ncr_phase)
    if i < n_rounds:
        rnd, routes, ov, note = round_frames[i]
        g = ncr_base()
        # 先上 net 線（序數 = 3..7）
        users = {}
        sym = {n: 3 + k for k, n in enumerate(routes)}
        for name, path in routes.items():
            for (y, x) in path:
                if GRID_C[y][x] == '.':
                    users.setdefault((y, x), []).append(sym[name])
        for (y, x), us in users.items():
            g[y][x] = us[0] if len(us) == 1 else 8   # 8 = 共用色
        for (y, x) in ov:
            g[y][x] = 9                               # 9 = 超載紅
        im.set_data(g)
        label = note
        if ov:
            label += "（紅 = 超載的格子，談判要解決的問題）"
        else:
            label += "（* = 兩條 net 共用、沒超過容量）→ 收斂！"
        title.set_text("PathFinder 協商擠塞繞線（A/B/C/D 4 條 net）\n" + label)
    else:
        # Q-learning 軌跡部分（底板換成 Q 用的 GRID）
        k = i - n_rounds
        g = [[0 if GRID[y][x] == '#' else 1 for x in range(COLS)]
             for y in range(ROWS)]
        for (y, x) in Q_PATH[:k + 1]:
            if (y, x) not in (Q_START, Q_GOAL):
                g[y][x] = 7
        im.set_data(g)
        label = (f"Q-learning agent 走第 {k + 1}/{len(Q_PATH) - 1} 步"
                 if k < len(Q_PATH) - 1 else
                 "Q-learning 學完：16 步 = BFS 最短")
        title.set_text(f"強化學習繞線：貪心走出最短路\n{label}")
    return []

frames = len(round_frames) + len(Q_PATH) + 1

from matplotlib.colors import ListedColormap
CMAP = ListedColormap(['#37474f', 'white', '#b0bec5', '#ef9a9a', '#90caf9',
                       '#a5d6a7', '#ffe082', '#b39ddb', '#ffab91', '#e53935'])
im = ax.imshow(ncr_base(), cmap=CMAP, vmin=0, vmax=9)
ncr_pins, q_pins = [], []
for (name, s, e) in NCR_NETS:
    for (p, cc) in [(s, '#1565c0'), (e, '#e53935')]:
        ncr_pins.append(ax.text(p[1], p[0], name, ha='center', va='center',
                                fontsize=10, color=cc))
for (lab, p, cc) in [('起', Q_START, '#1565c0'), ('訖', Q_GOAL, '#e53935')]:
    q_pins.append(ax.text(p[1], p[0], lab, ha='center', va='center',
                          fontsize=10, color=cc))
for t in q_pins:                  # PathFinder 階段先藏起 Q 的標記
    t.set_visible(False)

anim = FuncAnimation(fig, update, frames=frames, interval=600, repeat=True)
anim.save('5_ic_routing_modern.gif', writer=PillowWriter(fps=2))
print(f"PathFinder {len(round_frames)} 輪收斂 + Q 路徑 {len(Q_PATH) - 1} 步，"
      f"共 {frames} 幀，動畫已存成 5_ic_routing_modern.gif")

try:
    plt.show()
except Exception:
    pass
