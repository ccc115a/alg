"""
ast.py  –  手寫的 Python Lexer + Parser
產生與 cpython ast 相容的節點物件，供 py0i.py 使用。
完全不依賴標準函式庫的 ast 模組。
"""

# ══════════════════════════════════════════════════════════════════════════════
# 1.  AST 節點基礎類別
# ══════════════════════════════════════════════════════════════════════════════

class AST:
    """所有 AST 節點的共同基礎。"""
    _fields: tuple = ()

    def __init__(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        args: str = ', '.join(f'{f}={getattr(self, f, None)!r}' for f in self._fields)
        return f'{self.__class__.__name__}({args})'


# ── 節點工廠 (讓 isinstance 可用) ─────────────────────────────────────────────
def _node(name: str, *fields: str) -> type:
    return type(name, (AST,), {'_fields': fields})


# ── Module ────────────────────────────────────────────────────────────────────
Module        = _node('Module',       'body', 'type_ignores')

# ── Statements ───────────────────────────────────────────────────────────────
Expr          = _node('Expr',         'value')
Assign        = _node('Assign',       'targets', 'value', 'type_comment')
AugAssign     = _node('AugAssign',    'target', 'op', 'value')
AnnAssign     = _node('AnnAssign',    'target', 'annotation', 'value', 'simple')
Return        = _node('Return',       'value')
Delete        = _node('Delete',       'targets')
Pass          = _node('Pass')
Break         = _node('Break')
Continue      = _node('Continue')
Raise         = _node('Raise',        'exc', 'cause')
Assert        = _node('Assert',       'test', 'msg')
Global        = _node('Global',       'names')
Nonlocal      = _node('Nonlocal',     'names')
Import        = _node('Import',       'names')
ImportFrom    = _node('ImportFrom',   'module', 'names', 'level')
If            = _node('If',           'test', 'body', 'orelse')
While         = _node('While',        'test', 'body', 'orelse')
For           = _node('For',          'target', 'iter', 'body', 'orelse', 'type_comment')
With          = _node('With',         'items', 'body', 'type_comment')
Try           = _node('Try',          'body', 'handlers', 'orelse', 'finalbody')
FunctionDef   = _node('FunctionDef',  'name', 'args', 'body', 'decorator_list', 'returns', 'type_comment')
AsyncFunctionDef = _node('AsyncFunctionDef', 'name', 'args', 'body', 'decorator_list', 'returns', 'type_comment')
ClassDef      = _node('ClassDef',     'name', 'bases', 'keywords', 'body', 'decorator_list')

# ── Exception handler ─────────────────────────────────────────────────────────
ExceptHandler = _node('ExceptHandler','type', 'name', 'body')

# ── With item ─────────────────────────────────────────────────────────────────
withitem      = _node('withitem',     'context_expr', 'optional_vars')

# ── Expressions ───────────────────────────────────────────────────────────────
Constant      = _node('Constant',     'value', 'kind')
Name          = _node('Name',         'id', 'ctx')
Attribute     = _node('Attribute',    'value', 'attr', 'ctx')
Subscript     = _node('Subscript',    'value', 'slice', 'ctx')
Starred       = _node('Starred',      'value', 'ctx')
NamedExpr     = _node('NamedExpr',    'target', 'value')
BinOp         = _node('BinOp',        'left', 'op', 'right')
UnaryOp       = _node('UnaryOp',      'op', 'operand')
BoolOp        = _node('BoolOp',       'op', 'values')
Compare       = _node('Compare',      'left', 'ops', 'comparators')
Call          = _node('Call',         'func', 'args', 'keywords')
IfExp         = _node('IfExp',        'test', 'body', 'orelse')
Lambda        = _node('Lambda',       'args', 'body')
JoinedStr     = _node('JoinedStr',    'values')
FormattedValue= _node('FormattedValue','value', 'conversion', 'format_spec')
List          = _node('List',         'elts', 'ctx')
Tuple         = _node('Tuple',        'elts', 'ctx')
Set           = _node('Set',          'elts')
Dict          = _node('Dict',         'keys', 'values')
Slice         = _node('Slice',        'lower', 'upper', 'step')
ListComp      = _node('ListComp',     'elt', 'generators')
SetComp       = _node('SetComp',      'elt', 'generators')
DictComp      = _node('DictComp',     'key', 'value', 'generators')
GeneratorExp  = _node('GeneratorExp', 'elt', 'generators')
comprehension = _node('comprehension','target', 'iter', 'ifs', 'is_async')
Yield         = _node('Yield',        'value')
YieldFrom     = _node('YieldFrom',    'value')
Await         = _node('Await',        'value')

# ── Function arguments ────────────────────────────────────────────────────────
arguments     = _node('arguments',    'posonlyargs', 'args', 'vararg',
                                      'kwonlyargs', 'kw_defaults', 'kwarg', 'defaults')
arg           = _node('arg',          'arg', 'annotation', 'type_comment')
keyword       = _node('keyword',      'arg', 'value')
alias         = _node('alias',        'name', 'asname')

# ── Operators ─────────────────────────────────────────────────────────────────
Add      = _node('Add')
Sub      = _node('Sub')
Mult     = _node('Mult')
Div      = _node('Div')
FloorDiv = _node('FloorDiv')
Mod      = _node('Mod')
Pow      = _node('Pow')
BitAnd   = _node('BitAnd')
BitOr    = _node('BitOr')
BitXor   = _node('BitXor')
LShift   = _node('LShift')
RShift   = _node('RShift')
MatMult  = _node('MatMult')
UAdd     = _node('UAdd')
USub     = _node('USub')
Not      = _node('Not')
Invert   = _node('Invert')
And      = _node('And')
Or       = _node('Or')
Eq       = _node('Eq')
NotEq    = _node('NotEq')
Lt       = _node('Lt')
LtE      = _node('LtE')
Gt       = _node('Gt')
GtE      = _node('GtE')
Is       = _node('Is')
IsNot    = _node('IsNot')
In       = _node('In')
NotIn    = _node('NotIn')

# Context singletons
Load  = _node('Load')()
Store = _node('Store')()
Del   = _node('Del')()

# ── walk (needed by py0i) ─────────────────────────────────────────────────────
def walk(node: 'AST') -> 'object':
    """廣度優先走訪所有子節點。"""
    from collections import deque
    q: object = deque([node])
    while q:
        cur: object = q.popleft()
        yield cur
        if isinstance(cur, AST):
            for f in cur._fields:
                child = getattr(cur, f, None)
                if isinstance(child, AST):
                    q.append(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST):
                            q.append(item)

# ── copy_location ─────────────────────────────────────────────────────────────
def copy_location(new_node: 'AST', old_node: 'AST') -> 'AST':
    for attr in ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'):
        if hasattr(old_node, attr):
            setattr(new_node, attr, getattr(old_node, attr))
    return new_node


# ══════════════════════════════════════════════════════════════════════════════
# 2.  Lexer
# ══════════════════════════════════════════════════════════════════════════════

import re

# Token 種類
TK = type('TK', (), {
    'NUM':    'NUM',
    'STR':    'STR',
    'NAME':   'NAME',
    'NEWLINE':'NEWLINE',
    'INDENT': 'INDENT',
    'DEDENT': 'DEDENT',
    'OP':     'OP',
    'EOF':    'EOF',
    'COMMENT':'COMMENT',
    'NL':     'NL',       # 空白行的換行（不產生 NEWLINE token）
})

KEYWORDS: frozenset = frozenset([
    'False','None','True','and','as','assert','async','await',
    'break','class','continue','def','del','elif','else','except',
    'finally','for','from','global','if','import','in','is',
    'lambda','nonlocal','not','or','pass','raise','return',
    'try','while','with','yield',
])

class Token:
    def __init__(self, kind: str, value: str, line: int = 0, col: int = 0) -> None:
        self.kind:  str = kind
        self.value: str = value
        self.line:  int = line
        self.col:   int = col

    def __repr__(self) -> str:
        return f'Token({self.kind}, {self.value!r}, L{self.line})'


def _tokenize(source: str) -> list:
    """
    手寫 tokenizer，產生 Token 串列。
    處理：縮排/DEDENT、字串（含三引號、f-string）、數字、運算子。
    """
    tokens: list       = []
    lines: list        = source.splitlines(keepends=True)
    indent_stack: list = [0]
    paren_depth: int   = 0   # () [] {} 裡面的換行不算 NEWLINE

    # ── 字串 pattern ──────────────────────────────────────────────────────────
    # 三引號要先比對
    STR_PAT = re.compile(
        r'(?:'
        # 三引號字串（可含前綴 r/b/f/u）
        r'(?:[rRbBuUfF]{0,2}"""[\s\S]*?""")'
        r'|(?:[rRbBuUfF]{0,2}' + r"'''[\s\S]*?''')"
        # 單引號字串
        r"|(?:[rRbBuUfF]{0,2}'(?:[^'\\\n]|\\.)*')"
        r'|(?:[rRbBuUfF]{0,2}"(?:[^"\\\n]|\\.)*")'
        r')'
    )

    NUM_PAT = re.compile(
        r'0[xX][0-9a-fA-F_]+'        # hex
        r'|0[bB][01_]+'               # bin
        r'|0[oO][0-7_]+'              # oct
        r'|(?:\d[\d_]*\.[\d_]*(?:[eE][+-]?\d+)?j?'  # float
        r'|\.\d[\d_]*(?:[eE][+-]?\d+)?j?'          # 小數點後需有數字，避免 '._' 誤判
        r'|\d[\d_]*[eE][+-]?\d+j?'
        r'|\d[\d_]*j'                 # complex
        r'|\d[\d_]*)'                 # int
    )

    # 多字元運算子要先列（長的先）
    OPS = [
        ':=','**=','//=','>>=','<<=',
        '+=','-=','*=','/=','%=','&=','|=','^=','@=',
        '**','//','>>', '<<', '<=', '>=', '==', '!=', '->',
        '+','-','*','/','%','&','|','^','~','<','>','=',
        '(',')','{','}','[',']',',',':','...','.',  # '...' 必須在 '.' 前
        '@',';','!','\\',
    ]
    OP_RE = re.compile('|'.join(re.escape(o) for o in OPS))

    # ── 逐行掃描 ──────────────────────────────────────────────────────────────
    # 把整個 source 當成一個字串流，記錄行號
    pos:    int = 0
    lnum:   int = 1
    lstart: int = 0          # 目前行的起始 pos
    src:    str = source

    def cur_col() -> int:
        return pos - lstart

    def emit(kind: str, val: str, ln: int = None, co: int = None) -> None:
        tokens.append(Token(kind, val, ln or lnum, co if co is not None else cur_col()))

    # ── 主迴圈 ────────────────────────────────────────────────────────────────
    while pos < len(src):
        # ── 行首縮排處理 ───────────────────────────────────────────────────────
        # 只有在頂層（paren_depth==0）且位於行首才計算縮排
        if pos == lstart:
            # 計算縮排寬度
            indent = 0
            p2 = pos
            while p2 < len(src) and src[p2] in ' \t':
                indent += 4 if src[p2] == '\t' else 1
                p2 += 1

            # 跳過空白行 / 純注解行
            if p2 < len(src) and src[p2] in '\r\n':
                # 空白行
                pos = p2
                # 讓後面的 \n 處理負責推進 lnum
            elif p2 < len(src) and src[p2] == '#':
                # 整行注解，跳過
                while pos < len(src) and src[pos] not in '\r\n':
                    pos += 1
            else:
                # 真正有內容的行，處理縮排
                if paren_depth == 0:
                    top = indent_stack[-1]
                    if indent > top:
                        indent_stack.append(indent)
                        emit(TK.INDENT, indent)
                    elif indent < top:
                        while indent_stack and indent_stack[-1] > indent:
                            indent_stack.pop()
                            emit(TK.DEDENT, indent)
                        if indent_stack[-1] != indent:
                            raise IndentationError(f"unindent does not match at line {lnum}")
                pos = p2   # 跳過縮排空白

        if pos >= len(src):
            break

        c = src[pos]

        # ── 換行 ─────────────────────────────────────────────────────────────
        if c in '\r\n':
            nl = '\r\n' if src[pos:pos+2] == '\r\n' else c
            if paren_depth == 0:
                emit(TK.NEWLINE, nl)
            else:
                emit(TK.NL, nl)
            pos += len(nl)
            lnum += 1
            lstart = pos
            continue

        # ── 反斜線接續 ───────────────────────────────────────────────────────
        if c == '\\':
            if pos+1 < len(src) and src[pos+1] in '\r\n':
                nl = '\r\n' if src[pos+1:pos+3] == '\r\n' else src[pos+1]
                pos += 1 + len(nl)
                lnum += 1
                lstart = pos
                continue
            else:
                pos += 1
                continue

        # ── 注解 ─────────────────────────────────────────────────────────────
        if c == '#':
            while pos < len(src) and src[pos] not in '\r\n':
                pos += 1
            continue

        # ── 空白 ─────────────────────────────────────────────────────────────
        if c in ' \t':
            while pos < len(src) and src[pos] in ' \t':
                pos += 1
            continue

        # ── 字串（含 f-string）────────────────────────────────────────────────
        m = STR_PAT.match(src, pos)
        if m:
            raw = m.group(0)
            co  = cur_col()
            # 記錄字串跨越多少行
            newlines = raw.count('\n')
            emit(TK.STR, raw, lnum, co)
            pos += len(raw)
            lnum += newlines
            if newlines:
                lstart = pos - (len(raw) - raw.rfind('\n') - 1)
            continue

        # ── 數字 ─────────────────────────────────────────────────────────────
        m = NUM_PAT.match(src, pos)
        if m:
            emit(TK.NUM, m.group(0))
            pos += m.end() - m.start()
            continue

        # ── 識別字 / 關鍵字 ───────────────────────────────────────────────────
        if c.isidentifier():
            end = pos + 1
            while end < len(src) and (src[end].isidentifier() or src[end].isdigit()):
                end += 1
            word = src[pos:end]
            co = cur_col()
            emit(TK.NAME, word, lnum, co)
            pos = end
            continue

        # ── 運算子 ────────────────────────────────────────────────────────────
        m = OP_RE.match(src, pos)
        if m:
            op = m.group(0)
            co = cur_col()
            emit(TK.OP, op, lnum, co)
            if op in '([{':
                paren_depth += 1
            elif op in ')]}':
                paren_depth -= 1
            pos += len(op)
            continue

        raise SyntaxError(f"unexpected character {c!r} at line {lnum}, col {cur_col()}")

    # 補上尾部 DEDENT
    while len(indent_stack) > 1:
        indent_stack.pop()
        emit(TK.DEDENT, 0)

    emit(TK.EOF, '')
    return tokens


# ══════════════════════════════════════════════════════════════════════════════
# 3.  Parser
# ══════════════════════════════════════════════════════════════════════════════

class _Parser:
    def __init__(self, tokens: list) -> None:
        self.tokens: list = tokens
        self.pos:    int  = 0

    # ── token 操作 ────────────────────────────────────────────────────────────

    def peek(self, offset: int = 0) -> 'Token':
        p: int = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]   # EOF

    def cur(self) -> 'Token':
        return self.peek(0)

    def advance(self) -> 'Token':
        t: 'Token' = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def eat(self, kind: str, value: str = None) -> 'Token':
        t: 'Token' = self.cur()
        if t.kind != kind or (value is not None and t.value != value):
            exp = f'{kind}({value!r})' if value else kind
            raise SyntaxError(
                f'expected {exp} but got {t.kind}({t.value!r}) at line {t.line}')
        return self.advance()

    def match(self, kind: str, value: str = None) -> 'Token':
        t: 'Token' = self.cur()
        if t.kind == kind and (value is None or t.value == value):
            return self.advance()
        return None

    def skip_newlines(self) -> None:
        while self.cur().kind in (TK.NEWLINE, TK.NL):
            self.advance()

    def skip_nl(self) -> None:
        """括號內換行（NL）跳過，不跳過頂層 NEWLINE。"""
        while self.cur().kind == TK.NL:
            self.advance()

    def is_op(self, *ops: str) -> bool:
        return self.cur().kind == TK.OP and self.cur().value in ops

    def is_name(self, *names: str) -> bool:
        return self.cur().kind == TK.NAME and self.cur().value in names

    def is_keyword(self, *kws: str) -> bool:
        return self.cur().kind == TK.NAME and self.cur().value in kws

    # ── 頂層 ──────────────────────────────────────────────────────────────────

    def parse_module(self) -> 'AST':
        self.skip_newlines()
        body: list = []
        while self.cur().kind != TK.EOF:
            stmts = self.parse_stmt()
            body.extend(stmts)
            self.skip_newlines()
        return Module(body=body, type_ignores=[])

    # ── 語句 ──────────────────────────────────────────────────────────────────

    def parse_stmt(self) -> list:
        """回傳語句清單（同一行可能有多個用分號分隔）。"""
        t: 'Token' = self.cur()

        # 複合語句
        if t.kind == TK.NAME:
            kw = t.value
            if kw == 'if':     return [self.parse_if()]
            if kw == 'while':  return [self.parse_while()]
            if kw == 'for':    return [self.parse_for()]
            if kw == 'try':    return [self.parse_try()]
            if kw == 'with':   return [self.parse_with()]
            if kw in ('def', 'async'): return [self.parse_funcdef()]
            if kw == 'class':  return [self.parse_classdef()]
            if kw == 'return': return [self.parse_return()]
            if kw == 'raise':  return [self.parse_raise()]
            if kw == 'del':    return [self.parse_del()]
            if kw == 'pass':
                self.advance()
                self._eat_stmt_end()
                return [Pass()]
            if kw == 'break':
                self.advance()
                self._eat_stmt_end()
                return [Break()]
            if kw == 'continue':
                self.advance()
                self._eat_stmt_end()
                return [Continue()]
            if kw == 'global':   return [self.parse_global()]
            if kw == 'nonlocal': return [self.parse_nonlocal()]
            if kw == 'import':   return [self.parse_import()]
            if kw == 'from':     return [self.parse_from_import()]
            if kw == 'assert':   return [self.parse_assert()]
            if kw == 'yield':
                expr = self.parse_expr()
                self._eat_stmt_end()
                return [Expr(value=expr)]

        # INDENT block は呼び出し元で処理
        if t.kind == TK.INDENT:
            raise SyntaxError(f"unexpected indent at line {t.line}")

        # 簡單語句（賦值 or 表達式）
        return self.parse_simple_stmt()

    def parse_simple_stmt(self) -> list:
        """一行可含多個 ; 分隔的語句。"""
        stmts: list = [self._parse_one_simple()]
        while self.is_op(';'):
            self.advance()
            if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF):
                break
            stmts.append(self._parse_one_simple())
        self._eat_stmt_end()
        return stmts

    def _parse_one_simple(self) -> 'AST':
        """解析單一簡單語句（賦值 / AugAssign / AnnAssign / Expr）。"""
        exprs: list = [self.parse_expr()]

        # 可能是 tuple 的逗號
        while self.is_op(','):
            self.advance()
            if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF, TK.OP) \
               and self.cur().value in (')', ']', '}', ';', ':'):
                # trailing comma
                exprs.append(None)
                break
            exprs.append(self.parse_expr())

        target_expr = exprs[0] if len(exprs) == 1 else \
                      Tuple(elts=exprs, ctx=Store)

        # AugAssign  +=  -=  …
        aug_ops = {
            '+=': Add(),  '-=': Sub(),   '*=': Mult(),  '/=': Div(),
            '//=':FloorDiv(), '%=': Mod(), '**=': Pow(),
            '&=': BitAnd(), '|=': BitOr(), '^=': BitXor(),
            '>>=':RShift(), '<<=':LShift(), '@=': MatMult(),
        }
        if self.cur().kind == TK.OP and self.cur().value in aug_ops:
            op = aug_ops[self.advance().value]
            val = self.parse_expr()
            return AugAssign(target=_to_store(target_expr), op=op, value=val)

        # AnnAssign  x: int  or  x: int = 5
        if self.is_op(':'):
            self.advance()
            ann = self.parse_expr()
            val = None
            if self.is_op('='):
                self.advance()
                val = self.parse_expr()
            return AnnAssign(target=_to_store(target_expr),
                             annotation=ann, value=val, simple=1)

        # Assign  x = …  (可以有多個 targets)
        if self.is_op('='):
            targets = [_to_store(target_expr)]
            while self.is_op('='):
                self.advance()
                rhs_exprs = [self.parse_expr()]
                while self.is_op(','):
                    self.advance()
                    if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF):
                        break
                    rhs_exprs.append(self.parse_expr())
                rhs = rhs_exprs[0] if len(rhs_exprs) == 1 else \
                      Tuple(elts=rhs_exprs, ctx=Load)
                if self.is_op('='):
                    targets.append(_to_store(rhs))
                    target_expr = rhs
                else:
                    return Assign(targets=targets, value=rhs, type_comment=None)
            # 走到這裡表示最後沒有 =
            return Assign(targets=targets[:-1],
                          value=_to_store(targets[-1]) if targets else target_expr,
                          type_comment=None)

        # 純 Expr 語句
        if len(exprs) > 1:
            return Expr(value=Tuple(elts=exprs, ctx=Load))
        return Expr(value=target_expr)

    def _eat_stmt_end(self) -> None:
        """吃掉 NEWLINE / ; / EOF。"""
        t: 'Token' = self.cur()
        if t.kind in (TK.NEWLINE, TK.NL):
            self.advance()
        elif t.kind == TK.EOF:
            pass
        # else: 不吃，可能是 ;

    # ── Block ─────────────────────────────────────────────────────────────────

    def parse_block(self) -> list:
        """NEWLINE INDENT stmts DEDENT，或同行 simple suite。"""
        # 同行 suite：冒號後緊接語句（無 NEWLINE/INDENT）
        if self.cur().kind not in (TK.NEWLINE, TK.NL, TK.INDENT, TK.EOF):
            return self.parse_stmt()
        self.skip_newlines()
        self.eat(TK.INDENT)
        self.skip_newlines()
        stmts: list = []
        while self.cur().kind not in (TK.DEDENT, TK.EOF):
            stmts.extend(self.parse_stmt())
            self.skip_newlines()
        self.match(TK.DEDENT)
        return stmts

    # ── 複合語句 ──────────────────────────────────────────────────────────────

    def parse_if(self) -> 'AST':
        self.eat(TK.NAME, 'if')
        test = self.parse_expr()
        self.eat(TK.OP, ':')
        body = self.parse_block()
        orelse = []
        self.skip_newlines()
        while self.is_keyword('elif'):
            self.advance()
            etest = self.parse_expr()
            self.eat(TK.OP, ':')
            ebody = self.parse_block()
            orelse = [If(test=etest, body=ebody, orelse=[])]
            self.skip_newlines()
            # 繼續往前看是否還有 elif/else
            if orelse and self.is_keyword('elif'):
                inner = self.parse_if_chain()
                orelse[0].orelse = inner
                break
        if self.is_keyword('else'):
            self.advance()
            self.eat(TK.OP, ':')
            if orelse:
                # 附加到最深的 elif
                def _attach(node, els):
                    if not node.orelse:
                        node.orelse = els
                    else:
                        for n in node.orelse:
                            if isinstance(n, If):
                                _attach(n, els)
                _attach(orelse[0] if orelse else None, self.parse_block())
            else:
                orelse = self.parse_block()
        return If(test=test, body=body, orelse=orelse)

    def parse_if_chain(self) -> list:
        """遞迴解析 elif…else 鏈，回傳 orelse list。"""
        if self.is_keyword('elif'):
            self.advance()
            test = self.parse_expr()
            self.eat(TK.OP, ':')
            body = self.parse_block()
            self.skip_newlines()
            orelse = self.parse_if_chain()
            return [If(test=test, body=body, orelse=orelse)]
        elif self.is_keyword('else'):
            self.advance()
            self.eat(TK.OP, ':')
            return self.parse_block()
        return []

    def parse_while(self) -> 'AST':
        self.eat(TK.NAME, 'while')
        test = self.parse_expr()
        self.eat(TK.OP, ':')
        body = self.parse_block()
        orelse = []
        self.skip_newlines()
        if self.is_keyword('else'):
            self.advance()
            self.eat(TK.OP, ':')
            orelse = self.parse_block()
        return While(test=test, body=body, orelse=orelse)

    def parse_for(self) -> 'AST':
        self.eat(TK.NAME, 'for')
        target = self.parse_target_list()
        self.eat(TK.NAME, 'in')
        iter_ = self.parse_expr()
        self.eat(TK.OP, ':')
        body = self.parse_block()
        orelse = []
        self.skip_newlines()
        if self.is_keyword('else'):
            self.advance()
            self.eat(TK.OP, ':')
            orelse = self.parse_block()
        return For(target=target, iter=iter_, body=body, orelse=orelse, type_comment=None)

    def parse_target_list(self) -> 'AST':
        """for 後面的 target，可能是 a, b, c 或 (a, b)。
        只解析到 'in' 關鍵字為止，不吃 'in'。"""
        targets = [_to_store(self._parse_for_target())]
        while self.is_op(','):
            self.advance()
            if self.is_keyword('in') or self.is_op(':'):
                break
            targets.append(_to_store(self._parse_for_target()))
        if len(targets) == 1:
            return targets[0]
        return Tuple(elts=targets, ctx=Store)

    def _parse_for_target(self) -> 'AST':
        """解析 for 迴圈的單一目標變數（不包含 'in'）。"""
        t = self.cur()
        if t.kind == TK.OP and t.value == '(':
            self.advance()
            targets = [_to_store(self._parse_for_target())]
            while self.is_op(','):
                self.advance()
                if self.is_op(')'):
                    break
                targets.append(_to_store(self._parse_for_target()))
            self.eat(TK.OP, ')')
            if len(targets) == 1:
                return targets[0]
            return Tuple(elts=targets, ctx=Store)
        if t.kind == TK.OP and t.value == '[':
            self.advance()
            targets = [_to_store(self._parse_for_target())]
            while self.is_op(','):
                self.advance()
                if self.is_op(']'):
                    break
                targets.append(_to_store(self._parse_for_target()))
            self.eat(TK.OP, ']')
            return List(elts=targets, ctx=Store)
        if t.kind == TK.OP and t.value == '*':
            self.advance()
            return Starred(value=Name(id=self.eat(TK.NAME).value, ctx=Store), ctx=Store)
        name = self.eat(TK.NAME).value
        return Name(id=name, ctx=Store)

    def parse_try(self) -> 'AST':
        self.eat(TK.NAME, 'try')
        self.eat(TK.OP, ':')
        body = self.parse_block()
        handlers = []
        orelse    = []
        finalbody = []
        self.skip_newlines()
        while self.is_keyword('except'):
            self.advance()
            exc_type = None
            exc_name = None
            if not self.is_op(':'):
                exc_type = self.parse_expr()
                if self.is_keyword('as'):
                    self.advance()
                    exc_name = self.eat(TK.NAME).value
            self.eat(TK.OP, ':')
            hbody = self.parse_block()
            handlers.append(ExceptHandler(type=exc_type, name=exc_name, body=hbody))
            self.skip_newlines()
        if self.is_keyword('else'):
            self.advance()
            self.eat(TK.OP, ':')
            orelse = self.parse_block()
            self.skip_newlines()
        if self.is_keyword('finally'):
            self.advance()
            self.eat(TK.OP, ':')
            finalbody = self.parse_block()
        return Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)

    def parse_with(self) -> 'AST':
        self.eat(TK.NAME, 'with')
        items = [self.parse_with_item()]
        while self.is_op(','):
            self.advance()
            items.append(self.parse_with_item())
        self.eat(TK.OP, ':')
        body = self.parse_block()
        return With(items=items, body=body, type_comment=None)

    def parse_with_item(self) -> 'AST':
        ctx: 'AST' = self.parse_expr()
        var = None
        if self.is_keyword('as'):
            self.advance()
            var = _to_store(self.parse_expr())
        return withitem(context_expr=ctx, optional_vars=var)

    def parse_funcdef(self) -> 'AST':
        is_async: bool = False
        if self.is_keyword('async'):
            self.advance()
            is_async = True
        self.eat(TK.NAME, 'def')
        name = self.eat(TK.NAME).value
        self.eat(TK.OP, '(')
        args = self.parse_arguments()
        self.eat(TK.OP, ')')
        returns = None
        if self.is_op('->'):
            self.advance()
            returns = self.parse_expr()
        self.eat(TK.OP, ':')
        body = self.parse_block()
        cls = AsyncFunctionDef if is_async else FunctionDef
        return cls(name=name, args=args, body=body,
                   decorator_list=[], returns=returns, type_comment=None)

    def parse_funcdef_with_decorators(self) -> 'AST':
        decorators: list = []
        while self.is_op('@'):
            self.advance()
            decorators.append(self.parse_expr())
            self.skip_newlines()
        node = self.parse_funcdef()
        node.decorator_list = decorators
        return node

    def parse_classdef(self) -> 'AST':
        self.eat(TK.NAME, 'class')
        name: str      = self.eat(TK.NAME).value
        bases: list    = []
        keywords: list = []
        if self.is_op('('):
            self.advance()
            if not self.is_op(')'):
                bases, keywords = self.parse_call_args_raw()
            self.eat(TK.OP, ')')
        self.eat(TK.OP, ':')
        body = self.parse_block()
        return ClassDef(name=name, bases=bases, keywords=keywords,
                        body=body, decorator_list=[])

    def parse_return(self) -> 'AST':
        self.eat(TK.NAME, 'return')
        if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF) or self.is_op(';'):
            self._eat_stmt_end()
            return Return(value=None)
        val = self.parse_expr_or_tuple()
        self._eat_stmt_end()
        return Return(value=val)

    def parse_raise(self) -> 'AST':
        self.eat(TK.NAME, 'raise')
        if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF) or self.is_op(';'):
            self._eat_stmt_end()
            return Raise(exc=None, cause=None)
        exc = self.parse_expr()
        cause = None
        if self.is_keyword('from'):
            self.advance()
            cause = self.parse_expr()
        self._eat_stmt_end()
        return Raise(exc=exc, cause=cause)

    def parse_del(self) -> 'AST':
        self.eat(TK.NAME, 'del')
        targets = [_to_del(self.parse_expr())]
        while self.is_op(','):
            self.advance()
            targets.append(_to_del(self.parse_expr()))
        self._eat_stmt_end()
        return Delete(targets=targets)

    def parse_global(self) -> 'AST':
        self.eat(TK.NAME, 'global')
        names = [self.eat(TK.NAME).value]
        while self.is_op(','):
            self.advance()
            names.append(self.eat(TK.NAME).value)
        self._eat_stmt_end()
        return Global(names=names)

    def parse_nonlocal(self) -> 'AST':
        self.eat(TK.NAME, 'nonlocal')
        names = [self.eat(TK.NAME).value]
        while self.is_op(','):
            self.advance()
            names.append(self.eat(TK.NAME).value)
        self._eat_stmt_end()
        return Nonlocal(names=names)

    def parse_import(self) -> 'AST':
        self.eat(TK.NAME, 'import')
        aliases = [self.parse_alias()]
        while self.is_op(','):
            self.advance()
            aliases.append(self.parse_alias())
        self._eat_stmt_end()
        return Import(names=aliases)

    def parse_from_import(self) -> 'AST':
        self.eat(TK.NAME, 'from')
        level = 0
        while self.is_op('.'):
            self.advance()
            level += 1
        module = None
        if self.cur().kind == TK.NAME and self.cur().value not in ('import',):
            parts = [self.eat(TK.NAME).value]
            while self.is_op('.'):
                self.advance()
                parts.append(self.eat(TK.NAME).value)
            module = '.'.join(parts)
        self.eat(TK.NAME, 'import')
        if self.is_op('('):
            self.advance()
            aliases = [self.parse_alias()]
            while self.is_op(','):
                self.advance()
                if self.is_op(')'):
                    break
                aliases.append(self.parse_alias())
            self.eat(TK.OP, ')')
        elif self.is_op('*'):
            self.advance()
            aliases = [alias(name='*', asname=None)]
        else:
            aliases = [self.parse_alias()]
            while self.is_op(','):
                self.advance()
                aliases.append(self.parse_alias())
        self._eat_stmt_end()
        return ImportFrom(module=module, names=aliases, level=level)

    def parse_alias(self) -> 'AST':
        name_parts: list = [self.eat(TK.NAME).value]
        while self.is_op('.'):
            self.advance()
            name_parts.append(self.eat(TK.NAME).value)
        name_str = '.'.join(name_parts)
        asname = None
        if self.is_keyword('as'):
            self.advance()
            asname = self.eat(TK.NAME).value
        return alias(name=name_str, asname=asname)

    def parse_assert(self) -> 'AST':
        self.eat(TK.NAME, 'assert')
        test = self.parse_expr()
        msg = None
        if self.is_op(','):
            self.advance()
            msg = self.parse_expr()
        self._eat_stmt_end()
        return Assert(test=test, msg=msg)

    # ── 函式參數 ──────────────────────────────────────────────────────────────

    def parse_arguments(self) -> 'AST':
        """解析 def f( ... ) 的參數列表。"""
        posonlyargs = []
        args_list   = []
        vararg      = None
        kwonlyargs  = []
        kw_defaults = []
        kwarg       = None
        defaults    = []

        if self.is_op(')'):
            return arguments(posonlyargs=posonlyargs, args=args_list,
                             vararg=vararg, kwonlyargs=kwonlyargs,
                             kw_defaults=kw_defaults, kwarg=kwarg,
                             defaults=defaults)

        saw_star = False
        saw_slash= False

        while not self.is_op(')'):
            if self.is_op('**'):
                self.advance()
                kwarg = arg(arg=self.eat(TK.NAME).value,
                            annotation=self._parse_arg_ann(),
                            type_comment=None)
                self.match(TK.OP, ',')
                break
            elif self.is_op('*'):
                self.advance()
                saw_star = True
                if self.is_op(','):
                    # bare *
                    self.advance()
                    continue
                elif not self.is_op(')'):
                    vararg = arg(arg=self.eat(TK.NAME).value,
                                 annotation=self._parse_arg_ann(),
                                 type_comment=None)
                    self.match(TK.OP, ',')
                    continue
            elif self.is_op('/'):
                self.advance()
                saw_slash = True
                # 把目前 args_list 移到 posonlyargs
                posonlyargs = args_list[:]
                # defaults 也要切分
                args_list = []
                defaults  = []
                self.match(TK.OP, ',')
                continue
            else:
                a_name = self.eat(TK.NAME).value
                ann    = self._parse_arg_ann()
                a      = arg(arg=a_name, annotation=ann, type_comment=None)
                default= None
                if self.is_op('='):
                    self.advance()
                    default = self.parse_expr()
                if saw_star:
                    kwonlyargs.append(a)
                    kw_defaults.append(default)
                else:
                    args_list.append(a)
                    if default is not None:
                        defaults.append(default)
                self.match(TK.OP, ',')

        return arguments(posonlyargs=posonlyargs, args=args_list,
                         vararg=vararg, kwonlyargs=kwonlyargs,
                         kw_defaults=kw_defaults, kwarg=kwarg,
                         defaults=defaults)

    def _parse_arg_ann(self) -> 'AST':
        if self.is_op(':'):
            self.advance()
            return self.parse_expr()
        return None

    # ── 表達式（優先級由低到高）──────────────────────────────────────────────

    def parse_expr_or_tuple(self) -> 'AST':
        """頂層表達式，支援 a, b 隱式 tuple（用於 return/yield）。"""
        first = self.parse_expr()
        if self.is_op(','):
            elts = [first]
            while self.is_op(','):
                self.advance()
                if self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF):
                    break
                elts.append(self.parse_expr())
            return Tuple(elts=elts, ctx=Load)
        return first

    def parse_expr(self) -> 'AST':
        """最頂層：lambda、walrus、yield。"""
        if self.is_keyword('lambda'):
            return self.parse_lambda()
        if self.is_keyword('yield'):
            self.advance()
            if self.is_keyword('from'):
                self.advance()
                val = self.parse_expr()
                return YieldFrom(value=val)
            val = None
            if not (self.cur().kind in (TK.NEWLINE, TK.NL, TK.EOF) or self.is_op(',')):
                val = self.parse_expr()
            return Yield(value=val)
        return self.parse_named_expr()

    def parse_named_expr(self) -> 'AST':
        """walrus operator :="""
        expr = self.parse_ternary()
        if self.is_op(':='):
            self.advance()
            val = self.parse_expr()
            return NamedExpr(target=_to_store(expr), value=val)
        return expr

    def parse_ternary(self) -> 'AST':
        """x if cond else y"""
        body = self.parse_or()
        self.skip_nl()
        if self.is_keyword('if'):
            self.advance()
            self.skip_nl()
            test = self.parse_or()
            self.skip_nl()
            self.eat(TK.NAME, 'else')
            self.skip_nl()
            orelse = self.parse_expr()
            return IfExp(test=test, body=body, orelse=orelse)
        return body

    def parse_or(self) -> 'AST':
        left: 'AST' = self.parse_and()
        while self.is_keyword('or'):
            self.advance()
            right = self.parse_and()
            if isinstance(left, BoolOp) and isinstance(left.op, Or.__class__) \
               and type(left.op) is type(Or()):
                left.values.append(right)
            else:
                left = BoolOp(op=Or(), values=[left, right])
        return left

    def parse_and(self) -> 'AST':
        left: 'AST' = self.parse_not()
        while self.is_keyword('and'):
            self.advance()
            right = self.parse_not()
            if isinstance(left, BoolOp) and type(left.op).__name__ == 'And':
                left.values.append(right)
            else:
                left = BoolOp(op=And(), values=[left, right])
        return left

    def parse_not(self) -> 'AST':
        if self.is_keyword('not'):
            self.advance()
            return UnaryOp(op=Not(), operand=self.parse_not())
        return self.parse_compare()

    def parse_compare(self) -> 'AST':
        left: 'AST' = self.parse_bitor()
        ops  = []
        comparators = []
        CMP_MAP = {
            '<': Lt(), '>': Gt(), '<=': LtE(), '>=': GtE(),
            '==': Eq(), '!=': NotEq(),
        }
        while True:
            if self.cur().kind == TK.OP and self.cur().value in CMP_MAP:
                ops.append(CMP_MAP[self.advance().value])
                comparators.append(self.parse_bitor())
            elif self.is_keyword('in'):
                self.advance()
                ops.append(In())
                comparators.append(self.parse_bitor())
            elif self.is_keyword('not') and self.peek(1).kind == TK.NAME \
                 and self.peek(1).value == 'in':
                self.advance(); self.advance()
                ops.append(NotIn())
                comparators.append(self.parse_bitor())
            elif self.is_keyword('is'):
                self.advance()
                if self.is_keyword('not'):
                    self.advance()
                    ops.append(IsNot())
                else:
                    ops.append(Is())
                comparators.append(self.parse_bitor())
            else:
                break
        if ops:
            return Compare(left=left, ops=ops, comparators=comparators)
        return left

    # ── 位元運算 ──────────────────────────────────────────────────────────────

    def parse_bitor(self) -> 'AST':
        return self._left_binop(self.parse_bitxor,
                                {'|': BitOr()})

    def parse_bitxor(self) -> 'AST':
        return self._left_binop(self.parse_bitand,
                                {'^': BitXor()})

    def parse_bitand(self) -> 'AST':
        return self._left_binop(self.parse_shift,
                                {'&': BitAnd()})

    def parse_shift(self) -> 'AST':
        return self._left_binop(self.parse_add,
                                {'<<': LShift(), '>>': RShift()})

    def parse_add(self) -> 'AST':
        return self._left_binop(self.parse_mul,
                                {'+': Add(), '-': Sub()})

    def parse_mul(self) -> 'AST':
        return self._left_binop(self.parse_unary,
                                {'*': Mult(), '/': Div(), '//': FloorDiv(),
                                 '%': Mod(), '@': MatMult()})

    def _left_binop(self, sub: object, op_map: dict) -> 'AST':
        left: 'AST' = sub()
        while self.cur().kind == TK.OP and self.cur().value in op_map:
            op  = op_map[self.advance().value]
            right = sub()
            left  = BinOp(left=left, op=op, right=right)
        return left

    def parse_unary(self) -> 'AST':
        if self.is_op('+'):
            self.advance()
            return UnaryOp(op=UAdd(), operand=self.parse_unary())
        if self.is_op('-'):
            self.advance()
            return UnaryOp(op=USub(), operand=self.parse_unary())
        if self.is_op('~'):
            self.advance()
            return UnaryOp(op=Invert(), operand=self.parse_unary())
        return self.parse_power()

    def parse_power(self) -> 'AST':
        base: 'AST' = self.parse_await_expr()
        if self.is_op('**'):
            self.advance()
            exp = self.parse_unary()   # ** 是右結合
            return BinOp(left=base, op=Pow(), right=exp)
        return base

    def parse_await_expr(self) -> 'AST':
        if self.is_keyword('await'):
            self.advance()
            return Await(value=self.parse_primary())
        return self.parse_primary()

    # ── Primary（呼叫、subscript、屬性）────────────────────────────────────────

    def parse_primary(self) -> 'AST':
        node: 'AST' = self.parse_atom()
        while True:
            if self.is_op('('):
                node = self.parse_call(node)
            elif self.is_op('['):
                self.advance()
                sl = self.parse_subscript_slice()
                self.eat(TK.OP, ']')
                node = Subscript(value=node, slice=sl, ctx=Load)
            elif self.is_op('.'):
                self.advance()
                attr = self.eat(TK.NAME).value
                node = Attribute(value=node, attr=attr, ctx=Load)
            else:
                break
        return node

    def parse_call(self, func):
        self.eat(TK.OP, '(')
        args, kws = self.parse_call_args_raw()
        self.eat(TK.OP, ')')
        return Call(func=func, args=args, keywords=kws)

    def parse_call_args_raw(self) -> tuple:
        """回傳 (args_list, keywords_list)。"""
        args: list = []
        kws: list  = []
        self.skip_newlines()
        while not self.is_op(')'):
            self.skip_newlines()
            if self.is_op('**'):
                self.advance()
                kws.append(keyword(arg=None, value=self.parse_expr()))
            elif self.is_op('*'):
                self.advance()
                args.append(Starred(value=self.parse_expr(), ctx=Load))
            elif self.cur().kind == TK.NAME and self.peek(1).kind == TK.OP \
                 and self.peek(1).value == '=':
                kname = self.advance().value
                self.advance()  # eat =
                kws.append(keyword(arg=kname, value=self.parse_expr()))
            else:
                e = self.parse_expr()
                # comprehension inside call
                if self.is_keyword('for'):
                    gen = self.parse_comp_generators()
                    e = GeneratorExp(elt=e, generators=gen)
                args.append(e)
            self.skip_newlines()
            if not self.is_op(')'):
                self.match(TK.OP, ',')
            self.skip_newlines()
        return args, kws

    def parse_subscript_slice(self) -> 'AST':
        """解析 [] 內的內容，可能是 slice 或 index 或 tuple。"""
        elts: list = [self._parse_single_slice()]
        while self.is_op(','):
            self.advance()
            if self.is_op(']'):
                break
            elts.append(self._parse_single_slice())
        if len(elts) == 1:
            return elts[0]
        return Tuple(elts=elts, ctx=Load)

    def _parse_single_slice(self) -> 'AST':
        """冒號形式的 slice 或普通表達式。"""
        # 先檢查是否為 slice
        if self.is_op(':'):
            # :stop 或 :stop:step 或 ::step
            self.advance()
            stop = None
            step = None
            if not self.is_op(':') and not self.is_op(']') and not self.is_op(','):
                stop = self.parse_expr()
            if self.is_op(':'):
                self.advance()
                if not self.is_op(']') and not self.is_op(','):
                    step = self.parse_expr()
            return Slice(lower=None, upper=stop, step=step)

        expr = self.parse_expr()
        if self.is_op(':'):
            self.advance()
            stop = None
            step = None
            if not self.is_op(':') and not self.is_op(']') and not self.is_op(','):
                stop = self.parse_expr()
            if self.is_op(':'):
                self.advance()
                if not self.is_op(']') and not self.is_op(','):
                    step = self.parse_expr()
            return Slice(lower=expr, upper=stop, step=step)
        return expr

    # ── Atom ──────────────────────────────────────────────────────────────────

    def parse_atom(self) -> 'AST':
        t: 'Token' = self.cur()

        # 數字
        if t.kind == TK.NUM:
            self.advance()
            return Constant(value=_parse_number(t.value), kind=None)

        # 字串（相鄰字串自動串接）
        if t.kind == TK.STR:
            parts = []
            while self.cur().kind == TK.STR:
                parts.append(self.advance().value)
            return _make_str_node(parts)

        # 識別字 / 關鍵字
        if t.kind == TK.NAME:
            if t.value == 'True':
                self.advance(); return Constant(value=True, kind=None)
            if t.value == 'False':
                self.advance(); return Constant(value=False, kind=None)
            if t.value == 'None':
                self.advance(); return Constant(value=None, kind=None)
            if t.value == 'lambda':
                return self.parse_lambda()
            if t.value == 'not':
                return self.parse_not()
            self.advance()
            return Name(id=t.value, ctx=Load)

        # (expr) 或 tuple 或 generator
        if t.kind == TK.OP and t.value == '(':
            self.advance()
            self.skip_newlines()
            if self.is_op(')'):
                self.advance()
                return Tuple(elts=[], ctx=Load)
            first = self.parse_expr()
            self.skip_newlines()
            # generator expression
            if self.is_keyword('for'):
                gens = self.parse_comp_generators()
                self.eat(TK.OP, ')')
                return GeneratorExp(elt=first, generators=gens)
            # tuple
            if self.is_op(','):
                elts = [first]
                while self.is_op(','):
                    self.advance()
                    self.skip_newlines()
                    if self.is_op(')'):
                        break
                    elts.append(self.parse_expr())
                    self.skip_newlines()
                self.eat(TK.OP, ')')
                return Tuple(elts=elts, ctx=Load)
            self.skip_newlines()
            self.eat(TK.OP, ')')
            return first

        # [list] or list comprehension
        if t.kind == TK.OP and t.value == '[':
            self.advance()
            self.skip_newlines()
            if self.is_op(']'):
                self.advance()
                return List(elts=[], ctx=Load)
            first = self.parse_expr()
            self.skip_newlines()
            if self.is_keyword('for'):
                gens = self.parse_comp_generators()
                self.eat(TK.OP, ']')
                return ListComp(elt=first, generators=gens)
            elts = [first]
            while self.is_op(','):
                self.advance()
                self.skip_newlines()
                if self.is_op(']'):
                    break
                elts.append(self.parse_expr())
                self.skip_newlines()
            self.skip_newlines()
            self.eat(TK.OP, ']')
            return List(elts=elts, ctx=Load)

        # {dict/set} or comprehension
        if t.kind == TK.OP and t.value == '{':
            self.advance()
            self.skip_newlines()
            if self.is_op('}'):
                self.advance()
                return Dict(keys=[], values=[])
            # **spread 開頭
            if self.is_op('**'):
                return self.parse_dict_or_set_from_star()
            first = self.parse_expr()
            self.skip_newlines()
            # dict
            if self.is_op(':'):
                self.advance()
                val = self.parse_expr()
                self.skip_newlines()
                if self.is_keyword('for'):
                    gens = self.parse_comp_generators()
                    self.eat(TK.OP, '}')
                    return DictComp(key=first, value=val, generators=gens)
                keys = [first]; values = [val]
                while self.is_op(','):
                    self.advance()
                    self.skip_newlines()
                    if self.is_op('}'):
                        break
                    if self.is_op('**'):
                        self.advance()
                        keys.append(None)
                        values.append(self.parse_expr())
                    else:
                        k = self.parse_expr()
                        self.eat(TK.OP, ':')
                        v = self.parse_expr()
                        keys.append(k); values.append(v)
                    self.skip_newlines()
                self.eat(TK.OP, '}')
                return Dict(keys=keys, values=values)
            # set
            if self.is_keyword('for'):
                gens = self.parse_comp_generators()
                self.eat(TK.OP, '}')
                return SetComp(elt=first, generators=gens)
            elts = [first]
            while self.is_op(','):
                self.advance()
                self.skip_newlines()
                if self.is_op('}'):
                    break
                elts.append(self.parse_expr())
                self.skip_newlines()
            self.eat(TK.OP, '}')
            return Set(elts=elts)

        # *expr  (在賦值目標 / 函式呼叫裡)
        if t.kind == TK.OP and t.value == '*':
            self.advance()
            return Starred(value=self.parse_expr(), ctx=Store)

        # Ellipsis
        if t.kind == TK.OP and t.value == '...':
            self.advance()
            return Constant(value=..., kind=None)

        # 裝飾器起頭 @ — 只在語句層用，不在表達式裡
        if t.kind == TK.OP and t.value == '@':
            raise SyntaxError(f"unexpected '@' in expression at line {t.line}")

        raise SyntaxError(
            f"unexpected token {t.kind}({t.value!r}) at line {t.line}")

    def parse_dict_or_set_from_star(self) -> 'AST':
        """{ **d, ... } 開頭的 dict。"""
        keys: list = []; values: list = []
        while not self.is_op('}'):
            if self.is_op('**'):
                self.advance()
                keys.append(None)
                values.append(self.parse_expr())
            else:
                k = self.parse_expr()
                self.eat(TK.OP, ':')
                v = self.parse_expr()
                keys.append(k); values.append(v)
            if not self.is_op('}'):
                self.eat(TK.OP, ',')
                self.skip_newlines()
        self.eat(TK.OP, '}')
        return Dict(keys=keys, values=values)

    def parse_lambda(self) -> 'AST':
        self.eat(TK.NAME, 'lambda')
        # 簡化版參數（不含型別注解）
        args_list = []
        defaults  = []
        vararg    = None
        kwarg     = None
        while not self.is_op(':'):
            if self.is_op('**'):
                self.advance()
                kwarg = arg(arg=self.eat(TK.NAME).value, annotation=None, type_comment=None)
                self.match(TK.OP, ',')
            elif self.is_op('*'):
                self.advance()
                if not self.is_op(',') and not self.is_op(':'):
                    vararg = arg(arg=self.eat(TK.NAME).value, annotation=None, type_comment=None)
                self.match(TK.OP, ',')
            else:
                a = arg(arg=self.eat(TK.NAME).value, annotation=None, type_comment=None)
                args_list.append(a)
                if self.is_op('='):
                    self.advance()
                    defaults.append(self.parse_expr())
                self.match(TK.OP, ',')
        self.eat(TK.OP, ':')
        body = self.parse_expr()
        return Lambda(args=arguments(posonlyargs=[], args=args_list,
                                     vararg=vararg, kwonlyargs=[],
                                     kw_defaults=[], kwarg=kwarg,
                                     defaults=defaults), body=body)

    # ── Comprehension generators ───────────────────────────────────────────────

    def parse_comp_generators(self) -> list:
        gens: list = []
        self.skip_newlines()
        while self.is_keyword('for') or self.is_keyword('async'):
            is_async = 0
            if self.is_keyword('async'):
                self.advance()
                is_async = 1
            self.eat(TK.NAME, 'for')
            target = _to_store(self.parse_target_list())
            self.eat(TK.NAME, 'in')
            # comprehension の iter は OR level（ternary は使わない）
            iter_ = self.parse_or()
            ifs   = []
            self.skip_newlines()
            while self.is_keyword('if'):
                self.advance()
                ifs.append(self.parse_or())
                self.skip_newlines()
            gens.append(comprehension(target=target, iter=iter_,
                                      ifs=ifs, is_async=is_async))
            self.skip_newlines()
        return gens

    # ── stmt 首行帶 decorator 的情況 ─────────────────────────────────────────

    def parse_stmt(self) -> list:  # noqa: F811  (override)
        """語句解析主入口，支援 @ 裝飾器。"""
        self.skip_newlines()
        t: 'Token' = self.cur()

        # 裝飾器
        if t.kind == TK.OP and t.value == '@':
            decorators = []
            while self.cur().kind == TK.OP and self.cur().value == '@':
                self.advance()
                decorators.append(self.parse_primary())
                # 括號呼叫
                if self.is_op('('):
                    decorators[-1] = self.parse_call(decorators[-1])
                self.skip_newlines()
            node = self._parse_def_or_class()
            node.decorator_list = decorators
            return [node]

        if t.kind == TK.NAME:
            kw = t.value
            if kw == 'if':     return [self.parse_if()]
            if kw == 'while':  return [self.parse_while()]
            if kw == 'for':    return [self.parse_for()]
            if kw == 'try':    return [self.parse_try()]
            if kw == 'with':   return [self.parse_with()]
            if kw in ('def', 'async'):
                node = self.parse_funcdef()
                return [node]
            if kw == 'class':  return [self.parse_classdef()]
            if kw == 'return': return [self.parse_return()]
            if kw == 'raise':  return [self.parse_raise()]
            if kw == 'del':    return [self.parse_del()]
            if kw == 'pass':
                self.advance(); self._eat_stmt_end(); return [Pass()]
            if kw == 'break':
                self.advance(); self._eat_stmt_end(); return [Break()]
            if kw == 'continue':
                self.advance(); self._eat_stmt_end(); return [Continue()]
            if kw == 'global':   return [self.parse_global()]
            if kw == 'nonlocal': return [self.parse_nonlocal()]
            if kw == 'import':   return [self.parse_import()]
            if kw == 'from':     return [self.parse_from_import()]
            if kw == 'assert':   return [self.parse_assert()]

        if t.kind == TK.INDENT:
            raise SyntaxError(f"unexpected indent at line {t.line}")

        return self.parse_simple_stmt()

    def _parse_def_or_class(self) -> 'AST':
        if self.is_keyword('class'):
            return self.parse_classdef()
        return self.parse_funcdef()


