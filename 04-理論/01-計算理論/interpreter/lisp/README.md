# Lisp 直譯器

這是一個極簡的 Lisp 直譯器，僅 101 行程式碼，展示了 Lisp 語言的核心理念：**程式即資料**。

## 語言特色

Lisp 的精髓在於 **S-expression**（符號表達式）：

```
(operator arg1 arg2 arg3 ...)
```

一切皆為列表，列表的第一個元素是操作符，其餘是參數。

## 語法結構

```lisp
; 條件判斷
(if condition then_expr else_expr)

; 定義函式
(defun factorial (n)
  (if (= n 0)
    1
    (* n (factorial (- n 1)))))

; 算術運算
(+ 1 2 3 4 5)  ; => 15

; 變數賦值
(defvar x 10)
```

## 架構設計

### 1. 極簡架構

```
原始碼 → Tokenize → Read → AST → Eval → 結果
         (空白分割)  (遞迴讀取)
```

### 2. Tokenizer (分詞器)

Lisp 的Tokenizer 極度簡潔：

```python
def tokenize(chars):
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()
```

**原理**：將 `(` 和 `)` 替換為獨立 token，然後按空白分割。

**範例**：
```
(if (> x 0) x (- x))
```
轉換為：
```
['(', 'if', '(', '>', 'x', '0', ')', 'x', '(', '-', 'x', ')', ')']
```

### 3. Parser (讀取器)

使用遞迴下降解析：

```python
def read_from_tokens(tokens):
    if not tokens: return None
    token = tokens.pop(0)
    
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # 移除 ')'
        return L
    else:
        return atom(token)
```

**核心思想**：
- 遇到 `(` → 遞迴建立列表
- 遇到 `)` → 返回當前列表
- 其他 → 轉換為原子（數字或符號）

### 4. 原子轉換

```python
def atom(token):
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)
```

自動識別整數、浮點數、符號。

### 5. Environment (環境)

```python
class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    
    def find(self, var):
        if var in self: return self
        if self.outer is None:
            raise NameError(f"Symbol '{var}' not found.")
        return self.outer.find(var)
```

**繼承式作用域**：`Env` 繼承自 `dict`，支援鏈式查找。

### 6. 標準環境

```python
def standard_env():
    env = Env()
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        '=': op.eq, '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le,
        'print': print, 'begin': lambda *x: x[-1]
    })
    return env

global_env = standard_env()
```

**內建函式**：算術、比較、print、begin。

### 7. 求值器 (Evaluator)

#### 程序類型

```python
class Procedure:
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    
    def __call__(self, *args):
        return eval_ast(self.body, Env(self.parms, args, self.env))
```

#### AST 求值

```python
def eval_ast(x, env=global_env):
    # 變數查詢
    if isinstance(x, str):
        return env.find(x)[x]
    
    # 數字直接返回
    if not isinstance(x, list):
        return x
    
    # 解構操作符與參數
    op_name, *args = x
    
    # 特殊形式
    if op_name == 'if':
        test, conseq, alt = args
        exp = conseq if eval_ast(test, env) else alt
        return eval_ast(exp, env)
    
    if op_name == 'defun':
        name, parms, body = args
        env[name] = Procedure(parms, body, env)
        return name
    
    # 函式呼叫
    proc = eval_ast(op_name, env)
    vals = [eval_ast(arg, env) for arg in args]
    return proc(*vals)
```

### 8. 主執行流程

```python
def run_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        script = f.read()
    
    # 包裝在 (begin ...) 中支援多表達式
    tokens = tokenize(f"(begin {script} )")
    ast = read_from_tokens(tokens)
    eval_ast(ast)
```

## 程式碼流程圖

```
使用者輸入:
    (defun add (x y) (+ x y))
    (print (add 1 2))

Tokens:
    ['(', 'defun', 'add', '(', 'x', 'y', ')', '(', '+', 'x', 'y', ')', ')']

AST:
    ['begin',
        ['defun', 'add', ['x', 'y'], ['+', 'x', 'y']],
        ['print', ['add', 1, 2]]]

求值:
    1. eval(['defun', ...]) → 創建 Procedure 加入 env
    2. eval(['print', ...]) → 呼叫 print
       └─ eval(['add', 1, 2])
          └─ proc(1, 2) → eval(['+', 1, 2]) → 3

輸出: 3
```

## 設計特點

### 極簡設計

| 特性 | 實現方式 |
|------|----------|
| Tokenizer | 字串替換 + split |
| Parser | 20 行遞迴函式 |
| AST | Python 原生列表 |
| 求值器 | 模式匹配 |

### 特殊形式 vs 函式呼叫

Lisp 只有少數**特殊形式**需要特殊處理：

```python
if op_name == 'if':      # 需要短路求值
if op_name == 'defun':  # 修改環境
if op_name == 'quote':  # 阻止求值
```

其他都是普通函式呼叫。

### 閉包實現

```python
class Procedure:
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env  # 保存建立時的環境
    
    def __call__(self, *args):
        # 新環境繼承閉包環境
        return eval_ast(self.body, Env(self.parms, args, self.env))
```

## 執行範例

```lisp
; factorial.lisp
(defun factorial (n)
  (if (= n 0)
    1
    (* n (factorial (- n 1)))))

(print (factorial 5))
```

```bash
$ python lisp/lisp.py factorial.lisp
120
```

## 學習重點

1. **S-expression 的優雅**: 極簡語法，強大表達力
2. **程式即資料**: AST 就是列表結構
3. **特殊形式**: 需要特殊處理的語法
4. **閉包**: 環境捕獲
5. **元程式設計潛力**: 可操作自己的程式碼

## 擴展方向

當前實現是「微語言」(Toy Lisp)，可擴展方向：

- **quote / quasiquote**: 阻止求值
- **let**: 區域綁定
- **cond**: 多分支
- **macro**: 編譯時計算
- **尾遞迴優化**: TCO
