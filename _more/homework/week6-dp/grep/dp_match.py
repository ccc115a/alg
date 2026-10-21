"""動態規劃解法：正規表達式比對 (支援 . 與 *)。

支援語法：'.' 匹配任意單一字元，'*' 匹配前一個字元零次或多次。
即經典的 regex matching（如 LeetCode #10）。

狀態定義
    dp[i][j] = s 的前 i 個字元是否能完全匹配 p 的前 j 個 pattern。

轉移方程
    p[j-1] 是普通字元或 '.'：
        dp[i][j] = dp[i-1][j-1] and s[i-1] == p[j-1] (或 p[j-1]=='.')
    p[j-1] 是 '*'，令前驅 token = p[j-2]：
        - 零次：dp[i][j] = dp[i][j-2]
        - 一次以上：dp[i-1][j] and s[i-1] 匹配 token
    注意 '*' 前面一定要有 token，故 j >= 2。

複雜度：時間 O(nm)、空間 O(nm)（可壓成 O(m)）。
"""

from __future__ import annotations


def is_match(s: str, p: str) -> bool:
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    # 空字串對 "a*b*c*" 型 pattern 可匹配（全零次）
    for j in range(2, m + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 2]  # 零次
                tok = p[j - 2]
                if tok == "." or tok == s[i - 1]:
                    dp[i][j] |= dp[i - 1][j]  # 一次以上（'*' 留著繼續吃）
            else:
                if p[j - 1] == "." or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
    return dp[n][m]


def find_matches(text: str, pattern: str) -> list[int]:
    """回傳 text 中所有「完全匹配 pattern」的起始位置（pattern 需吃完整段才停）。
    這裡簡化為：對每個起始位置 i，檢查 text[i:] 是否有前綴完全匹配 pattern。
    """
    results = []
    for i in range(len(text)):
        # 由於 is_match 要求完全匹配，需再用「可提前結束」的變體
        if _match_prefix(text, i, pattern):
            results.append(i)
    return results


def _match_prefix(s: str, start: int, p: str) -> bool:
    """檢查 s[start:] 是否有某前綴完全匹配 p（用 dp 掃到任意 i 即可）。"""
    n, m = len(s) - start, len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(2, m + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 2]
                tok = p[j - 2]
                if tok == "." or tok == s[start + i - 1]:
                    dp[i][j] |= dp[i - 1][j]
            else:
                if p[j - 1] == "." or p[j - 1] == s[start + i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
        if dp[i][m]:
            return True
    return False


if __name__ == "__main__":
    for s, p in [("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*.")]:
        print(f"is_match({s!r}, {p!r}) = {is_match(s, p)}")
    print(find_matches("abab", "ab*"))
