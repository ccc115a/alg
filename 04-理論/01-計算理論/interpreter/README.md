# Interpreters 直譯器集合

本目錄收錄了五種不同程式語言的直譯器實作，展示多元化的語言設計風格與直譯器架構。

## 目錄

| 直譯器 | 語言 | 行數 | 特色 |
|--------|------|------|------|
| [basic/](basic/README.md) | BASIC | 129 | 行號導向、簡單直譯 |
| [js0i/](js0i/README.md) | JavaScript | 635 | 完整語法樹、Tree-walking |
| [lisp/](lisp/README.md) | Lisp | 101 | S-expression、元程式設計 |
| [prolog/](prolog/README.md) | Prolog | 280 | 模式比對、Backtracking |
| [py0i/](py0i/README.md) | Python | 1017 | AST 直譯、完整標準庫 |

## 設計原理總覽

### 1. 直譯器的基本架構

直譯器通常包含以下核心模組：

```
原始碼 → [Tokenizer/Lexer] → [Parser] → [AST/Bytecode] → [Evaluator] → 輸出
              (詞彙分析)        (語法分析)      (語意分析)      (執行)
```

### 2. 五種語言的設計典範

#### 基礎命令式 (BASIC)
- **範例**: 行號導向、逐行執行
- **直譯方式**: 直接解析執行，無中間表示
- **適用場景**: 教學、入門語言

#### 現代多範式 (JavaScript/Python)
- **範例**: 完整語法、類別系統、閉包
- **直譯方式**: 先建立 AST，再遍歷執行 (Tree-walking)
- **適用場景**: 生產力語言、Web 開發

#### 函數式 (Lisp)
- **範例**: S-expression、元程式設計
- **直譯方式**: 極簡語法、資料即程式
- **適用場景**: AI、符號計算、快速原型

#### 邏輯式 (Prolog)
- **範例**: 模式比對、變數 unification
- **直譯方式**: 宣告式、backtracking 搜尋
- **適用場景**: 專家系統、定理證明、自然語言處理

## 直譯器設計模式

### Environment (環境/作用域)

所有直譯器都需要管理變數的作用域：

```python
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(name)
```

### 信號機制 (Signals)

用於實現控制流（break、continue、return）：

```python
class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass
class ReturnSignal(Exception): pass
```

### 閉包 (Closure)

儲存函數建立時的環境：

```python
class Function:
    def __init__(self, params, body, closure_env):
        self.params = params
        self.body = body
        self.closure_env = closure_env
```

## 執行方式

```bash
# BASIC
python basic/basic.py program.bas

# JavaScript
node js0i/js0i.js script.js

# Lisp
python lisp/lisp.py program.lisp

# Prolog
python prolog/prolog.py program.pl

# Python (self-hosted)
python py0i/py0i.py script.py
```
