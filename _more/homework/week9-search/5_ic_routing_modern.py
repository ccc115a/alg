#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 5（進階）：IC 繞線的「現代方法」與 SOTA 思想
#
# 5_ic_routing.py 已示範三種「單條 net 的格子搜尋」（Lee / Hadlock / A*）。
# 這一支補上真實 EDA 工具會用到的四種更高階做法：
#
#   方法 4：線搜尋 (Line Search, Soukup / Mikami-Tabuchi 思想)
#           - 狀態不再是「一格」，而是「一段直線」
#           - 一次前進一整段，轉彎次數少、開展快；但不保證最短路
#
#   方法 5：Steiner 樹拓撲（FLUTE 的核心思想，全域繞線 global routing 基礎）
#           - 多 pin net 不是兩兩連，而是連成一棵「總長最短的樹」
#           - Hanan 定理：最佳 RST 的 Steiner 點必落在
#             「pin 的 y 座標集合 × x 座標集合」構成的 Hanan grid 上
#           - 本程式在 3-pin 特例上精確窮舉（小規模可證明是最優解）
#
#   方法 6：可協商擠塞繞線 (Negotiated Congestion Routing，PathFinder 演算法)
#           - 多條 net 競爭容量有限的格子（晶片上 = metal track 數有限）
#           - 每一輪所有 net 都重繞一次；違反容量的格子每輪漲價
#           - 擠塞自己會被「談判」掉，像市場機制——這是 PathFinder (1995)
#             至今仍是 FPGA 繞線標準（VTR 的 AIR）的原因
#
#   方法 7：強化學習繞線（deep RL 的最小示意）
#           - 讓 agent 學「在每個格子往哪個方向走」的策略 (policy)
#           - 訓練完成後，繞一條 net 只需沿 policy 貪心行走 L 步
#             （A* 每次繞都要重新展開幾十格）
#           - 這是 DeepPR (ISPD'23)、PRNet、NeuralSteiner (NeurIPS'24)
#             等 RL 繞線研究的玩具版
#
# 執行：python3 5_ic_routing_modern.py

import heapq
import random
from collections import Counter, deque

# ---------- 共用格子圖 ----------
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
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]   # 上 下 左 右

def inside(y, x):
    return 0 <= y < ROWS and 0 <= x < COLS

def is_free(p):
    return GRID[p[0]][p[1]] == '.'

def bfs_dist(start, goal):
    """BFS 最短距離（當「標準答案」用）"""
    seen = {start: 0}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            return seen[cur]
        for dy, dx in DIRS:
            n = (cur[0] + dy, cur[1] + dx)
            if inside(*n) and is_free(n) and n not in seen:
                seen[n] = seen[cur] + 1
                q.append(n)
    return None

def dijkstra(start, goal, cost_fn, board=None):
    """邊權 = cost_fn(進入的格子) 的 Dijkstra；回傳 (路徑, 開展格數)
       board 預設用 GRID，NCR 部分會傳自己的底板进来"""
    grid = board if board is not None else GRID
    def free(p):
        return grid[p[0]][p[1]] == '.'
    g = {start: 0}
    parent = {start: None}
    pq = [(0, start)]
    expanded = 0
    while pq:
        d, cur = heapq.heappop(pq)
        if d > g[cur]:
            continue
        expanded += 1
        if cur == goal:
            path, at = [], cur
            while at:
                path.append(at); at = parent[at]
            return path[::-1], expanded
        y, x = cur
        for dy, dx in DIRS:
            n = (y + dy, x + dx)
            if inside(*n) and free(n):
                nd = d + cost_fn(n)
                if n not in g or nd < g[n]:
                    g[n] = nd
                    parent[n] = cur
                    heapq.heappush(pq, (nd, n))
    return None, expanded

