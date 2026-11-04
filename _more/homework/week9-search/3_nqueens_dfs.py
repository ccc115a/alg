#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 習題 3：八皇后問題（DFS + 回溯）
#
# 問題：在 8x8 棋盤上放 8 個皇后，使得任何兩個皇后都不在同一列、
#       同一行、或同一條對角線上（即不能互相攻擊）。問有幾種放法？
#
# 搜尋法分析（這是經典的「回溯法」＝ 走不通就退一步的 DFS）：
#   狀態比對  = 每一列放一個皇后 → 狀態就是「前 k 列的行號序列」
#   開展      = 在第 k 列的 8 個欄位各試一次
#   剪枝      = 檢查新皇后是否被前面的皇后攻擊，不符就直接不遞迴
#               （= 只搜合法分支，大幅省下搜尋空間）
#   DFS 特性  = 一分支走到底再換下一支；全部窮舉完 → 解數量正確
#
# 約束檢查：
#   同行 conflict_column  → q[i] == q[k]
#   主對角線 (左上到右下)   → q[i] - i == q[k] - k
#   反對角線 (右上到左下)    → q[i] + i == q[k] + k
#
# 執行：python3 3_nqueens_dfs.py

N = 8
queens = []            # queens[r] = c：第 r 列的皇后放在第 c 行
solutions = []         # 收集所有解（每個解是完整的行號 list）

def conflict(row, col):
    """檢查把皇后放到 (row, col) 會不會被前面的皇后攻擊"""
    for r, c in enumerate(queens):
        # 同行 | 主對角線 | 反對角線
        if c == col or abs(r - row) == abs(c - col):
            return True
    return False

def dfs(row=0):
    """DFS：從第 row 列開始往下放皇后；放滿 N 列就是一組解"""
    if row == N:                       # 全部放好了 → 收集解答
        solutions.append(queens[:])
        return
    for col in range(N):
        if conflict(row, col):
            continue                   # 剪枝：這格不行，換下一行
        queens.append(col)             # 選擇：放皇后
        dfs(row + 1)                   # 往下一層走
        queens.pop()                   # 撤銷（回溯）：換下一行再試

def board_str(sol):
    """畫出棋盤：Q = 皇后，. = 空格"""
    grid = [['.'] * N for _ in range(N)]
    for r, c in enumerate(sol):
        grid[r][c] = 'Q'
    return [' '.join(row) for row in grid]

if __name__ == '__main__':
    dfs()
    print(f"=== 八皇后 (DFS + 回溯) ===\n共找到 {len(solutions)} 組解（理論值 92）\n")
    for i, sol in enumerate(solutions, 1):
        print(f"解 {i}：行號序列 = {sol}")
        if i <= 3:                            # 只畫前三組解的棋盤
            for line in board_str(sol):
                print("   " + line)
            print()
