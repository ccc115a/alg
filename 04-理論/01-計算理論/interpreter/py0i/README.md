# Python 直譯器 (py0i)

py0i 是一個功能完整的 Python 直譯器，使用 Python 標準庫的 `ast` 模組解析程式碼，自己實現執行引擎。這是五個直譯器中最複雜的一個。

## 語言特色

- 完整的 Python 語法支援
- 類別與繼承
- 閉包與裝飾器
- 例外處理 (try/catch/finally)
- import 機制
- 列表/字典/集合推导式
- 切片與負索引
- 生成器與迭代器
- f-string 格式化

## 架構設計

```
Python 原始碼 → ast.parse() → AST → Interpreter.exec_module() → 結果
                    ↑              ↑
              標準庫提供       自己實現
```

### 1. 環境管理 (Environment)

```python
class Environment:
    def __init__(self, parent: 'Environment' = None) -> None:
        self.vars: dict = {}
        self.parent: 'Environment' = parent
    
    def get(self, name: str) -> object:
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"name '{name}' is not defined")
    
    def set(self, name: str, value: object) -> None:
        self.vars[name] = value
    
    def assign(self, name: str, value: object) -> None:
        """賦值給已存在的變數，或建立新變數"""
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent and self.parent._has(name):
            self.parent.assign(name, value)
            return
        self.vars[name] = value
```

**三層操作**：
- `set`: 僅在當前環境建立
- `assign`: 向上查找並修改或建立
- `assign_global`: 穿越到全域環境

### 2. 控制流信號

```python
class _ReturnBox:
    """用於傳遞 return 值的輕量 sentinel"""
    __slots__ = ('value',)
    def __init__(self, v): self.value = v

class ReturnSignal(Exception): pass
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
```

**為什麼用例外？** 
因為 return/break/continue 需要「跳躍」到外層語境，例外是最乾淨的實現方式。

### 3. 函式包裝 (PyFunction)

```python
class PyFunction:
    def __init__(self, node: object, closure_env: 'Environment',
                 interpreter: 'Interpreter') -> None:
        self.node = node              # ast.FunctionDef
        self.closure_env = closure_env
        self.interpreter = interpreter
        self.name = node.name
    
    def __call__(self, *args, **kwargs):
        func_env = Environment(parent=self.closure_env)
        
        # 處理預設參數
        defaults = [self.interpreter.eval_expr(d, self.closure_env)
                    for d in self.node.args.defaults]
        all_args = self.node.args.args
        n_defaults = len(defaults)
        default_start = len(all_args) - n_defaults
        
        # 綁定位置參數
        for i, arg in enumerate(all_args):
            if i < len(args):
                func_env.force_local(arg.arg, args[i])
            elif arg.arg in kwargs:
                func_env.force_local(arg.arg, kwargs[arg.arg])
            else:
                di = i - default_start
                if di >= 0:
                    func_env.force_local(arg.arg, defaults[di])
                else:
                    raise TypeError(f"missing required argument")
        
        # *args 和 **kwargs
        if self.node.args.vararg:
            func_env.force_local(
                self.node.args.vararg.arg,
                args[len(all_args):]
            )
        
        if self.node.args.kwarg:
            extra_kw = {k: v for k, v in kwargs.items()
                        if k not in {a.arg for a in all_args}}
            func_env.force_local(self.node.args.kwarg.arg, extra_kw)
        
        # 執行函式體
        for stmt in self.node.body:
            result = self.interpreter.exec_stmt(stmt, func_env)
            if isinstance(result, _ReturnBox):
                return result.value
        return None
```

### 4. 類別系統 (PyClass / PyInstance)

