#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 3（動畫）：八皇后 — 看 DFS + 剪枝怎麼「放皇后、衝突、拿掉重試」
#
#   綠底 = 已放好的皇后（目前路徑上）
#   紅叉 = 剪枝偵測到的衝突格（這一刻該格被擋掉）
#   灰底 = 歷史探索過仍回溯掉的列
#   動畫結尾 = 第一組解逕行定格，並注明 DFS 窮舉出 92 組解
#
# 執行：python3 3_nqueens_plot.py

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from _plot_common import setup_cjk
setup_cjk()

N = 8

# ---------- 有錄影功能的 DFS + 剪枝 ----------
queens = []
frames = []          # (row, col, 放/撤/衝突)
solutions = []

def conflict(row, col):
    for r, c in enumerate(queens):
        if c == col or abs(r - row) == abs(c - col):
            return True
    return False

def dfs(row=0):
    if row == N:
        solutions.append(queens[:])
        frames.append(('sol', None, None))
        if len(solutions) == 1:      # 第一組解後就不再展開（動畫到此定格即可）
            raise StopIteration
        return
    for col in range(N):
        if conflict(row, col):
            frames.append(('conflict', row, col))
            continue
        frames.append(('place', row, col))
        queens.append(col)
        dfs(row + 1)
        frames.append(('remove', row, col))
        queens.pop()

try:
    dfs()
except StopIteration:
    pass

first_solution = solutions[0]
frames = frames[:[k for k, _, _ in frames].index('sol') + 1]  # 動畫只播到第一組解

# 動畫結束後再安靜地把全部解數完（演示回溯窮舉完整性）
def count_all():
    sols = []
    q = []
    def dfs_all(row):
        if row == N:
            sols.append(q[:])
            return
        for col in range(N):
            ok = all(q[i] != col and abs(i - row) != abs(q[i] - col)
                     for i in range(row))
            if ok:
                q.append(col)
                dfs_all(row + 1)
                q.pop()
    dfs_all(0)
    return sols

all_solutions = count_all()

# ---------- 動畫 ----------
fig, ax = plt.subplots(figsize=(6, 6))
title = ax.set_title('八皇后：DFS + 剪枝回溯', fontsize=13)
ax.set_xlim(-0.5, N - 0.5); ax.set_ylim(N - 0.5, -0.5)
ax.set_xticks(range(N)); ax.set_yticks(range(N))
ax.set_xticklabels([]); ax.set_yticklabels([]); ax.tick_params(length=0)
for x in range(N):
    for y in range(N):
        face = '#f5f5f5' if (x + y) % 2 == 0 else '#e0e0e0'
        ax.add_patch(plt.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                   facecolor=face, edgecolor='none'))
SQ = '♛'

# 877 步太多，存 gif 時每 STEP 步取一幀（互動播放仍可全速）
STEP = 6
seq = list(range(0, len(frames), STEP))
if seq[-1] != len(frames) - 1:
    seq.append(len(frames) - 1)

def update(j):
    kind, row, col = frames[seq[j]]
    for t in list(ax.texts):
        t.remove()
    # 重播到 seq[j] 時，目前的皇后在哪
    cur = []
    for m in range(seq[j] + 1):
        k, r, c = frames[m]
        if k == 'place':
            cur.append((r, c))
        elif k == 'remove' and cur:
            cur.pop()
    for r, c in cur:
        ax.text(c, r, SQ, ha='center', va='center', fontsize=22,
                color='#43a047')
    if kind == 'conflict':
        ax.text(col, row, '✕', ha='center', va='center',
                fontsize=18, color='#e53935')
        label = f"第 {row} 列第 {col} 行被前面皇后攻擊 → 剪枝跳過"
    elif kind == 'place':
        label = f"第 {row} 列皇后放在第 {col} 行（已有 {len(cur)} 個皇后）"
    elif kind == 'remove':
        label = f"第 {row} 列回溯（撤掉皇后），目前已展開 {seq[j]} 步"
    else:
        label = "找到第一組解！（動畫結束後程式繼續窮舉到 92 組）"
    title.set_text(f"八皇后：DFS + 剪枝回溯\n{label}")
    return []

anim = FuncAnimation(fig, update, frames=len(seq), interval=120, repeat=True)
anim.save('3_nqueens.gif', writer=PillowWriter(fps=10))
print(f"原始搜尋 {len(frames)} 步（動畫抽樣 {len(seq)} 幀）、"
      f"窮舉共 {len(all_solutions)} 組解，動畫已存成 3_nqueens.gif")

try:
    plt.show()
except Exception:
    pass
