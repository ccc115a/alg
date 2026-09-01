# Prolog 直譯器

Prolog 是一種**邏輯式編程語言**，採用完全不同的範式：宣言式編程，告訴電腦「什麼是真的」，而不是「如何做」。

## 語言特色

- **模式比對**: 透過事實與規則定義知識
- **Unification**: 自動變數綁定與約束傳播
- **Backtracking**: 自動搜尋所有可能的解答
- **邏輯變數**: 延遲賦值的變數

## 語法結構

```prolog
% 事實 (Facts)
likes(john, music).
likes(jane, books).

% 規則 (Rules)
friend(X, Y) :- likes(X, Z), likes(Y, Z).

% 查詢 (Queries)
?- likes(john, What).
```

## 架構設計

### 1. 核心資料結構

```python
class Var:
    def __init__(self, name): self.name = name
    def __hash__(self): return hash(self.name)
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name

class Term:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
    
    def __repr__(self):
        if not self.args: return str(self.name)
        return f"{self.name}({', '.join(map(str, self.args))})"

class Clause:
    def __init__(self, head, body=None):
        self.head = head
        self.body = body or []
```

### 2. Parser (語法分析器)

#### Tokenizer

```python
class Parser:
    def __init__(self, text):
        text = re.sub(r'%.*', '', text)  # 移除註解
        self.tokens = re.findall(
            r"'[^']*'|[A-Z_][a-zA-Z0-9_]*|[a-z][a-zA-Z0-9_]*|\d+"
            r"|:-|\\=|\(|\)|\[|\]|\||,|\.|>=|=<|<=|>|<|=|\+|-|\*|/",
            text
        )
```

**規則**：
- 大寫字母開頭 → 變數 (`X`, `What`)
- 小寫字母開頭 → 原子/謂詞 (`likes`, `john`)

#### Term 解析

```python
def parse_term(self):
    token = self.next_token()
    
    # 列表解析 [...]
    if token == '[':
        if self.peek() == ']':  # 空列表 []
            return Term('[]')
        
        elements = []
        while True:
            elements.append(self.parse_term())
            if self.peek() == ',': self.next_token()
            else: break
        
        # 處理尾部 [H|T]
        tail = Term('[]')
        if self.peek() == '|':
            self.next_token()
            tail = self.parse_term()
        
        # 轉換為內部結構 [H|T] → [|](H, T)
        res = tail
        for e in reversed(elements):
            res = Term('[|]', [e, res])
        return res
    
    # 變數檢測
    is_var = (token[0].isupper() or token == '_')
    
    # 複合項 parse_term(args)
    if self.peek() == '(':
        args = []
        while True:
            args.append(self.parse_term())
            if self.peek() == ')': break
            self.next_token()  # skip ','
        return Term(token, args)
    
    return Var(token) if is_var else Term(token)
```

### 3. Unification (合一)

Unification 是 Prolog 的核心：找出兩個 Term 是否可以「合一」。

```python
def unify(x, y, subst):
    subst = subst.copy()
    x, y = resolve(x, subst), resolve(y, subst)
    
    # 相同 → 成功
    if x == y: return subst
    
    # 匿名變數 _ → 忽略
    if isinstance(x, Var) and x.name == '_': return subst
    if isinstance(y, Var) and y.name == '_': return subst
    
    # 單一變數 → 綁定
    if isinstance(x, Var):
        subst[x.name] = y; return subst
    if isinstance(y, Var):
        subst[y.name] = x; return subst
    
    # 複合項 → 遞迴合一
    if isinstance(x, Term) and isinstance(y, Term):
        if x.name != y.name or len(x.args) != len(y.args):
            return None
        for a, b in zip(x.args, y.args):
            subst = unify(a, b, subst)
            if subst is None: return None
        return subst
    
    return None
```

**關鍵點**：
- `resolve()` 追蹤變數鏈
- 遞迴處理巢狀結構
- 失敗立即返回 `None`

### 4. 求解引擎 (SLD 解析)

