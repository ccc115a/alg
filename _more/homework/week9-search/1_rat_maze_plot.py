#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 1（動畫）：老鼠走迷宮 — 用動畫看 DFS 怎麼「走到底、撞牆、回頭」
#
# 幾種顏色的意義：
#   灰底格子   = DFS 已探訪過（visited）的格子
#   綠色粗線   = 目前在手上的路徑（path 堆疊）
#   細紅線     = 最終找到的路徑（動畫結束定格）
#
# 執行：python3 1_rat_maze_plot.py
#      （動畫會存成 1_rat_maze.gif，映片視窗可即時觀看）

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
from _plot_common import setup_cjk

setup_cjk()

MAZE = [
    "#############",
    "#S#.......#.#",
    "#.#.#####.#.#",
    "#.#.#...#.#.#",
    "#...#.#.#.#.#",
    "#####.#.#.#.#",
    "#.....#.#...#",
    "#.#####.##.##",
    "#.#...#..#..#",
    "#.#.#.#.##..#",
    "#.#.#.#.#...#",
    "#...#...#...E",
    "#############",
]
ROWS, COLS = len(MAZE), len(MAZE[0])

def find(ch):
    for y in range(ROWS):
        for x in range(COLS):
            if MAZE[y][x] == ch:
                return (y, x)

start, goal = find('S'), find('E')
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ---------- 有「錄影」能力的 DFS ----------
visited, path = set(), []
frames = []          # 每個畫面 = (visited 快照, path 快照, 狀態文字)

def snapshot(label):
    frames.append((set(visited), list(path), label))

def dfs(y, x):
    visited.add((y, x))
    path.append((y, x))
    snapshot(f"走進 ({y},{x})，試過 {len(visited)} 格")
    if (y, x) == goal:
        snapshot(f"老鼠衝出力啦！到達出口 ({y},{x})")
        return True
    for dy, dx in DIRS:
        ny, nx = y + dy, x + dx
        if 0 <= ny < ROWS and 0 <= nx < COLS \
           and MAZE[ny][nx] != '#' and (ny, nx) not in visited:
            if dfs(ny, nx):
                return True
    path.pop()
    snapshot(f"({y},{x}) 是死路 → 回溯")
    return False

dfs(*start)

def base_grid():
    """把迷宮轉成等值網格：3=?牆 2=路 4=出口等其他狀態由 draw 堆上去"""
    g = [[0] * COLS for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if MAZE[y][x] == '#':
                g[y][x] = 0          # 牆
            else:
                g[y][x] = 1          # 可走
    return g

fig, ax = plt.subplots(figsize=(6, 6))
im = ax.imshow(base_grid(), cmap=ListedColormap(
    ['#222831', 'white', '#cfd8dc', '#4caf50', '#e53935']),
    vmin=0, vmax=4)
ax.set_xticks([]); ax.set_yticks([])
title = ax.set_title('DFS 老鼠走迷宮', fontsize=12)

def update(i):
    vis, pat, label = frames[i]
    g = base_grid()
    for (y, x) in vis:
        if (y, x) not in (start, goal) and g[y][x] == 1:
            g[y][x] = 2               # 已探過
    for (y, x) in pat:
        if (y, x) not in (start, goal):
            g[y][x] = 3               # 綠 = 現在的路徑
    im.set_data(g)
    title.set_text(f"DFS 老鼠走迷宮   第 {i} 步\n{label}")
    return [im, title]

anim = FuncAnimation(fig, update, frames=len(frames), interval=220, repeat=True)
anim.save('1_rat_maze.gif', writer=PillowWriter(fps=5))
print(f"共 {len(frames)} 幅畫面，動畫已存成 1_rat_maze.gif")

try:
    plt.show()
except Exception:
    pass