# =========================================================
# 方法 4：線搜尋 (Line Search) —— 狀態 = 一整段直線
# =========================================================
def line_search(start, goal):
    """Soukup 型線搜尋：DFS，但以「整段直線」為開展單位。
       策略：方向依「朝目標更近」排序；直行時只在『距離遞減』時續走
       （= 貪心的線性推進）。不保證最短，但轉彎次數少、開展極快。
       cells = 開展的格子數；segs = 嘗試過的直線段數（≈ 轉彎次數）"""
    dist = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    visited = {start}
    path = [start]
    stats = {'cells': 1, 'segs': 0}

    def dfs(y, x):
        if (y, x) == goal:
            return True
        dirs = sorted(DIRS,
                      key=lambda d: dist((y + d[0], x + d[1])))
        for dy, dx in dirs:
            cy, cx, seg = y, x, []
            while True:
                ny, nx = cy + dy, cx + dx
                if not inside(ny, nx) or not is_free((ny, nx)) \
                   or (ny, nx) in visited:
                    break
                if seg and dist((ny, nx)) >= dist((cy, cx)):
                    break                                  # 續走不再更近 → 該轉彎了
                visited.add((ny, nx))
                path.append((ny, nx))
                seg.append((ny, nx))
                stats['cells'] += 1
                cy, cx = ny, nx
                if (cy, cx) == goal:
                    stats['segs'] += 1
                    return True
            if seg:
                stats['segs'] += 1
                if dfs(cy, cx):
                    return True
                for _ in seg:            # 回溯：撤掉整段
                    path.pop()
        return False

    if dfs(*start):
        return path, stats
    return None, stats

# =========================================================
# 方法 5：3-pin Steiner 樹（Hanan grid 精確窮舉 ＝ FLUTE 的思想）
# =========================================================
STEINER_BOARD = [['.'] * 9 for _ in range(8)]
PINS_3 = [(0, 0), (0, 8), (6, 4)]          # 三個接腳 (y, x)

def manh_mst(nodes):
    """完全圖（邊權 = 曼哈頓距離）上的 Kruskal MST。
       邊的方向若騎在行/列上，畫圖時是直線；否則畫成 L 形彎折。"""
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            edges.append((abs(a[0] - b[0]) + abs(a[1] - b[1]), i, j))
    edges.sort()
    par = list(range(len(nodes)))
    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    total, kept = 0, []
    for w, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            par[ri] = rj
            total += w
            kept.append((nodes[i], nodes[j], w))
    return total, kept

def steiner_3pin(pins):
    """窮舉 Hanan lattice 交點子集，找『總長最短的 Steiner 樹』。
       （Hanan 定理：此窮舉在 3-pin 時可找到精確最佳解）"""
    ys = sorted({p[0] for p in pins})
    xs = sorted({p[1] for p in pins})
    lattice = [(y, x) for y in ys for x in xs]
    best = None
    for mask in range(1 << len(lattice)):
        nodes = list(dict.fromkeys(tuple(pins) +
                     tuple(lattice[i] for i in range(len(lattice)) if mask >> i & 1)))
        total, edges = manh_mst(nodes)
        if best is None or total < best[0]:
            best = (total, nodes, edges)
    return best

def draw_steiner(pins, total, edges):
    b = [row[:] for row in STEINER_BOARD]
    pins_set = set(pins)
    steiners = set()
    for a, bnd, _ in edges:                 # 畫出每條邊（直線或 L 形）
        (ay, ax), (by, bx) = a, bnd
        def hline(y, x1, x2):
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                if b[y][x] == '.':
                    b[y][x] = '-'
        def vline(x, y1, y2):
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                if b[y][x] == '.':
                    b[y][x] = '|'
        if ay == by:                        # 水平直線
            hline(ay, ax, bx)
        elif ax == bx:                      # 垂直直線
            vline(ax, ay, by)
        else:                               # 其他 → 畫成 L 形（畫在中繼處折彎）
            vline(ax, ay, by)
            hline(by, ax, bx)
            if (by, ax) not in pins_set:
                steiners.add((by, ax))
        if a not in pins_set: steiners.add(a)
        if bnd not in pins_set: steiners.add(bnd)
    for (y, x) in steiners:
        b[y][x] = 'S'
    for (y, x) in pins:
        b[y][x] = 'P'
    for row in b:
        print(' '.join(row))
    print(f"  Steiner 樹總長 = {total}；使用的 Steiner 點 = {sorted(steiners)}")

