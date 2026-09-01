# JavaScript 直譯器 (js0i)

js0i 是一個完整的 JavaScript ES6 直譯器，採用經典的 Tree-walking 架構，支援現代 JavaScript 的大部分特性。

## 語言特色

- 完整的表達式解析（運算子優先順序）
- 函式宣告與表達式
- 箭頭函式 `=>`
- 類別語法
- try/catch/finally 例外處理
- 陣列與物件字面量
- `for...in` / `for...of` 迴圈

## 架構設計

```
原始碼 → Tokenizer → Parser → AST → Evaluator → 結果
```

### 1. Tokenizer (詞彙分析器)

將原始碼字串轉換為 Token 串列：

```javascript
function tokenize(src) {
  var toks = [];
  var i = 0;
  while (i < len) {
    var c = src[i];
    
    // 空白忽略
    if (c === ' ' || c === '\t') { i++; continue; }
    
    // 註解
    if (c === '/' && src[i+1] === '/') { ... }
    
    // 數字 (含 0x, 0b, 0o)
    if (isDigit(c)) { ... }
    
    // 字串
    if (c === '"' || c === "'") { ... }
    
    // 識別符
    if (isAlpha(c)) { ... }
    
    // 運算子
    if ('+-*/%=<>!&|^~?:.;,(){}[]'.indexOf(c)>=0) { ... }
  }
  toks.push({t:'E',v:''}); // End token
  return toks;
}
```

**Token 類型**：
- `N`: 數字 (Number)
- `S`: 字串 (String)
- `I`: 識別符 (Identifier)
- `P`: 標點符號 (Punctuation)
- `E`: 結束 (End)

### 2. Parser (語法分析器)

#### 運算子優先順序解析

使用 **Pratt Parser** (Top-down Operator Precedence)：

```javascript
var PREC = {
  '||':1, '&&':2, '|':3, '^':4, '&':5,
  '==':6, '!=':6, '<':7, '>':7, '+':9, '-':9, '*':10, '/':10, '**':11
};

Parser.prototype.parseBin = function(minP) {
  var left = this.parseUnary();
  while(true) {
    var p = this.getPrec();
    if(p < minP) break;
    var op = this.nx().v;
    var right = this.parseBin(p + (op === '**' ? 0 : 1));
    left = {type:'Binary', op:op, left:left, right:right};
  }
  return left;
};
```

**核心思想**：每個運算子有自己的「綁定強度」(precedence)，較強的運算子先結合。

#### 表達式解析層次

```
parseExpr()
  └─ parseAssign()         // =, +=, -=, ...
      └─ parseTernary()    // ?:
          └─ parseBin()     // +, -, *, /, &&, ||, ...
              └─ parseUnary()  // !, -, ++, --, typeof, delete
                  └─ parsePostfix()  // ++, --
                      └─ parseCallMember()
                          └─ parsePrimary()  // literals, identifiers
```

#### 語句解析

```javascript
Parser.prototype.parseStmt = function() {
  if (this.at('P','{')) return this.parseBlock();
  if (this.at('I','var')) return this.parseVarDecl(true);
  if (this.at('I','function')) return this.parseFuncDecl();
  if (this.at('I','if')) return this.parseIf();
  if (this.at('I','while')) return this.parseWhile();
  if (this.at('I','for')) return this.parseFor();
  // ...
};
```

### 3. AST 節點類型

| 類型 | 說明 | 結構 |
|------|------|------|
| `Prog` | 程式 | `{type:'Prog', body:[stmts]}` |
| `Block` | 區塊 | `{type:'Block', body:[stmts]}` |
| `Var` | 變數宣告 | `{type:'Var', kind:'let', decls:[{name, init}]}` |
| `FuncDecl` | 函式宣告 | `{type:'FuncDecl', name, params, body}` |
| `If` | 條件 | `{type:'If', test, cons, alt}` |
| `While` | 迴圈 | `{type:'While', test, body}` |
| `For` | 計數迴圈 | `{type:'For', init, test, update, body}` |
| `Binary` | 二元運算 | `{type:'Binary', op, left, right}` |
| `Call` | 函式呼叫 | `{type:'Call', callee, args}` |
| `Member` | 成員存取 | `{type:'Member', obj, prop, computed}` |

