#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 1：老鼠走迷宮問題（DFS 深度優先搜尋）
#
# 問題：老鼠從入口 S 走到出口 E，只能上下左右移動。
#       找出一條可行路徑（DFS 不保證最短，但實作簡單、自然回溯）。
#
# 搜尋法分析：
#   狀態空間 State Space = 座標 (y, x)
#   開展 Expand          = 造訪上/下/左/右四個鄰居
#   搜尋策略            = DFS + 回溯 (backtracking)，走到撞牆再退回換路
#   訪問表 visited       = 記錄走過的格子，避免繞圈圈無限循環
#
# 執行：python3 1_rat_maze_dfs.py

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
    """找出字元 ch 在迷宮裡的位置"""
    for y in range(ROWS):
        for x in range(COLS):
            if MAZE[y][x] == ch:
                return (y, x)
    return None

start, goal = find('S'), find('E')
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]   # 上 下 左 右
visited = set()
path = []                                   # 目前路徑的堆疊
steps = 0                                   # 統計嘗試的格子數

def dfs(y, x):
    global steps
    steps += 1
    visited.add((y, x))
    path.append((y, x))
    if (y, x) == goal:
        return True                         # 找到出口，遞迴沿 True 逐層結束
    for dy, dx in DIRS:
        ny, nx = y + dy, x + dx
        if 0 <= ny < ROWS and 0 <= nx < COLS \
           and MAZE[ny][nx] != '#' and (ny, nx) not in visited:
            if dfs(ny, nx):                 # 往這條路走到最深
                return True
    path.pop()                              # 死路：回溯，把這格從路徑移除
    return False

def show(route):
    """把找到的路徑畫在迷宮上（用 * 標記腳印）"""
    board = [list(row) for row in MAZE]
    for y, x in route:
        if board[y][x] == '.':
            board[y][x] = '*'
    for row in board:
        print(''.join(row))

if __name__ == '__main__':
    print("=== 老鼠走迷宮 (DFS) ===\n原始迷宮：")
    show([])
    if dfs(*start):
        print(f"\n找到路徑！長度 = {len(path)} 格，共嘗試 {steps} 次\n")
        show(path)
        print("\n路徑座標:", ' -> '.join(str(p) for p in path))
    else:
        print("這個迷宮沒有路可以到達出口！")
