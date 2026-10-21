"""動態規劃解法：edit distance（編輯距離）定位最相似單字。

問題：在字典 D 中，找出與 query 編輯距離最小的單字（模糊搜尋/拼寫檢查）。

狀態定義
    dp[i][j] = query 前 i 字元 vs 候選 前 j 字元 的編輯距離。

轉移方程
    dp[i][j] = dp[i-1][j-1]                      若 q[i-1]==c[j-1]
             = 1 + min(dp[i-1][j],               刪除
                       dp[i][j-1],               插入
                       dp[i-1][j-1])             取代

對字典中每個候選都算一次，取最小值。
複雜度：每個候選 O(|q|·|c|)，全部 O(Σ|c|·|q|)。
可先用長度差或 n-gram 過濾再精算（bisect 過濾常見）。
"""

from __future__ import annotations


def edit_distance(a: str, b: str) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[n][m]


def fuzzy_search(query: str, dictionary: list[str], max_dist: int = 2) -> list[tuple[int, str]]:
    """回傳 (編輯距離, 單字) 列表，距離 <= max_dist，依距離遞增。"""
    results = []
    for word in dictionary:
        if abs(len(word) - len(query)) > max_dist:
            continue  # 長度剪枝
        d = edit_distance(query, word)
        if d <= max_dist:
            results.append((d, word))
    results.sort()
    return results


if __name__ == "__main__":
    words = ["hello", "world", "hallo", "help", "hell", "shell", "word"]
    print(fuzzy_search("helo", words))
