#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 5：IC 設計中的電路繞線問題（多種搜尋法）
#
# 問題：晶片內部的金屬層可以想成一張二維格子圖 (grid)，
#       每一個格子叫一個 "leave cell"。繞線 (routing) 就是把幾組
#       「接腳 → 接腳」(net) 各用一條不互相重疊的路徑連起來。
#
# 這是一張二維格子，多條 net 要繞，互不相交 → 用「逐條繞 + 剪枝」的策略：
#
#   方法 1：Lee 演算法（BFS 迷宮繞線 / maze routing，1961）
#           - 從起點像水波一樣一圈圈往外淹 (wavefront)
#           - 碰到目標點後回溯 → 得到「最短路徑」
#           - 優點：一定找得到（若存在）、路徑最佳；缺點：慢（會淹爆全圖）
#
#   方法 2：Hadlock 演算法（BFS + detour number 的 0-1 加權版本）
#           - 每個格子成本 = 到目前為止「逆著目標多繞的格數 (detour)」
#           - 用 deque：直行成本 0 排前頭、轉彎成本 1 排尾端（= 0/1 BFS）
#           - 比純 Lee 少展開很多格子，路徑長度仍然最短
#
#   方法 3：A* 繞線（演化版 Lee 演算法，現在工業工具的基礎）
#           - f(n) = g(n) + h(n)，h 用曼哈頓距離
#           - 有方向性地拓展 → 又比 Hadlock 更聚焦
#
#   額外的工程技巧（真實工具其實還會用）：
#           - 逐條繞線 (net ordering)：一條一條繞，先繞的畫格就變成障礙
#           - 擋牆 (blockage)：被佔用的格子標成 '#'
#           - 佳成本 (cost layer)... 總之都是「搜尋 + 剪枝 + 依序繪製」的心法
#
# 執行：python3 5_ic_routing.py

import heapq
from collections import deque

# 晶片格子：'#' = 已被佔用的障礙（其他 net / macro），'.' = 可繞線
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

A = ((0, 0), (5, 2))   # net 1：左上角 接腳 -> 中左 接腳
B = ((0, 9), (5, 7))   # net 2：右上角 接腳 -> 中右 接腳
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
ROWS, COLS = len(GRID), len(GRID[0])

def lee_bfs(start, goal, blocked):
    """方法 1：Lee 演算法（BFS 水波式）。回傳最短路徑."""
    parent = {start: None}
    frontier = deque([start])
    expanded = 0
    while frontier:
        cur = frontier.popleft()
        expanded += 1
        if cur == goal:
            path, at = [], cur
            while at:
                path.append(at); at = parent[at]
            return path[::-1], expanded
        for dy, dx in DIRS:
            n = (cur[0] + dy, cur[1] + dx)
            if 0 <= n[0] < ROWS and 0 <= n[1] < COLS \
               and n not in parent and GRID[n[0]][n[1]] == '.' and n not in blocked:
                parent[n] = cur
                frontier.append(n)
    return None, expanded

def hadlock(start, goal, blocked):
    """方法 2：Hadlock 演算法（0/1 BFS + detour number 計數）"""
    # deque 中放 (detour 數, 座標)：小的先 pop
    detour = {start: 0}
    parent = {start: None}
    frontier = deque([(0, start)])
    expanded = 0
    while frontier:
        d, cur = frontier.popleft()
        expanded += 1
        if cur == goal:
            path, at = [], cur
            while at:
                path.append(at); at = parent[at]
            return path[::-1], expanded
        y, x = cur
        for dy, dx in DIRS:
            n = (y + dy, x + dx)
            if not (0 <= n[0] < ROWS and 0 <= n[1] < COLS) or n in detour:
                continue
            if GRID[n[0]][n[1]] == '.' and n not in blocked:
                # 往「靠近目標」方向 = detour 不增加（成本 0，排前頭）
                # 逆著目標方向     = detour + 1  （成本 1，排後頭）
                away = abs(n[0] - goal[0]) + abs(n[1] - goal[1]) \
                       > abs(cur[0] - goal[0]) + abs(cur[1] - goal[1])
                nd = d + (1 if away else 0)
                detour[n] = nd
                parent[n] = cur
                if away:
                    frontier.append((nd, n))
                else:
                    frontier.appendleft((nd, n))
    return None, expanded

def astar_route(start, goal, blocked):
    """方法 3：A* 繞線。回傳最短路徑."""
    g_best = {start: 0}
    parent = {start: None}
    frontier = [(0, 0, start)]   # (f, g, 座標)
    expanded = 0
    while frontier:
        _, g, cur = heapq.heappop(frontier)
        expanded += 1
        if cur == goal:
            path, at = [], cur
            while at:
                path.append(at); at = parent[at]
            return path[::-1], expanded
        y, x = cur
        for dy, dx in DIRS:
            n = (y + dy, x + dx)
            if not (0 <= n[0] < ROWS and 0 <= n[1] < COLS) or GRID[n[0]][n[1]] == '#':
                continue
            g_new = g + 1
            if n in g_best and g_best[n] <= g_new:
                continue
            if n in blocked:
                continue
            g_best[n] = g_new
            parent[n] = cur
            h = abs(n[0] - goal[0]) + abs(n[1] - goal[1])
            heapq.heappush(frontier, (g_new + h, g_new, n))
    return None, expanded

def draw(routed):
    """把每條 net 畫上不同的字元（1/2），接腳用大寫 A/B 標記"""
    board = [list(row) for row in GRID]
    sym = ['1', '2']
    for k, (path, _) in enumerate(routed):
        for y, x in path:
            if board[y][x] == '.':
                board[y][x] = sym[k]
    board[A[0][0]][A[0][1]] = board[A[1][0]][A[1][1]] = 'A'
    board[B[0][0]][B[0][1]] = board[B[1][0]][B[1][1]] = 'B'
    for row in board:
        print(' '.join(row))

def route(method, name, nets):
    """逐條繞線 (net-by-net)：已繞的格子除「其他 net 的接腳」外通通封鎖"""
    print(f"\n--- {name} ---")
    total_expanded = 0
    routed = []
    blocked = set()
    for i, (s, g) in enumerate(nets):
        if method == 'lee':
            path, expanded = lee_bfs(s, g, blocked)
        elif method == 'hadlock':
            path, expanded = hadlock(s, g, blocked)
        else:
            path, expanded = astar_route(s, g, blocked)
        total_expanded += expanded
        if path is None:
            print(f"  net {s} -> {g} 繞不通！（被先繞的 net 擋死了）")
            return
        routed.append((path, expanded))
        print(f"  net {s} -> {g}  長度 = {len(path) - 1}，開展 {expanded} 格")
        blocked |= set(path)          # 通通封鎖
        blocked -= other_pins(nets, i)  # 但其他 net 的接腳要保留
    draw(routed)
    print(f"  （{name} 兩條 net 合計開展 {total_expanded} 格）")

def other_pins(nets, skip):
    """還沒繞到的 net 的接腳不能被封鎖"""
    out = set()
    for j, (s, g) in enumerate(nets):
        if j != skip:
            out |= {s, g}
    return out

if __name__ == '__main__':
    print("=== IC 電路繞線：Lee / Hadlock / A* ===")
    print("原始格子圖（# = 佔用障礙）：")
    draw([])
    nets = [A, B]
    route('lee', '方法 1：Lee 演算法（BFS 水波繞線）', nets)
    route('hadlock', '方法 2：Hadlock 演算法（detour 0/1 BFS）', nets)
    route('astar', '方法 3：A* 繞線（g + 曼哈頓 h）', nets)
