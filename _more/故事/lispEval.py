#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lispEval.py — McCarthy 1960 eval LISP interpreter (簡單版)

以最簡單的方式實作 McCarthy 1960 論文中那個「半頁紙」的 eval S-function。

資料表示法（直接用 Python 的內建型別）:
    NIL    -> 用 Python 的 None 表示
    ATOM   -> 用 Python 的 str 表示
    PAIR   -> 用 Python 的 tuple (car, cdr) 表示，cdr 為 None 時即為一般 list

用法:
    python3 lispEval.py                 # 互動 REPL
    python3 lispEval.py '運算式'         # 求值單一運算式
"""

import sys

NIL = None          # 空表 / 假值
T = "T"             # 真值
_EOF = object()     # 剖析器用到的「輸入結束」哨兵，與 NIL(None) 區分

# ================================================================
# 基本 S-expression 建構 / 判斷
# ================================================================

def is_atom(x):
    """ATOM: 字串即 atom；NIL（空表）也視為 atom"""
    return x is NIL or isinstance(x, str)

def cons(a, d):
    """CONS[a; d] = (a . d)"""
    return (a, d)

def car(x):
    """CAR — 取表頭"""
    return x[0]

def cdr(x):
    """CDR — 取表尾"""
    return x[1]

# 常用的複合存取
def cadr(x):  return car(cdr(x))
def caddr(x): return car(cdr(cdr(x)))
def caar(x):  return car(car(x))
def cadar(x): return car(cdr(car(x)))
def caddar(x):return car(cdr(cdr(car(x))))

def mk_list(*items):
    """把 items 組成（代表一般 list 的）S-expression"""
    out = NIL
    for it in reversed(items):
        out = cons(it, out)
    return out

# ================================================================
# 關聯表（環境）操作
# ================================================================

def assoc(e, a):
    """ASSOC[e; a] — 在綁定表 a 找 atom e，回傳其值（binding 為 (name . value)）"""
    while a is not NIL:
        binding = car(a)
        if car(binding) == e:
            return cdr(binding)
        a = cdr(a)
    raise NameError("unbound: %s" % e)

def pair(x, y):
    """PAIR[x; y] — 把參數列 x 與引數值列 y 壓成綁定表"""
    if x is NIL and y is NIL:
        return NIL
    return cons(cons(car(x), car(y)), pair(cdr(x), cdr(y)))

def append(x, y):
    """APPEND[x; y] — 串接兩個表"""
    if x is NIL:
        return y
    return cons(car(x), append(cdr(x), y))

# ================================================================
# 剖析器 — recursive descent
# ================================================================

class Reader:
    """把 LISP 文字讀成 S-expression"""
    def __init__(self, s):
        self.s = s
        self.i = 0

    def skip_ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def read(self):
        self.skip_ws()
        if self.i >= len(self.s):
            return _EOF
        c = self.s[self.i]
        if c == '(':
            self.i += 1
            self.skip_ws()
            items = []
            while self.i < len(self.s) and self.s[self.i] != ')':
                el = self.read()
                if el is _EOF:
                    break
                items.append(el)
                self.skip_ws()
            if self.i < len(self.s):
                self.i += 1          # 吃掉 ')'
            return mk_list(*items) if items else NIL
        # atom
        start = self.i
        while self.i < len(self.s) and not self.s[self.i].isspace() \
              and self.s[self.i] not in '()':
            self.i += 1
        tok = self.s[start:self.i].upper().strip()
        if tok in ('', 'NIL'):
            return NIL
        return tok

def parse(s):
    return Reader(s).read()

# ================================================================
# 印表 — 把 S-expression 印回文字
# ================================================================

def pprint(x):
    if x is NIL:
        return "NIL"
    if is_atom(x):
        return x
    # 一般 list: (a b c)
    parts = []
    while x is not NIL and not is_atom(x):
        parts.append(pprint(car(x)))
        x = cdr(x)
    if x is not NIL:                    # 結尾是 atom => dotted pair
        parts.append(". " + pprint(x))
    return "(" + " ".join(parts) + ")"

# ================================================================
# McCarthy 的 eval 及輔助函式
# ================================================================

def evlis(m, a):
    """EVLIS[m; a] = [null[m] -> NIL; T -> cons[eval[car[m];a]; evlis[cdr[m];a]]]"""
    if m is NIL:
        return NIL
    return cons(eval(car(m), a), evlis(cdr(m), a))

def evcon(c, a):
    """EVCON[c; a] = [eval[caar[c];a] -> eval[cadar[c];a]; T -> evcon[cdr[c];a]]"""
    while c is not NIL:
        if eval(caar(c), a) is not NIL:
            return eval(cadar(c), a)
        c = cdr(c)
    return NIL

def appq(m):
    """APPQ[m] — 把每個元素包成 (QUOTE x NIL)，避免引數被重覆求值"""
    if m is NIL:
        return NIL
    return cons(mk_list("QUOTE", car(m), NIL), appq(cdr(m)))

def eval(e, a):
    """
    EVAL[e; a] — McCarthy 1960 的核心
      atom[e]              -> assoc[e; a]
      atom[car[e]] ->
        QUOTE -> cadr[e]
        ATOM  -> atom[eval[cadr[e];a]]
        EQ    -> eval[cadr[e];a] = eval[caddr[e];a]
        COND  -> evcon[cdr[e]; a]
        CAR   -> car[eval[cadr[e];a]]
        CDR   -> cdr[eval[cadr[e];a]]
        CONS  -> cons[eval[cadr[e];a]; eval[caddr[e];a]]
        T     -> eval[cons[assoc[car[e];a]; appq[evlis[cdr[e];a]]]; a]
      caar[e] = LABEL  -> eval[cons[caddar[e]; cdr[e]]; cons[list[cadar[e]; car[e]; a]]]
      caar[e] = LAMBDA -> eval[caddar[e]; append[pair[cadar[e]; evlis[cdr[e];a]; a]]]
    """
    if e is NIL:
        return NIL
    if is_atom(e):
        return assoc(e, a)

    head = car(e)

    if is_atom(head):
        if head == "QUOTE":
            return cadr(e)
        if head == "ATOM":
            return T if is_atom(eval(cadr(e), a)) else NIL
        if head == "EQ":
            return T if eval(cadr(e), a) == eval(caddr(e), a) else NIL
        if head == "COND":
            return evcon(cdr(e), a)
        if head == "CAR":
            return car(eval(cadr(e), a))
        if head == "CDR":
            return cdr(eval(cadr(e), a))
        if head == "CONS":
            return cons(eval(cadr(e), a), eval(caddr(e), a))
        # 一般函式呼叫，配合 McCarthy 的 apply 定義
        return eval(cons(assoc(head, a), appq(evlis(cdr(e), a))), a)

    # head 不是 atom，檢查 LABEL / LAMBDA
    head_head = caar(e)
    if head_head == "LABEL":
        name = cadar(e)        # 函式名稱
        lam  = caddar(e)       # (LAMBDA ...) 形式
        args = cdr(e)          # 傳入的引數形式
        new_a = cons(cons(name, car(e)), a)   # name -> 整個 LABEL 形式（遞迴用）
        return eval(cons(lam, args), new_a)
    if head_head == "LAMBDA":
        params = cadar(e)      # (X Y ...)
        body   = caddar(e)
        return eval(body, append(pair(params, evlis(cdr(e), a)), a))

    raise SyntaxError("unknown form: %s" % pprint(e))

# ================================================================
# REPL
# ================================================================

def repl():
    env = NIL
    print("McCarthy LISP (1960) — 輸入 (quit) 離開")
    print("內建: QUOTE ATOM EQ COND CAR CDR CONS LABEL LAMBDA")
    print("範例: (CAR (QUOTE (A B C)))  =>  A")
    while True:
        try:
            line = input("LISP> ").strip()
        except EOFError:
            break
        if not line:
            continue
        expr = parse(line)
        if expr == "QUIT" or (not is_atom(expr) and not expr is NIL
                              and car(expr) == "QUIT"):
            break
        # (DEFINE name value) — 把 value 原樣（不求值）存入環境
        if not is_atom(expr) and not expr is NIL and car(expr) == "DEFINE":
            name = cadr(expr)
            env = cons(cons(name, caddr(expr)), env)
            print("Defined: %s" % name)
            continue
        try:
            print(pprint(eval(expr, env)))
        except (NameError, SyntaxError) as ex:
            print("Error: %s" % ex)

# ================================================================
# 執行
# ================================================================

def main():
    if len(sys.argv) > 1:
        expr = parse(sys.argv[1])
        print(pprint(eval(expr, NIL)))
    else:
        repl()

if __name__ == "__main__":
    main()