# ══════════════════════════════════════════════════════════════════════════════
# 4.  輔助函式
# ══════════════════════════════════════════════════════════════════════════════

def _to_store(node: 'AST') -> 'AST':
    """將 Load context 的節點轉成 Store context。"""
    if isinstance(node, Name):
        node.ctx = Store
    elif isinstance(node, (Tuple, List)):
        node.ctx = Store
        for e in node.elts:
            if e is not None:
                _to_store(e)
    elif isinstance(node, Attribute):
        node.ctx = Store
    elif isinstance(node, Subscript):
        node.ctx = Store
    elif isinstance(node, Starred):
        node.ctx = Store
        _to_store(node.value)
    return node

def _to_del(node: 'AST') -> 'AST':
    if isinstance(node, Name):
        node.ctx = Del
    elif isinstance(node, Attribute):
        node.ctx = Del
    elif isinstance(node, Subscript):
        node.ctx = Del
    return node


def _parse_number(s: str) -> object:
    """把 token 字串轉成 Python 數值。"""
    s2: str = s.replace('_', '')
    try:
        if s2.endswith('j') or s2.endswith('J'):
            return complex(s2)
        if '.' in s2 or 'e' in s2.lower():
            return float(s2)
        return int(s2, 0)
    except ValueError:
        return eval(s2)   # fallback


