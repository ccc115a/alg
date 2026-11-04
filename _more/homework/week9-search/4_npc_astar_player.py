#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 4：NPC 搜尋玩家問題（A* 演算法）
#
# 問題：遊戲地圖上有一個 NPC（怪物 boss）和一個玩家（player）。
#       NPC 要穿過障礙物，用最少的步數走到玩家所在的位置。
#       這是遊戲 AI 中最典型的「尋路 (pathfinding)」問題。
#
# 搜尋法分析（A* = BFS 的聰明版，加了「方向感」）：
#   狀態        = 座標 (y, x)
#   開展        = 上下左右鄰居（不可穿牆）
#   g(n)        = 從起點走到 n 的實際步數
#   h(n)        = 啟發函數：n 到玩家的曼哈頓距離 |dy| + |dx|
#                 （可通行網格上永遠不會高估 → 保守 → 保證最短路）
#   f(n) = g(n) + h(n)   完整估計；每次挑 f 最小的節點開展
#   開放佇列     = priority queue（依 f 排序）
#   對照         :
#                 DFS → 盲目往深走      可能繞遠路
#                 BFS → 一層層擴散      保證最短但幾乎全地圖都跑過
#                 A*  → 朝目標方向優先 少跑很多格且仍保證最短
#
# 執行：python3 4_npc_astar_player.py

import heapq

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

def find(ch):
    for y in range(ROWS):
        for x in range(COLS):
            if MAP[y][x] == ch:
                return (y, x)

NPC, PLAYER = find('N'), find('P')
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def h(pos):
    """啟發函數：曼哈頓距離（網格可通行時必為真實成本的保守估計）"""
    return abs(pos[0] - PLAYER[0]) + abs(pos[1] - PLAYER[1])

def astar():
    """A* 搜尋：回傳 (路徑, 開展過的格數)"""
    frontier = [(h(NPC), NPC)]        # heapq 存 (f(n), 座標)
    g_best = {NPC: 0}                 # 到目前為止各點的最佳 g 值
    parent = {NPC: None}              # 前驅表 → 重建路徑
    expanded = 0

    while frontier:
        f, cur = heapq.heappop(frontier)   # 挑 f 最小的先開展
        expanded += 1
        if cur == PLAYER:                   # 出隊時即宣告勝利
            path, at = [], cur
            while at:
                path.append(at)
                at = parent[at]
            return path[::-1], expanded
        for dy, dx in DIRS:
            ny, nx = cur[0] + dy, cur[1] + dx
            if not (0 <= ny < ROWS and 0 <= nx < COLS) or MAP[ny][nx] == '#':
                continue
            g_new = g_best[cur] + 1         # 走一步成本 = 1
            nxt = (ny, nx)
            # Dijkstra 鬆弛 (relaxation)：發現更省的路才更新
            if nxt not in g_best or g_new < g_best[nxt]:
                g_best[nxt] = g_new
                parent[nxt] = cur
                heapq.heappush(frontier, (g_new + h(nxt), nxt))
    return None, expanded

def show(route):
    board = [list(row) for row in MAP]
    for y, x in route:
        if board[y][x] in '.N':
            board[y][x] = '*' if board[y][x] == '.' else 'N'
    for row in board:
        print(''.join(row))

if __name__ == '__main__':
    print("=== NPC 搜尋玩家 (A*) ===\n原始地圖：")
    show([])
    path, expanded = astar()
    if path:
        print(f"\n最短距離 = {len(path) - 1} 步，A* 只開展 {expanded} 個格子\n")
        show(path)
    else:
        print("NPC 到不了玩家（被牆完全包住）")

    # 對照組：純 BFS 在同一張圖會開展多少格？
    from collections import deque
    seen, frontier, bfs_exp = {NPC: 0}, deque([NPC]), 0
    while frontier:
        cur = frontier.popleft()
        bfs_exp += 1
        if cur == PLAYER:
            break
        for dy, dx in DIRS:
            ny, nx = cur[0] + dy, cur[1] + dx
            if 0 <= ny < ROWS and 0 <= nx < COLS and MAP[ny][nx] != '#' \
               and (ny, nx) not in seen:
                seen[(ny, nx)] = True
                frontier.append((ny, nx))
    print(f"\n對照：BFS 開展 {bfs_exp} 格  →  A* 開展 {expanded} 格（靠啟發函數省下很多）")