```python
class PyClass:
    def __init__(self, name: str, bases: list, namespace: dict) -> None:
        self.name = name
        self.bases = bases
        self.namespace = namespace
    
    def __call__(self, *args, **kwargs):
        instance = PyInstance(self)
        init = self._lookup('__init__')
        if init:
            init(instance, *args, **kwargs)
        return instance
    
    def _lookup(self, name: str) -> object:
        if name in self.namespace:
            return self.namespace[name]
        for base in self.bases:
            if isinstance(base, PyClass):
                found = base._lookup(name)
                if found is not None:
                    return found
        return None

class PyInstance:
    def __init__(self, cls: 'PyClass') -> None:
        self.__dict__['_cls'] = cls
        self.__dict__['_attrs'] = {}
    
    def __getattr__(self, name: str) -> object:
        attrs = object.__getattribute__(self, '_attrs')
        if name in attrs:
            return attrs[name]
        
        cls = object.__getattribute__(self, '_cls')
        found = cls._lookup(name)
        if found is not None:
            if isinstance(found, PyFunction):
                # 綁定方法
                def bound(*args, **kwargs):
                    return found(self, *args, **kwargs)
                return bound
            return found
        raise AttributeError(f"'{cls.name}' has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: object) -> None:
        self.__dict__['_attrs'][name] = value
```

**方法綁定**：存取 `instance.method` 時，自動將 `self` 作為第一個參數。

### 5. 語句執行器 (exec_stmt)

```python
def exec_stmt(self, node: object, env: 'Environment',
              global_names: set = None) -> None:
    t = type(node)
    
    if t is ast.Expr:
        self.eval_expr(node.value, env)
    
    elif t is ast.Assign:
        value = self.eval_expr(node.value, env)
        for target in node.targets:
            self.assign_target(target, value, env, global_names)
    
    elif t is ast.If:
        if self.eval_expr(node.test, env):
            for s in node.body:
                r = self.exec_stmt(s, env, global_names)
                if isinstance(r, _ReturnBox): return r
        else:
            for s in node.orelse:
                r = self.exec_stmt(s, env, global_names)
                if isinstance(r, _ReturnBox): return r
    
    elif t is ast.While:
        while self.eval_expr(node.test, env):
            try:
                for s in node.body:
                    r = self.exec_stmt(s, env, global_names)
                    if isinstance(r, _ReturnBox): return r
            except BreakSignal: break
            except ContinueSignal: continue
        # else clause
        for s in node.orelse:
            r = self.exec_stmt(s, env, global_names)
            if isinstance(r, _ReturnBox): return r
    
    elif t is ast.FunctionDef:
        fn = PyFunction(node, env, self)
        # 裝飾器
        for d in reversed(node.decorator_list):
            fn = self.eval_expr(d, env)(fn)
        if global_names and node.name in global_names:
            env.assign_global(node.name, fn)
        else:
            env.set(node.name, fn)
    
    elif t is ast.ClassDef:
        bases = [self.eval_expr(b, env) for b in node.bases]
        class_env = Environment(parent=env)
        for s in node.body:
            self.exec_stmt(s, class_env)
        cls = PyClass(node.name, bases, class_env.vars)
        env.set(node.name, cls)
    
    elif t is ast.Return:
        return _ReturnBox(
            self.eval_expr(node.value, env) if node.value else None
        )
    
    elif t is ast.Break:
        raise BreakSignal()
    
    elif t is ast.Continue:
        raise ContinueSignal()
    
    # ... 更多語句類型
```

### 6. 表達式求值器 (eval_expr)

```python
def eval_expr(self, node: object, env: 'Environment') -> object:
    t = type(node)
    
    if t is ast.Constant:
        return node.value
    
    elif t is ast.Name:
        return env.get(node.id)
    
    elif t is ast.Attribute:
        obj = self.eval_expr(node.value, env)
        return getattr(obj, node.attr)
    
    elif t is ast.BinOp:
        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)
        return self.apply_binop(node.op, left, right)
    
    elif t is ast.Call:
        func = self.eval_expr(node.func, env)
        args = [self.eval_expr(a, env) for a in node.args]
        return func(*args)
    
    elif t is ast.IfExp:  # 三元運算
        if self.eval_expr(node.test, env):
            return self.eval_expr(node.body, env)
        return self.eval_expr(node.orelse, env)
    
    elif t is ast.List:
        return [self.eval_expr(e, env) for e in node.elts]
    
    elif t is ast.Dict:
        return {self.eval_expr(k, env): self.eval_expr(v, env)
                for k, v in zip(node.keys, node.values)}
    
    elif t is ast.Subscript:
        obj = self.eval_expr(node.value, env)
        key = self.eval_subscript_key(node.slice, env)
        return obj[key]
    
    elif t is ast.ListComp:  # [x for x in range(10)]
        return self.eval_comprehension(list, node, env)
    
    elif t is ast.JoinedStr:  # f-string
        return ''.join(self._eval_fstring_part(v, env)
                        for v in node.values)
    
    # ... 更多表達式類型
```