def _make_str_node(raw_parts: list) -> 'AST':
    """
    把一個或多個相鄰字串 token 解析成 Constant 或 JoinedStr（f-string）。
    """
    has_fstr: bool = any(p.startswith(('f', 'F', 'rf', 'fr', 'rF', 'Fr', 'RF', 'FR'))
                   for p in raw_parts)
    if has_fstr:
        # 把所有部分合成一個 f-string 節點
        all_values = []
        for raw in raw_parts:
            all_values.extend(_parse_fstring_raw(raw))
        return JoinedStr(values=all_values)
    # 普通字串：串接
    value = ''.join(_decode_str(p) for p in raw_parts)
    return Constant(value=value, kind=None)


def _decode_str(raw: str) -> str:
    """把 token 原始字串（含引號）解碼為 Python str/bytes。"""
    # 去掉前綴
    prefix: str = ''
    s: str = raw
    while s and s[0].lower() in 'bru':
        prefix += s[0].lower()
        s = s[1:]
    # 去掉引號
    if s.startswith('"""') or s.startswith("'''"):
        q = s[:3]
        inner = s[3:-3]
    else:
        q = s[0]
        inner = s[1:-1]
    # 解碼
    try:
        if 'b' in prefix:
            return eval(raw)  # bytes 直接用 eval
        if 'r' in prefix:
            return inner  # raw string：不處理跳脫
        # 處理常見跳脫序列
        return inner.encode('raw_unicode_escape').decode('unicode_escape')
    except Exception:
        return eval(raw)  # fallback


