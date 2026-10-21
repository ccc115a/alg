"""非動態規劃解法：Thompson NFA 模擬（grep/egrep 的正規表示式引擎原理）。

原理
    把 pattern 編譯成 NFA（非確定性有限自動機）：
      - 普通字元 c：建一個 c 轉移
      - '.'          ：建一個「任意字元」轉移
      - 串接         ：子機器頭尾相連（ε 邊）
      - '*'          ：加 ε-環（可跳過、可重複）
      - '|'          ：兩分支（ε 到兩邊，兩邊再 ε 到匯合點）
    模擬時維持「當前可能處於的所有狀態集合」，每讀一個字元就並行推進
    （ε-closure + 轉移）。任一接受狀態在集合中即匹配成功。

    這是經典的 Thompson 構造 + 並行模擬，也是 grep 的核心；
    與 DP 的 dp[i][j] 在本質上等價——「第 i 字元後可能處於的狀態集」
    就是 DP 表的一列——但實作上以圖遍歷而非表格填寫呈現。

複雜度：編譯 O(|p|)、模擬每字元 O(|p|)，總計 O(n·|p|)；
最壞與 DP 相同，但 ε-closure 可快取、實務常數更小。
"""

from __future__ import annotations


class NFA:
    """支援語法：字元、'.'、'*'、'|'、'()'。'*' 綁定前一個 atom。"""

    def __init__(self, pattern: str):
        self.trans: dict[int, list[tuple[str | None, int]]] = {}
        # 構造；start 固定為 0，accept 為最終出口
        _, self.start, self.accept = self._parse(pattern, 0, len(pattern))

    def _new_state(self) -> int:
        sid = len(self.trans)
        self.trans[sid] = []
        return sid

    def _add(self, fr: int, ch: str | None, to: int) -> None:
        self.trans[fr].append((ch, to))

    def _parse(self, p: str, i: int, end: int) -> tuple[int, int, int]:
        """解析 alternation：branch ('|' branch)*。回傳 (新 i, 入口, 出口)。"""
        entry = self._new_state()
        exit_ = self._new_state()
        cur_entry = entry
        while True:
            i, tail = self._parse_seq(p, i, end, cur_entry)
            self._add(tail, None, exit_)
            if i < end and p[i] == "|":
                i += 1
                cur_entry = self._new_state()
                self._add(entry, None, cur_entry)  # 分支入口
            else:
                break
        return i, entry, exit_

    def _parse_seq(self, p: str, i: int, end: int, start: int) -> tuple[int, int]:
        """解析串接的 atom/atom* 序列。回傳 (新 i, 出口狀態)。"""
        cur = start
        while i < end and p[i] not in "|)":
            if p[i] == "(":
                i += 1
                i, sub_in, sub_out = self._parse(p, i, end)
                assert i < end and p[i] == ")", "missing ')'"
                i += 1  # 跳過 ')'
                # group 也支援 '*'
                if i < end and p[i] == "*":
                    i += 1
                    body_in = self._new_state()
                    out = self._new_state()
                    self._add(cur, None, body_in)
                    self._add(cur, None, out)      # 零次
                    self._add(body_in, None, sub_in)  # 進入子機器
                    self._add(sub_out, None, out)    # 離開子機器
                    self._add(out, None, body_in)    # 重複
                    cur = out
                else:
                    self._add(cur, None, sub_in)
                    cur = sub_out
                continue
            # atom
            ch = p[i]
            if ch != ".":
                i += 1
            else:
                i += 1  # '.' 本身就是 atom，ch 保持 '.'
            # 檢查 '*'
            if i < end and p[i] == "*":
                i += 1
                # Thompson star: cur --ε--> body --ε--> out, body --ε--> out (skip),
                #   out --ε--> body (loop)
                body_in = self._new_state()
                out = self._new_state()
                self._add(cur, None, body_in)   # 進入
                self._add(cur, None, out)       # 跳過（零次）
                self._add(body_in, ch, out)     # 吃一個字元
                self._add(out, None, body_in)   # 重複（環）
                cur = out
            else:
                nxt = self._new_state()
                self._add(cur, ch, nxt)
                cur = nxt
        return i, cur

    def _epsilon_closure(self, states: set[int]) -> set[int]:
        stack = list(states)
        while stack:
            s = stack.pop()
            for ch, t in self.trans[s]:
                if ch is None and t not in states:
                    states.add(t)
                    stack.append(t)
        return states

    def match(self, text: str) -> bool:
        """text 是否完全匹配 pattern（fullmatch 語義，與 DP 版一致）。"""
        cur = self._epsilon_closure({self.start})
        for ch in text:
            nxt: set[int] = set()
            for s in cur:
                for c, t in self.trans[s]:
                    if c is not None and (c == "." or c == ch):
                        nxt.add(t)
            if not nxt:
                return False
            cur = self._epsilon_closure(nxt)
        return self.accept in cur


def nfa_match(s: str, p: str) -> bool:
    return NFA(p).match(s)


if __name__ == "__main__":
    import re

    for s, p in [
        ("aa", "a"),
        ("aa", "a*"),
        ("ab", ".*"),
        ("aab", "c*a*b"),
        ("abc", "(a|b)*c"),
    ]:
        r = nfa_match(s, p)
        print(f"nfa_match({s!r}, {p!r}) = {r}")
        assert r == bool(re.fullmatch(p, s)), f"re 對照失敗: {s=} {p=}"
