# Lambda 演算 (Lambda Calculus)

Lambda 演算是 Alonzo Church 在 1936 年發明的計算模型，與圖靈機等價，是函數式編程的理論基礎。

## 核心概念

Lambda 演算是最小的函數式語言，只有三種語法：

```
項 (Term) ::= 變數 x
            | λ 變數 . 項     (抽象/函數定義)
            | (項 項)          (應用/函數呼叫)
```

**範例**:
```
λx.x           # 恆等函數：接受 x，返回 x
λx.λy.x       # 接受 x，返回另一個接受 y 的函數
(λx.x) y      # 應用：將 y 傳給恆等函數，結果為 y
```

## 三個版本

本目錄包含三個不同複雜度的實現：

| 版本 | 路徑 | 行數 | 特色 |
|------|------|------|------|
| 精簡版 | `02-short/` | 77 | 核心功能 |
| 完整版 | `01-full/` | 219 | Church Encoding + Y Combinator |
| 直譯器 | `03-interpreter/` | 188 | 完整 Parser + AST |

## 完整實現架構

### 1. AST 節點

```python
class Node: pass

class Variable(Node):
    def __init__(self, name): self.name = name

class Abstraction(Node):
    def __init__(self, param, body):
        self.param = param
        self.body = body

class Application(Node):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
```

### 2. 解析器

```python
class Parser:
    def parse_expression(self):
        if self.next_token() == '\\':
            self.consume('\\')
            var = self.consume()
            self.consume('.')
            body = self.parse_expression()
            return Abstraction(var, body)
        
        # 左結合的應用
        expr = self.parse_atom()
        while self.next_token():
            expr = Application(expr, self.parse_atom())
        return expr
```

### 3. 求值器（β-歸約）

```python
def eval(self, node):
    if isinstance(node, Application):
        lhs = self.eval(node.lhs)
        if isinstance(lhs, Abstraction):
            # β-歸約：代換參數
            return self.eval(
                self.substitute(lhs.body, lhs.param, node.rhs)
            )
    
    if isinstance(node, Abstraction):
        return Abstraction(node.param, self.eval(node.body))
    
    return node

def substitute(self, node, var, replacement):
    if isinstance(node, Variable):
        return replacement if node.name == var else node
    
    if isinstance(node, Abstraction):
        if node.param == var: return node
        return Abstraction(node.param, 
            self.substitute(node.body, var, replacement))
    
    if isinstance(node, Application):
        return Application(
            self.substitute(node.lhs, var, replacement),
            self.substitute(node.rhs, var, replacement))
```

### 4. 自由變數與約束變數

```python
def get_free_vars(self, node):
    if isinstance(node, Variable):
        return {node.name}
    if isinstance(node, Abstraction):
        return self.get_free_vars(node.body) - {node.param}
    if isinstance(node, Application):
        return self.get_free_vars(node.lhs) | self.get_free_vars(node.rhs)
    return set()
```

## Church 編碼

用純 Lambda 演算表示資料結構與基本類型。

### Church Booleans

```python
TRUE  = lambda x: lambda y: x  # if true then x else y
FALSE = lambda x: lambda y: y  # if false then x else y
IF    = lambda c: lambda x: lambda y: c(x)(y)
```

**邏輯運算**:
```python
AND = lambda p: lambda q: p(q)(p)   # if p then q else p
OR  = lambda p: lambda q: p(p)(q)   # if p then p else q
NOT = lambda c: c(FALSE)(TRUE)     # if c then false else true
```

**測試**:
```python
AND(TRUE)(FALSE)  # = FALSE
OR(FALSE)(TRUE)   # = TRUE
NOT(TRUE)         # = FALSE
```

### Church Numerals

用函數應用次數表示數字：

```python
ZERO  = lambda f: lambda x: x           # f^0(x) = x
ONE   = lambda f: lambda x: f(x)        # f^1(x) = f(x)
TWO   = lambda f: lambda x: f(f(x))     # f^2(x) = f(f(x))
THREE = lambda f: lambda x: f(f(f(x)))  # f^3(x) = f(f(f(x)))
```

**轉換函數**:
```python
def church_to_int(n):
    return n(lambda x: x + 1)(0)

def int_to_church(n):
    result = ZERO
    for _ in range(n):
        result = SUCCESSOR(result)
    return result
```

### 算術運算

```python
SUCC      = lambda n: lambda f: lambda x: f(n(f)(x))
ADD       = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MULT      = lambda m: lambda n: lambda f: m(n(f))
POWER     = lambda x: lambda y: y(x)
PRED      = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda a: a)
SUB       = lambda m: lambda n: n(PRED)(m)
```