# =========================================================
# 方法 6：可協商擠塞繞線 (PathFinder / Negotiated Congestion Routing)
# =========================================================
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
NCR_NETS = [                      # 四條 net 都得「穿牆」到右邊
    ('A', (0, 0), (0, 9)),
    ('B', (2, 0), (2, 9)),
    ('C', (4, 0), (4, 9)),
    ('D', (6, 0), (6, 9)),
]
# 容量模型：每格預設 2（＝par上下兩層金屬各一條 track）
CAP = {(y, x): 2 for y in range(8) for x in range(10) if GRID_C[y][x] == '.'}

def ncr_route(max_rounds=40):
    """PathFinder 式迭代：
       第 1 輪：所有 net 都「不知道別人存在」，各自走自己的最短路 → 必然超載
       第 2 輪起：逐條重繞；成本 = 1 + 即時擠塞(p_fac×別人次數) + 歷史擠塞
       超過容量的格子每輪漲價（留下「吵架紀錄」），談判收斂到合法解"""
    cur = {}                     # 每條 net 目前的路徑
    history = Counter()          # 每格的擠塞歷史
    p_fac = 1.0                  # 本輪「即時擠塞」懲罰係數，逐輪加倍
    demand = Counter()
    for rnd in range(1, max_rounds + 1):
        # 第一輪：純最短路（未談判）
        for name, start, goal in NCR_NETS:
            if rnd == 1:
                path, _ = dijkstra(start, goal, lambda c: 1, board=GRID_C)
                cur[name] = path
                demand.update(path)
            else:
                # 逐條協商：先把自己這條撤下，重算成本，再建回去
                for c in cur[name]:
                    demand[c] -= 1
                def cost(c):
                    others = demand[c]           # 別人在這格的次數
                    return 1 + p_fac * others + history[c]
                path, _ = dijkstra(start, goal, cost, board=GRID_C)
                cur[name] = path
                demand.update(path)
        overflow = {c: demand[c] - CAP[c] for c in demand
                    if demand[c] > CAP[c]}
        print(f"  第 {rnd} 輪：超載格數 = {len(overflow)}  超載格子 = {sorted(overflow)}")
        if not overflow:
            return {n: (n, p, None) for n, p in cur.items()}, rnd
        for c in overflow:
            history[c] += demand[c] - CAP[c]
        p_fac *= 2               # 即時擠塞懲罰逐輪加倍（PathFinder 的 p_fac）
    return None, None

def draw_ncr(routes):
    b = [list(row) for row in GRID_C]
    sym = {'A': '1', 'B': '2', 'C': '3', 'D': '4'}
    cell_users = {}
    for name, path, _ in routes.values():
        for (y, x) in path:
            if GRID_C[y][x] == '.':
                cell_users.setdefault((y, x), []).append(sym[name])
    for (y, x), s in cell_users.items():
        b[y][x] = '*' if len(s) > 1 else s[0]   # 共用格（還有容量）畫成 *
    for name, start, goal in NCR_NETS:
        b[start[0]][start[1]] = name
        b[goal[0]][goal[1]] = name
    for row in b:
        print(' '.join(row))
    print("  （* = 兩條 net 共用的格子——擠塞被談判掉，不超過容量）")

