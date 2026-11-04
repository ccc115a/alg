#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 4（動畫）：NPC 用 A* 搜尋玩家 — 看「f 最小的格子先開展」的過程
#
#   白格   = 還沒被碰過
#   黃格   = 在 frontier 上（排隊等著開展，f = g+h 的值畫acy在旁邊）
#   藍格   = 已開展（closed）
#   紅框   = 這一刻正在開展的格子
#   綠線   = 找到的最短路徑（結尾亮起）
#
# 執行：python3 4_npc_astar_plot.py

import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from _plot_common import setup_cjk
setup_cjk()

MAP = [
    "#############",
    "#N...#......#",
    "#.#.#.#.####.",
    "#.#...#..#..#",
    "#.#####..#..#",
    "#.......#...#",
    "#.#####.#####",
    "#.#...#.....#",
    "#.#.#.#####.#",
    "#...#.....#.P",
    "#############",
]
ROWS, COLS = len(MAP), len(MAP[0])
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def find(ch):
    for y in range(ROWS):
        for x in range(COLS):
            if MAP[y][x] == ch:
                return (y, x)
NPC, PLAYER = find('N'), find('P')

def h(p):
    return abs(p[0] - PLAYER[0]) + abs(p[1] - PLAYER[1])

# ---------- 有錄影功能的 A* ----------
g_best = {NPC: 0}
parent = {NPC: None}
pop_order = []               # 開展順序 (cell, f, h, g以...不，g 值)
cur = NPC
pq = [(h(NPC), NPC)]
while pq:
    f, c = heapq.heappop(pq)
    if f > g_best[c] + h(c):        # 過期的舊條目
        continue
    pop_order.append((c, f, g_best[c]))
    cur = c
    if c == PLAYER:
        break
    for dy, dx in DIRS:
        n = (c[0] + dy, c[1] + dx)
        if 0 <= n[0] < ROWS and 0 <= n[1] < COLS and MAP[n[0]][n[1]] != '#':
            g_new = g_best[cur] + 1
            if n not in g_best or g_new < g_best[n]:
                g_best[n] = g_new
                parent[n] = cur
                heapq.heappush(pq, (g_new + h(n), n))

path, at = [], PLAYER
while at is not None:
    path.append(at); at = parent[at]
path = path[::-1]

pop_set = {c for c, _, _ in pop_order}

# ---------- 動畫 ----------
fig, ax = plt.subplots(figsize=(6.4, 5.6))
ax.set_xticks([]); ax.set_yticks([])
title = ax.set_title('A* 搜尋玩家', fontsize=12)

def base():
    g = [[0] * COLS for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            g[y][x] = 0 if MAP[y][x] == '#' else 1
    return g

def update(i):
    g = base()
    # 已開展（closed）的格子 = pop 次序在前面的
    upto = pop_order[:i + 1]
    for c, f, gval in upto[:-1]:
        if c not in (NPC, PLAYER):
            g[c[0]][c[1]] = 2
    # 還沒被開展、但已進 frontier 的格子 = 黃
    frontier = [c for c in g_best
                if c not in {p[0] for p in upto} and MAP[c[0]][c[1]] != '#']
    for (y, x) in frontier:
        if g[y][x] == 1:
            g[y][x] = 3
    if i < len(pop_order):
        cy, cx = pop_order[i][0]
        if g[cy][cx] >= 1:
            g[cy][cx] = 4
    # 最後亮路徑
    if i >= len(pop_order):
        for (y, x) in path:
            if (y, x) not in (NPC, PLAYER):
                g[y][x] = 5
    im.set_data(g)
    show = upto[-1] if i < len(pop_order) else None
    if show:
        c, f, gval = show
        label = f"開展 {c}: g={gval}, h={h(c)}, f=g+h={f}"
    else:
        label = f"找到最短路！長度 = {len(path) - 1} 步，共開展 {len(pop_order)} 格"
    title.set_text(f"A* 搜尋玩家 (NPC → 玩家)\n{label}")
    return []

from matplotlib.colors import ListedColormap
from matplotlib.image import AxesImage
im = ax.imshow(base(), cmap=ListedColormap(
    ['#263238', 'white', '#90caf9', '#fff59d', '#1565c0', '#66bb6a']),
    vmin=0, vmax=5)
# N 的位置重畫一次字元
ax.text(NPC[1], NPC[0], 'N', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#1565c0')
ax.text(PLAYER[1], PLAYER[0], 'P', ha='center', va='center',
        fontsize=11, fontweight='bold', color='#e53935')

frames = len(pop_order) + 1
anim = FuncAnimation(fig, update, frames=frames, interval=150, repeat=True)
anim.save('4_npc_astar.gif', writer=PillowWriter(fps=7))
print(f"A* 開展 {len(pop_order)} 格、路徑 {len(path) - 1} 步，"
      f"動畫已存成 4_npc_astar.gif")

try:
    plt.show()
except Exception:
    pass