### 比較運算

```python
IS_ZERO   = lambda n: n(lambda _: FALSE)(TRUE)
LEQ       = lambda m: lambda n: IS_ZERO(SUB(m)(n))
IS_EQUAL  = lambda m: lambda n: AND(LEQ(m)(n))(LEQ(n)(m))
```

### Church Lists

```python
CONS  = lambda x: lambda y: lambda f: f(x)(y)
CAR   = lambda p: p(TRUE)
CDR   = lambda p: p(FALSE)
NIL   = lambda x: TRUE
NULL  = lambda p: p(lambda x: lambda y: FALSE)
```

## Y Combinator（不動點 combinator）

這是 Lambda 演算中最神奇的構造之一，實現了遞迴。

### 問題

如何定義遞迴函數？

```
FACTORIAL = if n=0 then 1 else n * FACTORIAL(n-1)
```

FACTORIAL 在定義中引用了自己！

### 解決方案

```python
Y = lambda f: (lambda x: f(lambda y: x(x)(y)))(lambda x: f(lambda y: x(x)(y)))
```

**為什麼有效？**

```
Y(F) 
= (λx.F(λy.x(x)(y))) (λx.F(λy.x(x)(y)))
= F(λy.(λx.F(λy.x(x)(y)))(λx.F(λy.x(x)(y)))(y))
= F(Y(F))
```

所以 `Y(F)` 是 `F(Y(F))` 的不動點！

### 應用：階乘

```python
FACTORIAL = Y(lambda f: lambda n:
    IF(IS_ZERO(n))
        (lambda _: SUCCESSOR(n))
        (lambda _: MULT(n)(f(PRED(n))))
    (NIL))
```

## 完整列表操作

### RANGE

```python
RANGE = lambda m: lambda n: Y(
    lambda f: lambda m:
        IF(IS_EQUAL(m)(n))
            (lambda _: CONS(m)(NIL))
            (lambda _: CONS(m)(f(SUCC(m))))
    (NIL)
)(m)
```

### MAP

```python
MAP = lambda x: lambda g: Y(
    lambda f: lambda x:
        IF(IS_NULL(x))
            (lambda _: x)
            (lambda _: CONS(g(CAR(x)))(f(CDR(x))))
    (NIL)
)(x)
```

## 惰性求值（Call-by-Name）

直譯器實現中使用了惰性求值，確保：

1. **參數不提前求值**: 只有真正需要時才計算
2. **支援無限結構**: 如無限列表
3. **避免無窮歸約**: 延遲直到有足夠資訊

```python
def eval(self, node):
    if isinstance(node, Application):
        lhs = self.eval(node.lhs)
        if isinstance(lhs, Abstraction):
            # 延遲代換，不求值 rhs
            return self.eval(
                self.substitute(lhs.body, lhs.param, node.rhs)
            )
    return node
```

## Lambda 演算 vs 圖靈機

| 特性 | Lambda 演算 | 圖靈機 |
|------|-------------|--------|
| 發明者 | Alonzo Church | Alan Turing |
| 年份 | 1936 | 1936 |
| 核心概念 | 函數應用與代換 | 狀態與轉移 |
| 資料表示 | Church 編碼 | 符號串 |
| 表達力 | 完全等價 | 完全等價 |

## Church-Turing 論點

> 任何可計算的函數都可以用 Lambda 演算或圖靈機表示。

這確立了「可計算性」的數學定義。

## 與程式語言的關係

```
Lambda 演算
     ↓
Lisp (1958) - 第一個函數式語言
     ↓
Scheme, Clojure, Racket
     ↓
ML, Haskell, OCaml
     ↓
現代語言 (Python, JS, Rust) 的函數式特性
```

## 執行範例

```bash
$ cd 02-short
$ python lambdaCalculus.py
Testing Church numbers:
ZERO = 0
ONE = 1
TWO = 2
...
Testing operations:
PLUS(TWO, THREE) = 5
MULT(TWO, THREE) = 6
POWER(TWO, THREE) = 8
```

```bash
$ cd 03-interpreter
$ cat example/one.lc
one = \f.\x.f x;
one;
$ python lambda.py example/one.lc
--- Evaluation Result ---
\f.\x.f x
```

## 學習重點

1. **語法封裝**: 一切皆為函數
2. **代換模型**: β-歸約的本質
3. **Church 編碼**: 如何用函數表示資料
4. **Y Combinator**: 遞迴的純函數式實現
5. **閉包**: Lambda 表達式的環境綁定
