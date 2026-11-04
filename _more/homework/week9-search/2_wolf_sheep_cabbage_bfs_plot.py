#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 2（動畫）：狼羊菜過河 — 看 BFS 一層一層把 16 個狀態「染開來」
#
# 畫面：4x4 格子 = 全部 16 個渡河狀態，狀態編號 = (農夫,狼,羊,菜) 的四位元
#   黑格     = 非法狀態（農夫不在時羊狼或羊菜同岸）
#   白格     = 還沒被 BFS 發現的狀態
#   藍色深淺 = 該狀態被發現的「層數」（=步數；越早發現步數越少）
#   紅格     = 目標狀態 (1,1,1,1)
#   紅色外框 = 解法路徑上的狀態（動畫結尾亮起）
#
# 執行：python3 2_wolf_sheep_cabbage_bfs_plot.py

import collections
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from _plot_common import setup_cjk
setup_cjk()

START, GOAL = (0, 0, 0, 0), (1, 1, 1, 1)

def unsafe(s):
    f, w, sh, c = s
    return f != sh and (sh == w or sh == c)

def idx(s):
    return s[0] * 8 + s[1] * 4 + s[2] * 2 + s[3]

# ---------- 有錄影功能的 BFS ----------
discovered = []                      # 依「被展開」順序的 (狀態, 層數)
parent = {START: None}
level = {START: 0}
frontier = collections.deque([START])
while frontier:
    s = frontier.popleft()
    discovered.append((s, level[s]))
    if s == GOAL:
        break
    f = s[0]
    for pas in [None] + [i for i in range(1, 4) if s[i] == f]:
        t = list(s)
        t[0] = 1 - f
        if pas is not None:
            t[pas] = 1 - f
        t = tuple(t)
        if t not in parent and not unsafe(t):
            parent[t] = s
            level[t] = level[s] + 1
            frontier.append(t)

final = []
at = GOAL
while at is not None:
    final.append(at)
    at = parent[at]
final = final[::-1]

# ---------- 動畫 ----------
LEVEL_COLORS = ['#cfd8dc', '#b0bec5', '#90a4ae', '#7796b5', '#5c8ac5', '#4472a8']
STATES = [(f, w, s, c) for f in range(2) for w in range(2)
          for s in range(2) for c in range(2)]
IFMT = lambda s: ''.join(str(b) for b in s)

fig, ax = plt.subplots(figsize=(6.4, 6.4))
ax.set_xlim(-0.5, 7.5); ax.set_ylim(-0.5, 3.5)
ax.set_xticks(range(8)); ax.set_yticks(range(4))
ax.set_xticklabels([]); ax.set_yticklabels([])
ax.tick_params(length=0)
ax.set_xlabel('狀態按位元編號順序：(農夫,狼,羊,菜) 共 4x4 = 16 個', fontsize=9)
title = ax.set_title('狼羊菜過河：BFS 層層擴散', fontsize=12)

cells = {}
for s in STATES:
    k = idx(s)
    edge = 'none'
    if unsafe(s):
        face = '#1a1a1a'
    else:
        face = 'white'
    r, c = divmod(k, 4)
    rect = plt.Rectangle((c - 0.5, r - 0.5), 1, 1,
                         facecolor=face, edgecolor=edge, lw=2)
    ax.add_patch(rect)
    cells[k] = rect
    t = ax.text(c, r, IFMT(s), ha='center', va='center', fontsize=11,
                color='white' if unsafe(s) else '#455a64')
    if unsafe(s):
        t.set_text('×')

def update(i):
    seen = discovered[:max(0, i)]      # 前 i 個已被展開的狀態
    latest = discovered[i][0] if i < len(discovered) else None
    for s in STATES:
        k = idx(s)
        rect = cells[k]
        if unsafe(s):
            rect.set_facecolor('#1a1a1a')
            rect.set_edgecolor('none')
        elif i == len(discovered):      # 結尾畫面：亮出整條解徑
            if s in [p for p in final]:
                rect.set_facecolor(LEVEL_COLORS[min(level[s], 5)])
                rect.set_edgecolor('#d50000')
            else:
                rect.set_facecolor('white')
                rect.set_edgecolor('none')
        elif any(s == d[0] for d in seen) or s == START and i >= 0:
            lv = next(l for d, l in discovered if l == level[s] and d == s)
            rect.set_facecolor(LEVEL_COLORS[min(lv, 5)])
            lw = 3.5 if s == latest else 2
            rect.set_edgecolor('#ff6d00' if s == latest else 'none')
            if s == latest:
                rect.set_edgecolor('#ff6d00'); rect.set_facecolor('#ff8a30')
        else:
            rect.set_facecolor('white')
            rect.set_edgecolor('none')
    if latest is not None:
        label = f"展開 {IFMT(latest)}（第 {level[latest]} 層）"
    else:
        label = "結尾：解徑上的狀態以紅框亮出（最少 7 次渡河）"
    title.set_text(f"狼羊菜過河：BFS 層層擴散\n{label}")
    return []

steps = len(discovered) + 1
anim = FuncAnimation(fig, update, frames=steps, interval=700, repeat=True)
anim.save('2_wolf_sheep_cabbage_bfs.gif', writer=PillowWriter(fps=2))
print(f"共 {len(discovered)} 個被展開的狀態、最少 {len(final) - 1} 次渡河，"
      f"動畫已存成 2_wolf_sheep_cabbage_bfs.gif")

try:
    plt.show()
except Exception:
    pass