# =========================================================
# 方法 7：強化學習繞線（表格式 Q-learning 的最小示意）
# =========================================================
def q_learn_route(start, goal, episodes=600, seed=1):
    random.seed(seed)
    acts = DIRS
    Q = {}                      # Q[(state, action_index)] = 預期報酬
    alpha, gamma = 0.5, 0.98    # 學習率 / 折扣
    total_steps = 0
    for ep in range(episodes):
        eps = max(0.05, 1.0 - ep / max(1, episodes - 50))   # ε 衰減
        s = start
        for _ in range(120):                     # 單一 episode 步數上限
            total_steps += 1
            a = random.randrange(4) if random.random() < eps \
                else max(range(4), key=lambda i: Q.get((s, i), 0.0))
            ny, nx = s[0] + acts[a][0], s[1] + acts[a][1]
            if not inside(ny, nx) or not is_free((ny, nx)):
                s2, r, done = s, -1, False       # 撞牆：留原地，負報酬
            else:
                s2, done = (ny, nx), (ny, nx) == goal
                r = 0 if done else -1            # 每走一步扣 1 分
            q_next = max(Q.get((s2, i), 0.0) for i in range(4)) if not done else 0.0
            Q[(s, a)] = Q.get((s, a), 0.0) + alpha * (r + gamma * q_next
                                                       - Q.get((s, a), 0.0))
            s = s2
            if done:
                break
    # 訓練完：貪心行走 (greedy rollout)
    path, s, seen = [start], start, {start}
    for _ in range(80):
        a = max(range(4), key=lambda i: Q.get((s, i), float('-inf')))
        s = (s[0] + acts[a][0], s[1] + acts[a][1])
        path.append(s)
        if s == goal:
            break
        if s in seen:                        # 學壞了繞圈圈 → 根本沒學會
            return path, total_steps, False
        seen.add(s)
    return path, total_steps, s == goal

def draw_route(path, tag):
    b = [list(row) for row in GRID]
    for (y, x) in path:
        if b[y][x] == '.':
            b[y][x] = tag
    for row in b:
        print(''.join(row))

if __name__ == '__main__':
    print("=== IC 繞線：現代方法（線搜尋 / Steiner 樹 / PathFinder / Q-learning） ===\n")

    print("--- 方法 4：線搜尋 (Line Search) —— net (0,0) -> (5,2) ---")
    path, st = line_search((0, 0), (5, 2))
    print(f"  線長 = {len(path) - 1}（BFS 最短 = {bfs_dist((0,0),(5,2))}），"
          f"開展 {st['cells']} 格，嘗試 {st['segs']} 段直線：")
    draw_route(path, '*')

    print("\n--- 方法 5：3-pin Steiner 樹（FLUTE 的思想） ---")
    total, nodes, edges = steiner_3pin(PINS_3)
    mst_only, _ = manh_mst(list(PINS_3))
    print(f"  只用 MST 互連 3 個 pin：總長 = {mst_only}")
    draw_steiner(PINS_3, total, edges)
    print(f"  → 加進 Steiner 點後省了 {mst_only - total}（"
          f"{(mst_only - total) / mst_only:.0%}）的總線長！")

    print("\n--- 方法 6：可協商擠塞繞線 (PathFinder) ---")
    routes, rounds = ncr_route()
    if rounds is not None:
        print(f"  迭代 {rounds} 輪後收斂（超載 = 0），最終佈局：")
    else:
        print("  達到迭代上限仍未能把超載降到 0！")
    draw_ncr(routes)

    print("\n--- 方法 7：強化學習繞線 (Q-learning) —— net (7,0) -> (0,9) ---")
    path, steps, ok = q_learn_route((7, 0), (0, 9))
    print(f"  訓練 {600} episodes（共 {steps} 次走步）後，貪心策略走出的路：")
    draw_route(path, 'Q')
    best = bfs_dist((7, 0), (0, 9))
    print(f"  學到的路徑長 = {len(path) - 1} 步；BFS 標準答案 = {best} 步"
          f"  （{'已達最短' if len(path) - 1 == best else '尚未收斂'}）")
