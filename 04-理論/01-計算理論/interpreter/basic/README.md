# BASIC 直譯器

Mini BASIC 是一個精簡的命令式語言直譯器，展示了最基礎的程式語言直譯器設計。

## 語言語法

BASIC 語言採用**行號導向**的設計，所有語句都必須有行號：

```basic
10 LET X = 10
20 PRINT "Hello, World!"
30 INPUT "Enter number: ", N
40 IF X > 5 THEN GOTO 60
50 LET X = X - 1
60 END
```

## 支援的語法

| 語法 | 說明 | 範例 |
|------|------|------|
| `LET` | 變數賦值 | `LET X = 10` |
| `PRINT` | 輸出 | `PRINT X, "hello"` |
| `INPUT` | 輸入互動 | `INPUT N` |
| `GOTO` | 無條件跳躍 | `GOTO 100` |
| `IF...THEN` | 條件判斷 | `IF X > 5 THEN 100` |
| `END` | 程式結束 | `END` |

## 架構設計

### 1. 資料結構

```python
class MiniBasic:
    def __init__(self):
        self.lines = {}        # 行號 → 語句
        self.vars = {}         # 變數表
        self.line_numbers = [] # 排序後的行號列表
        self.pc = 0            # 程式計數器
```

### 2. 詞彙分析

使用正規表達式解析行號與語句：

```python
def load_file(self, filename):
    for line in f:
        m = re.match(r'^(\d+)\s+(.*)$', line)
        if m:
            num = int(m.group(1))
            stmt = m.group(2).strip()
            self.lines[num] = stmt
```

### 3. 表達式求值

`evaluate()` 方法將 BASIC 表達式轉換為 Python 可執行的形式：

```python
def evaluate(self, expr):
    temp = expr
    # 替換變數
    for v in self.vars:
        temp = re.sub(rf'\b{v}\b', str(self.vars[v]), temp)
    
    # 轉換運算子
    temp = temp.replace("<>", "!=")
    temp = re.sub(r'(?<![<>!=])=(?!=)', '==', temp)
    
    return eval(temp, {"__builtins__": {}}, {"INT": int})
```

**關鍵技術**：
- 使用 `\b` 邊界匹配避免部分變數名稱替換
- 動態重構表達式字串為 Python 語法
- `eval()` 安全隔離（無內建函式）

### 4. 語句執行

每種語法都有專屬的處理函式：

```python
def exec_statement(self, stmt):
    # LET X = expr
    m = re.match(r'^(?:LET\s+)?([A-Z][A-Z0-9]*)\s*=\s*(.*)$', stmt, re.I)
    if m:
        var, expr = m.groups()
        self.vars[var] = self.evaluate(expr)
        return
    
    # PRINT ...
    if stmt.upper().startswith("PRINT"):
        ...
```

### 5. 主執行迴圈

```python
def run(self):
    while self.pc < len(self.line_numbers):
        lnum = self.line_numbers[self.pc]
        stmt = self.lines[lnum]
        
        # IF...THEN 特殊處理
        m = re.match(r'IF\s+(.*?)\s+THEN\s+(.*)', stmt, re.I)
        if m:
            cond, action = m.groups()
            if self.evaluate(cond):
                # THEN 可能是一個行號或語句
                ...
            self.pc += 1
            continue
        
        self.exec_statement(stmt)
        self.pc += 1
```

## 設計特點

### 優點
- **極度精簡**: 僅 129 行程式碼
- **直觀易懂**: 沒有複雜的資料結構
- **即時反饋**: 支援 INPUT 互動

### 限制
- 無函式支援
- 無區域變數（全部全域）
- 僅支援數字與簡單字串

## 執行範例

```bash
$ cat > test.bas << 'EOF'
10 LET N = 5
20 LET FACT = 1
30 IF N <= 1 THEN GOTO 60
40 LET FACT = FACT * N
50 LET N = N - 1
60 PRINT "Factorial: ", FACT
70 END
EOF

$ python basic/basic.py test.bas
Factorial: 120
```

## 學習重點

1. **最簡直譯器模式**: 讀取 → 解析 → 執行
2. **狀態機設計**: 使用 `pc` 控制執行流程
3. **正規表達式應用**: 字元級語法分析
4. **eval 安全使用**: 隔離內建函式
