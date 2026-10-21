"""動態規劃解法：LCS (最長共同子序列) 產生 diff。

狀態定義
    dp[i][j] = a 的前 i 個字元與 b 的前 j 個字元的 LCS 長度

轉移方程
    dp[i][j] = dp[i-1][j-1] + 1            若 a[i-1] == b[j-1]
             = max(dp[i-1][j], dp[i][j-1]) 否則

回溯時，'=' 來自對角線，'-' 代表刪除 a 的字元，'+' 代表插入 b 的字元。
"""

from __future__ import annotations


def lcs_table(a: str, b: str) -> list[list[int]]:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp


def diff_lcs(a: str, b: str) -> list[tuple[str, str]]:
    """回傳 op 列表：('=', ch) 相同 / ('-', ch) 刪除 / ('+', ch) 插入。"""
    dp = lcs_table(a, b)
    ops: list[tuple[str, str]] = []
    i, j = len(a), len(b)
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(("=", a[i - 1]))
            i, j = i - 1, j - 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j - 1]):
            ops.append(("+", b[j - 1]))
            j -= 1
        else:
            ops.append(("-", a[i - 1]))
            i -= 1
    ops.reverse()
    return ops


def format_diff(a: str, b: str) -> str:
    lines = []
    for op, ch in diff_lcs(a, b):
        lines.append(f"{op} {ch}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_diff("ABCABBA", "CBABAC"))