def _parse_fstring_raw(raw: str) -> list:
    """
    把 f-string token 解析成 JoinedStr.values 所需的節點列表：
    Constant（文字段）和 FormattedValue（{...} 段）。
    """
    # 找到 f-string 的前綴和引號
    s = raw
    prefix = ''
    while s and s[0].lower() in 'bfrBFR':
        prefix += s[0].lower()
        s = s[1:]

    if s.startswith('"""') or s.startswith("'''"):
        q = s[:3]; inner = s[3:-3]
    else:
        q = s[0]; inner = s[1:-1]

    result = []
    i = 0
    buf = []

    while i < len(inner):
        if inner[i] == '{':
            if i+1 < len(inner) and inner[i+1] == '{':
                buf.append('{'); i += 2; continue
            # 找到對應的 }，考慮嵌套
            depth = 1; j = i+1
            while j < len(inner) and depth:
                if inner[j] == '{': depth += 1
                elif inner[j] == '}': depth -= 1
                j += 1
            expr_src = inner[i+1:j-1]
            # 可能有 !r !s !a 和 :format_spec
            conv = -1; fmt_spec = None
            # 先找 ! conversion（不在子表達式裡）
            parts = _split_fstring_expr(expr_src)
            main_expr = parts[0]
            if len(parts) > 1:
                # parts[1] 是 conversion 或 format_spec
                rest = parts[1]
                if rest and rest[0] == '!':
                    conv = ord(rest[1])
                    rest = rest[2:]
                if rest and rest.startswith(':'):
                    fmt_src = rest[1:]
                    # parse format spec as a JoinedStr
                    fmt_spec = _parse_fstring_spec(fmt_src)
            if buf:
                result.append(Constant(value=''.join(buf), kind=None))
                buf = []
            # parse main_expr as expression (not module)
            fv = FormattedValue(
                value=_parse_expr_str(main_expr.strip()),
                conversion=conv,
                format_spec=fmt_spec,
            )
            result.append(fv)
            i = j
        elif inner[i] == '}':
            if i+1 < len(inner) and inner[i+1] == '}':
                buf.append('}'); i += 2; continue
            raise SyntaxError("single '}' in f-string")
        else:
            buf.append(inner[i]); i += 1

    if buf:
        result.append(Constant(value=''.join(buf), kind=None))
    return result