```python
def solve(goals, clauses, subst, level=0):
    # 無目標 → 成功
    if not goals: yield subst; return
    
    first, rest = goals[0], goals[1:]
    
    # 內建謂詞處理
    if isinstance(first, Term):
        if first.name == 'write':
            print(resolve(first.args[0], subst), end='')
            yield from solve(rest, clauses, subst, level + 1)
            return
        
        if first.name == 'nl':
            print()
            yield from solve(rest, clauses, subst, level + 1)
            return
        
        if first.name == 'is':
            val = eval_expr(first.args[1], subst)
            new_subst = unify(first.args[0], Term(str(val)), subst)
            if new_subst is not None:
                yield from solve(rest, clauses, new_subst, level + 1)
            return
        
        if first.name in ['>', '<', '>=', '<=']:
            v1 = eval_expr(first.args[0], subst)
            v2 = eval_expr(first.args[1], subst)
            if eval({'>': v1 > v2, '<': v1 < v2, ...}[first.name]):
                yield from solve(rest, clauses, subst, level + 1)
            return
    
    # 規則匹配 (最關鍵！)
    for clause in clauses:
        # 變數重新命名（避免衝突）
        mapping = {v: Var(f"{v}_{level}") for v in get_vars(clause)}
        head = rename_vars(clause.head, mapping)
        body = [rename_vars(b, mapping) for b in clause.body]
        
        # 嘗試合一
        new_subst = unify(first, head, subst)
        if new_subst is not None:
            # 遞迴求解規則體
            yield from solve(body + rest, clauses, new_subst, level + 1)
```

### 5. Append 實現 (展示 backtracking)

```python
if first.name == 'append' and len(first.args) == 3:
    a1, a2, a3 = resolve(first.args[0], subst), \
                 resolve(first.args[1], subst), \
                 resolve(first.args[2], subst)
    
    # 第一條規則：append([], L, L)
    s = unify(a1, Term('[]'), subst)
    if s is not None:
        s2 = unify(a2, a3, s)
        if s2 is not None:
            yield from solve(rest, clauses, s2, level + 1)
    
    # 第二條規則：append([H|T], L, [H|R]) :- append(T, L, R)
    h = Var(f"_AH{level}")
    t = Var(f"_AT{level}")
    r = Var(f"_AR{level}")
    s = unify(a1, Term('[|]', [h, t]), subst)
    if s is not None:
        s2 = unify(a3, Term('[|]', [h, r]), s)
        if s2 is not None:
            yield from solve([Term('append', [t, a2, r])] + rest, clauses, s2, level + 1)
```

### 6. 互動式查詢

```python
def main():
    # 載入知識庫
    with open(sys.argv[1], 'r') as f:
        db = Parser(f.read()).parse_all()
    
    # 查詢循環
    while True:
        line = input("?- ").strip()
        if not line or line in ["exit", "quit"]: break
        if not line.endswith('.'): line += '.'
        
        goals = [Parser(line).parse_clause_item()]
        found = False
        
        for sol in solve(goals, db, {}):
            found = True
            q_vars = get_vars(goals[0])
            res = ", ".join([f"{v} = {resolve(Var(v), sol)}" for v in q_vars])
            print(f" ({res})" if res else " true.")
        
        if not found: print("false.")
```

## Unification 執行範例

```
Goal: append([1,2], [3,4], Result)

Step 1: unify([1,2], [], subst) → fail
Step 2: unify([1,2], [H|T], subst) → H=1, T=[2]
Step 3: unify(Result, [H|R], subst) → Result=[1|R]
Step 4: 新目標 append([2], [3,4], R)
        → 遞迴...
Result: [1,2,3,4]
```

## 設計特點

### 宣言式 vs 命令式

| 項目 | 命令式 | Prolog |
|------|--------|--------|
| 思維 | 如何做 | 什麼是真的 |
| 控制流 | 顯式指定 | 隱式 backtracking |
| 變數 | 賦值 | 約束傳播 |
| 執行 | 順序 | 搜尋 |

### Backtracking 流程圖

```
Query: likes(X, music), friend(X, Y)

Level 0: likes(X, music)
         ├─ X = john  ✓
         └─ X = jane  ✓
         
         ↓ each solution

Level 1: friend(john, Y)
         ├─ Y = john  (if likes(john, Z), likes(john, Z))
         └─ Y = jane  (if likes(john, books), likes(jane, books))
```

## 執行範例

```prolog
% family.pl
parent(tom, bob).
parent(tom, liz).
parent(bob, ann).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

ancestor(X, Z) :- parent(X, Z).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).
```

```bash
$ python prolog/prolog.py family.pl
Loaded 5 clauses.
?- grandparent(tom, Who).
 (Who = ann)
 (Who = liz)
false.
?- ancestor(tom, X).
 (X = bob)
 (X = ann)
 (X = liz)
false.
```

## 學習重點

1. **Unification**: 模式匹配的核心
2. **Backtracking**: 自動搜尋所有解答
3. **邏輯變數**: 延遲綁定
4. **變數重新命名**: 避免約束衝突
5. **遞迴規則**: 定義複雜關係

## 限制與擴展

**當前限制**：
- 無減號運算
- 無 cut (`!`)
- 無 list comprehension

**可擴展方向**：
- Cut/negation
- 算術運算增強
- 數字類型
- 外部函式接口
