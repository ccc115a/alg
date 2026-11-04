#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 2：狼、羊、甘藍菜過河問題（BFS 廣度優先搜尋）
#
# 問題：農夫要把狼、羊、菜運到河對岸，但小船一次只能載農夫與一件物品。
#       沒人看管時，狼會吃羊、羊會吃菜。請找出最少的渡河次數。
#
# 搜尋法分析：
#   狀態 State   = (農夫, 狼, 羊, 菜) 各在 0=左岸 1=右岸，共 16 個狀態
#   起點          = (0,0,0,0)   目標 = (1,1,1,1)
#   動作 Move    = 農夫獨自過河，或帶狼 / 羊 / 菜一起過河（翻轉對應位元）
#   陷阱約束     = 羊單獨與狼在一起（農夫不在）→ 狼吃羊
#                  羊單獨與菜在一起（農夫不在）→ 羊吃菜
#   搜尋策略    = BFS：一層一層往外展開，第一次碰到目標就是最少步數
#   visited      = 同一個狀態不需要拜訪第二次（用 set 記錄）
#
# BFS 和 DFS 的差別：這類「狀態圖」問題用 BFS 保證最短解；
# 若用 DFS 可能先走到一條很繞（甚至死循環）的路。
#
# 執行：python3 2_wolf_sheep_cabbage_bfs.py

from collections import deque

# 狀態用 4 個位元表示：(Farmer, Wolf, Sheep, Cabbage)，0=左岸 1=右岸
START = (0, 0, 0, 0)
GOAL = (1, 1, 1, 1)
NAME = ['農夫', '狼', '羊', '菜']

def unsafe(state):
    """檢查狀態是否違反約束（狼、羊、羊、菜）"""
    f, w, s, c = state
    return (f != s and (s == w or s == c))   # 羊沒人看時，旁邊不能有狼或菜

def path_to_str(path):
    """把狀態序列轉成動作描述"""
    out = []
    for prev, cur in zip(path, path[1:]):
        moved = [NAME[i] for i in range(4) if prev[i] != cur[i]]
        side = '右' if cur[0] else '左'
        carry = '帶著' + '和'.join(moved[1:]) if len(moved) > 1 else '單獨'
        out.append(f"農夫{carry}過河到{side}岸   狀態 = {cur}")
    return out

def bfs(start, goal):
    """BFS 找最短解；回傳完整狀態路徑"""
    frontier = deque([start])        # 待開展的狀態佇列 (FIFO)
    parent = {start: None}           # 前驅表，順便當 visited 用
    while frontier:
        state = frontier.popleft()   # 佇列性質 → 同一層先做完才去下一層
        if state == goal:
            # 從 parent 表回溯重建路徑
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1]
        f, w, s, c = state
        # 產生所有合法動作：農夫可以獨自走，或帶著「在他這邊」的任一件物品
        moves = [None] + [i for i in range(1, 4) if state[i] == f]
        for passenger in moves:
            nxt = list(state)
            nxt[0] = 1 - f                    # 農夫一定過河
            if passenger is not None:
                nxt[passenger] = 1 - f        # 帶上的物品跟著翻轉
            nxt = tuple(nxt)
            if nxt not in parent and not unsafe(nxt):
                parent[nxt] = state
                frontier.append(nxt)          # 排到佇列尾端 = 下一層再開展
    return None

if __name__ == '__main__':
    print("=== 狼羊菜過河 (BFS) ===\n起點 = (0,0,0,0) 全在左岸\n")
    path = bfs(START, GOAL)
    if path:
        print(f"最少渡河 {len(path) - 1} 次：")
        for line in path_to_str(path):
            print("  " + line)
    else:
        print("無解（約束設錯了！）")