### 7. 運算子映射

```python
def apply_binop(self, op: object, left: object, right: object) -> object:
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        # 位元運算
        ast.BitAnd: operator.and_,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshiftt,
    }
    return ops[type(op)](left, right)

def apply_cmpop(self, op: object, left: object, right: object) -> bool:
    ops = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.Gt: operator.gt,
        ast.Is: lambda a, b: a is b,
        ast.In: lambda a, b: a in b,
    }
    return ops[type(op)](left, right)
```

### 8. 內建函式

```python
def _setup_builtins(self) -> None:
    env = self.global_env
    builtins = {
        'print': self._builtin_print,
        'input': input,
        'len': len,
        'range': range,
        'int': int, 'float': float, 'str': str, 'bool': bool,
        'list': list, 'tuple': tuple, 'dict': dict, 'set': set,
        'type': type,
        'isinstance': self._builtin_isinstance,
        'abs': abs, 'max': max, 'min': min, 'sum': sum,
        'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
        'map': map, 'filter': filter,
        'chr': chr, 'ord': ord, 'hex': hex, 'oct': oct, 'bin': bin,
        'open': open, 'hasattr': hasattr, 'getattr': getattr,
        # ... 更多
    }
    for k, v in builtins.items():
        env.set(k, v)
```

### 9. 例外處理

```python
elif t is ast.Try:
    try:
        for s in node.body:
            r = self.exec_stmt(s, env, global_names)
            if isinstance(r, _ReturnBox): return r
    except (BreakSignal, ContinueSignal, ReturnSignal) as _ctrl:
        # 控制流訊號需要檢查是否有對應 handler
        ...
    except Exception as e:
        for handler in node.handlers:
            if handler.type is None:  # bare except
                for s in handler.body:
                    r = self.exec_stmt(s, env, global_names)
                    if isinstance(r, _ReturnBox): return r
                break
            exc_type = self.eval_expr(handler.type, env)
            if self._builtin_isinstance(e, exc_type):
                for s in handler.body:
                    r = self.exec_stmt(s, env, global_names)
                    if isinstance(r, _ReturnBox): return r
                break
    else:
        # no exception occurred
        for s in node.orelse: ...
    finally:
        for s in node.finalbody: ...
```

## 執行流程圖

```
import ast
      ↓
source = open('script.py').read()
      ↓
tree = ast.parse(source)
      ↓
interp = Interpreter()
      ↓
interp.exec_module(tree, global_env)
      ↓
for stmt in tree.body:
    exec_stmt(stmt)
      ↓
eval_expr(expr) ←→ exec_stmt(stmt)
      ↓
結果
```

## 執行範例

```python
# fact.py
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(10))

class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

p = Person("Alice")
print(p.greet())
```

```bash
$ python py0i/py0i.py fact.py
3628800
Hello, Alice!
```

## 設計特點

### 複雜度對比

| 功能 | BASIC | Lisp | Prolog | JS | Python |
|------|-------|------|--------|-----|--------|
| 行數 | 129 | 101 | 280 | 635 | 1017 |
| 函式 | ✗ | ✓ | ✗ | ✓ | ✓ |
| 類別 | ✗ | ✗ | ✗ | ✗ | ✓ |
| 閉包 | ✗ | ✓ | ✗ | ✓ | ✓ |
| 例外 | ✗ | ✗ | ✗ | ✓ | ✓ |
| import | ✗ | ✗ | ✗ | ✓ | ✓ |

### 技術亮點

1. **使用標準庫 ast**: 專注執行引擎
2. **類別系統**: 完整的繼承與方法綁定
3. **閉包**: 正確捕獲環境
4. **控制流信號**: 乾淨的跳躍機制
5. **內建函式橋接**: 直接使用 Python 標準庫

## 學習重點

1. **Tree-walking 直譯器**: 遍歷 AST 執行
2. **Environment 設計**: 作用域鏈
3. **類別實現**: MRO、實例屬性、方法綁定
4. **閉包原理**: 環境捕獲與引用
5. **例外機制**: try/catch/finally 實現