### 4. Evaluator (求值器)

#### Environment (環境鏈)

```javascript
function Env(parent) {
  this.parent = parent;
  this.vars = {};
}

Env.prototype.get = function(n) {
  if (this.vars.hasOwnProperty(n)) return this.vars[n];
  if (this.parent) return this.parent.get(n);
  throw new ReferenceError(n + ' is not defined');
};

Env.prototype.set = function(n, v) {
  if (this.vars.hasOwnProperty(n)) { this.vars[n] = v; return; }
  if (this.parent) { this.parent.set(n, v); return; }
  throw new ReferenceError(n + ' is not defined');
};
```

**作用域鏈**：當查詢變數時，先在當前環境尋找，找不到則沿著 `parent` 向上查找。

#### 信號機制 (Signals)

用於實現控制流：

```javascript
var SIG = {};
function RetSig(v) { this.s = SIG; this.v = v; }
function BrkSig(l) { this.s = SIG; this.l = l; }
function ContSig(l) { this.s = SIG; this.l = l; }
function isSig(e) { return e !== null && typeof e === 'object' && e.s === SIG; }
```

#### 函式建立

```javascript
function makeFunc(name, params, bodyNode, closureEnv) {
  var fn = function() {
    var localEnv = new Env(closureEnv);
    localEnv.def('this', this);
    var argsArr = [];
    for (var i = 0; i < arguments.length; i++) argsArr.push(arguments[i]);
    localEnv.def('arguments', argsArr);
    for (var i = 0; i < params.length; i++) {
      localEnv.def(params[i], i < argsArr.length ? argsArr[i] : undefined);
    }
    try { evalBody(bodyNode.body, localEnv); }
    catch(e) { if (e instanceof RetSig) return e.v; throw e; }
    return undefined;
  };
  // ...
  return fn;
}
```

**閉包關鍵**：`closureEnv` 保存了函式建立時的環境，形成閉包。

#### 遍歷執行

```javascript
function evalNode(node, env) {
  var tp = node.type;
  
  if (tp === 'Prog' || tp === 'Block') {
    evalBody(node.body, tp === 'Block' ? new Env(env) : env);
    return;
  }
  
  if (tp === 'If') {
    if (evalExpr(node.test, env)) evalNode(node.cons, env);
    else if (node.alt) evalNode(node.alt, env);
    return;
  }
  
  if (tp === 'While') {
    while (evalExpr(node.test, env)) {
      try { evalNode(node.body, env); }
      catch(e) {
        if (e instanceof ContSig) continue;
        if (e instanceof BrkSig) break;
        throw e;
      }
    }
    return;
  }
  
  // ... 更多節點類型
}
```

### 5. 全域環境

```javascript
function makeGlobal(argv) {
  var env = new Env(null);
  env.def('undefined', undefined);
  env.def('console', {
    log: function() { console.log.apply(console, arguments); }
  });
  env.def('Math', Math);
  env.def('JSON', JSON);
  env.def('require', function(name) {
    if (name === 'fs') return fs;
    // ...
  });
  // ...
  return env;
}
```

## 設計特點

### 優點
- **完整語法支援**: 涵蓋 ES6 大部分特性
- **Pratt Parser**: 高效的運算子優先順序處理
- **閉包實現**: 正確的作用域鏈
- **信號機制**: 優雅的控制流

### 技術亮點

1. **貪心匹配**: Tokenizer 優先匹配長運算子 (`===`, `!==`)
2. **雙向遍歷**: 成員存取 (`a.b.c`) 支援點號與括號
3. **Try/Catch**: 使用 JavaScript 原生例外機制

## 執行範例

```javascript
// factorial.js
function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

console.log(factorial(5)); // 120
```

```bash
$ node js0i/js0i.js factorial.js
120
```

## 學習重點

1. **Tree-walking 直譯器模式**
2. **Pratt Parser 演算法**
3. **Environment 作用域管理**
4. **閉包的實現原理**
5. **AST 遍歷模式**