def _split_fstring_expr(src: str) -> list:
    """把 f-string 的 {expr!r:spec} 切成 [expr, '!r:spec'] 兩部分。"""
    depth = 0
    for i, c in enumerate(src):
        if c in '([{': depth += 1
        elif c in ')]}': depth -= 1
        elif depth == 0 and c in ('!', ':'):
            return [src[:i], src[i:]]
    return [src]


def _parse_fstring_spec(spec_src: str) -> 'AST':
    """把 format spec 字串解析為 JoinedStr 節點（可能含 {expr}）。"""
    values = []
    i = 0; buf = []
    while i < len(spec_src):
        if spec_src[i] == '{':
            depth=1; j=i+1
            while j < len(spec_src) and depth:
                if spec_src[j] == '{': depth += 1
                elif spec_src[j] == '}': depth -= 1
                j += 1
            if buf:
                values.append(Constant(value=''.join(buf), kind=None)); buf=[]
            inner = spec_src[i+1:j-1]
            values.append(FormattedValue(value=parse(inner.strip()),
                                          conversion=-1, format_spec=None))
            i = j
        else:
            buf.append(spec_src[i]); i += 1
    if buf:
        values.append(Constant(value=''.join(buf), kind=None))
    return JoinedStr(values=values)


# ── 如果 parse() 被傳入一個表達式字串（不是完整的語句）─────────────────────────
def _parse_expr_str(src: str) -> 'AST':
    tokens: list = _tokenize(src.strip() + '\n')
    p: '_Parser' = _Parser(tokens)
    return p.parse_expr()


# ══════════════════════════════════════════════════════════════════════════════
# 5.  公開 API（與 stdlib ast 相容）
# ══════════════════════════════════════════════════════════════════════════════

def parse(source: str, filename: str = '<unknown>', mode: str = 'eval_or_exec') -> 'AST':
    """
    解析 Python 原始碼，回傳 AST。
    mode='exec'  → Module
    mode='eval'  → 單一表達式
    auto         → 優先嘗試 exec，若失敗嘗試 eval
    """
    if not source.endswith('\n'):
        source += '\n'
    tokens: list = _tokenize(source)
    p: '_Parser' = _Parser(tokens)

    if mode == 'eval':
        return p.parse_expr()

    return p.parse_module()
