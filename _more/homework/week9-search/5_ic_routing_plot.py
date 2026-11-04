#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 5（動畫）：IC 繞線 — 三種格子搜尋（Lee / Hadlock / A*）輪流上場
#
#   深色底 = 格已佔用（#）
#   亮→暗色階 = 開展的先後順序（波前演進的痕跡）
#   紅框 = 這一刻正在彈出/開展的格子
#   綠線 = 該方法最後找到的最短繞線
#
# 執行：python3 5_ic_routing_plot.py

import heapq
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
from _plot_common import setup_cjk
setup_cjk()

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
ROWS, COLS = len(GRID), len(GRID[0])
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
START, GOAL = (0, 0), (5, 2)

def free(p):
    return 0 <= p[0] < ROWS and 0 <= p[1] < COLS and GRID[p[0]][p[1]] == '.'

def rebuild(parent, cur):
    out = []
    while cur is not None:
        out.append(cur); cur = parent[cur]
    return out[::-1]

def lee():
    parent = {START: None}
    q = deque([START])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        if cur == GOAL:
            break
        for dy, dx in DIRS:
            n = (cur[0] + dy, cur[1] + dx)
            if free(n) and n not in parent:
                parent[n] = cur
                q.append(n)
    return order, rebuild(parent, GOAL)

def hadlock():
    parent = {START: None}
    detour = {START: 0}
    dq = deque([(0, START)])
    order = []
    while dq:
        d, cur = dq.popleft()
        order.append(cur)
        if cur == GOAL:
            break
        for dy, dx in DIRS:
            n = (cur[0] + dy, cur[1] + dx)
            if not free(n) or n in detour:
                continue
            away = abs(n[0] - GOAL[0]) + abs(n[1] - GOAL[1]) > \
                   abs(cur[0] - GOAL[0]) + abs(cur[1] - GOAL[1])
            nd = d + (1 if away else 0)
            detour[n] = nd
            parent[n] = cur
            if away:
                dq.append((nd, n))
            else:
                dq.appendleft((nd, n))
    return order, rebuild(parent, GOAL)

def astar():
    def h(p):
        return abs(p[0] - GOAL[0]) + abs(p[1] - GOAL[1])
    g = {START: 0}
    parent = {START: None}
    pq = [(h(START), START)]
    order = []
    while pq:
        f, cur = heapq.heappop(pq)
        if f > g[cur] + h(cur):
            continue
        order.append(cur)
        if cur == GOAL:
            break
        for dy, dx in DIRS:
            n = (cur[0] + dy, cur[1] + dx)
            if free(n):
                gn = g[cur] + 1
                if n not in g or gn < g[n]:
                    g[n] = gn
                    parent[n] = cur
                    heapq.heappush(pq, (gn + h(n), n))
    return order, rebuild(parent, GOAL)

METHODS = [('Lee (BFS 水波)', lee()),
           ('Hadlock (detour 0/1 BFS)', hadlock()),
           ('A* (g + h)', astar())]

# ---------- 動畫 ----------
fig, ax = plt.subplots(figsize=(6.4, 5.6))
ax.set_xticks([]); ax.set_yticks([])
title = ax.set_title('IC 繞線：三種搜尋法的波前', fontsize=12)

def base():
    g = [[0 if GRID[y][x] == '#' else 1 for x in range(COLS)]
         for y in range(ROWS)]
    return g

def update(frame_no):
    # frame -> (method_index, step)
    seq = []
    for mi, (name, (order, path)) in enumerate(METHODS):
        for st in range(len(order)):
            seq.append((mi, st))
        seq.append((mi, -1))          # -1 = 該方法的完結畫面（亮路徑）
    if frame_no >= len(seq):
        return
    mi, st = seq[frame_no]
    name, (order, path) = METHODS[mi]
    g = base()
    upto = order[:st + 1] if st >= 0 else order
    for k, c in enumerate(upto):
        if c in (START, GOAL):
            continue
        g[c[0]][c[1]] = 2 + min(k, 6)
    if st >= 0:                       # 紅框 = 正在彈出的格子
        c = order[st]
        g[c[0]][c[1]] = 9
    else:                             # 完結：亮出最終路徑
        for (y, x) in path:
            if (y, x) not in (START, GOAL):
                g[y][x] = 8
    im.set_data(g)
    extra = (f"步數 {st + 1}/{len(order)}, 已開展 {min(st + 1, len(order))} 格"
             if st >= 0 else
             f"完成！找到長度 {len(path) - 1} 的最短繞線")
    title.set_text(f"{name}\n{extra}")
    return []

from matplotlib.colors import ListedColormap
CMAP = ListedColormap(['#37474f', 'white', '#80deea', '#4dd0e1', '#26c6da',
                       '#00acc1', '#0097a7', '#00838f', '#66bb6a', '#e53935'])
im = ax.imshow(base(), cmap=CMAP, vmin=0, vmax=9)
ax.text(START[1], START[0], 'S', ha='center', va='center', fontsize=10,
        fontweight='bold', color='#0097a7')
ax.text(GOAL[1], GOAL[0], 'G', ha='center', va='center', fontsize=10,
        fontweight='bold', color='#0097a7')

seq_len = sum(len(p[1][0]) + 1 for p in METHODS)
anim = FuncAnimation(fig, update, frames=seq_len, interval=100, repeat=True)
anim.save('5_ic_routing.gif', writer=PillowWriter(fps=10))
print(f"三種方法開展格數 = " +
      ", ".join(f"{n}: {len(p[0])}" for n, p in METHODS) +
      f"，共 {seq_len} 幀，動畫已存成 5_ic_routing.gif")

try:
    plt.show()
except Exception:
    pass
