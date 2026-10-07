import re

# ==========================================
# 1. 符號數學語法樹結構 (AST Nodes)
# ==========================================

class Expr:
    def __add__(self, other):
        return Add(self, other if isinstance(other, Expr) else Const(other))
    def __mul__(self, other):
        return Mul(self, other if isinstance(other, Expr) else Const(other))
    def __pow__(self, power):
        return Power(self, power)

class Const(Expr):
    def __init__(self, val):
        self.val = val
    def diff(self, var):
        return Const(0)
    def __repr__(self):
        return str(self.val)

class Var(Expr):
    def __init__(self, name):
        self.name = name
    def diff(self, var):
        return Const(1) if self.name == var else Const(0)
    def __repr__(self):
        return self.name

class Add(Expr):
    def __init__(self, f, g):
        self.f, self.g = f, g
    def diff(self, var):
        return Add(self.f.diff(var), self.g.diff(var))
    def __repr__(self):
        return f"({self.f} + {self.g})"

class Mul(Expr):
    def __init__(self, f, g):
        self.f, self.g = f, g
    def diff(self, var):
        return Add(Mul(self.f.diff(var), self.g), Mul(self.f, self.g.diff(var)))
    def __repr__(self):
        return f"({self.f} * {self.g})"

class Power(Expr):
    def __init__(self, f, n):
        self.f, self.n = f, n
    def diff(self, var):
        return Mul(Mul(Const(self.n), Power(self.f, self.n - 1)), self.f.diff(var))
    def __repr__(self):
        return f"({self.f}^{self.n})"

class Sin(Expr):
    def __init__(self, f):
        self.f = f
    def diff(self, var):
        return Mul(Cos(self.f), self.f.diff(var))
    def __repr__(self):
        return f"sin({self.f})"

class Cos(Expr):
    def __init__(self, f):
        self.f = f
    def diff(self, var):
        return Mul(Mul(Const(-1), Sin(self.f)), self.f.diff(var))
    def __repr__(self):
        return f"cos({self.f})"


# ==========================================
# 2. TeX Parser (遞迴下降語法解析器)
# ==========================================

class TexParser:
    """
    語法優先順序 (由低到高):
    Expr   := Term ('+' Term | '-' Term)*
    Term   := Factor (('*'| implicit_mul) Factor)*
    Factor := Base ('^' Integer | '^{' Integer '}')?
    Base   := Number | Var | '\\sin' Base | '\\cos' Base | '(' Expr ')' | '{' Expr '}'
    """
    def __init__(self, tex_str):
        self.tokens = self._tokenize(tex_str)
        self.pos = 0

    def _tokenize(self, s):
        # 切分數字、變數、TeX 指令 (\sin, \cos)、運算子與括號
        token_pattern = r'\d+|\\[a-zA-Z]+|[a-zA-Z]|[\+\-\*\^\(\)\{\}]'
        return re.findall(token_pattern, s)

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _consume(self, expected=None):
        token = self._peek()
        if expected and token != expected:
            raise ValueError(f"期待 '{expected}' 但收到 '{token}'")
        self.pos += 1
        return token

    def parse(self):
        res = self._parse_expr()
        if self.pos < len(self.tokens):
            raise ValueError(f"未解析完成的 Token: {self.tokens[self.pos:]}")
        return res

    def _parse_expr(self):
        node = self._parse_term()
        while self._peek() in ('+', '-'):
            op = self._consume()
            next_term = self._parse_term()
            if op == '+':
                node = Add(node, next_term)
            else:
                node = Add(node, Mul(Const(-1), next_term))
        return node

    def _parse_term(self):
        node = self._parse_factor()
        # 處理顯式乘法 (*) 與隱式乘法 (如 2x, x\sin(x))
        while self._peek() and self._peek() not in ('+', '-', ')', '}'):
            if self._peek() == '*':
                self._consume('*')
            node = Mul(node, self._parse_factor())
        return node

    def _parse_factor(self):
        node = self._parse_base()
        if self._peek() == '^':
            self._consume('^')
            # 處理 ^{n} 或 ^n 兩種 TeX 寫法
            if self._peek() == '{':
                self._consume('{')
                n = int(self._consume())
                self._consume('}')
            else:
                n = int(self._consume())
            node = Power(node, n)
        return node

    def _parse_base(self):
        token = self._peek()
        if token is None:
            raise ValueError("意外到達結尾")

        if token.isdigit():
            return Const(int(self._consume()))
        
        elif token == '\\sin':
            self._consume('\\sin')
            return Sin(self._parse_base())
            
        elif token == '\\cos':
            self._consume('\\cos')
            return Cos(self._parse_base())
            
        elif token == '(':
            self._consume('(')
            node = self._parse_expr()
            self._consume(')')
            return node
            
        elif token == '{':
            self._consume('{')
            node = self._parse_expr()
            self._consume('}')
            return node
            
        elif token.isalpha():
            return Var(self._consume())
            
        else:
            raise ValueError(f"無法識別的語法 token: {token}")


def parse_tex(tex_str):
    """將 TeX 字串轉換為 AST 物件"""
    return TexParser(tex_str).parse()


# ==========================================
# 3. 遞迴微分與遞迴化簡函式
# ==========================================

def sym_diff(expr, var='x'):
    return expr.diff(var)

def simplify(expr):
    if isinstance(expr, Add):
        f, g = simplify(expr.f), simplify(expr.g)
        if isinstance(f, Const) and f.val == 0: return g
        if isinstance(g, Const) and g.val == 0: return f
        if isinstance(f, Const) and isinstance(g, Const): return Const(f.val + g.val)
        return Add(f, g)
        
    elif isinstance(expr, Mul):
        f, g = simplify(expr.f), simplify(expr.g)
        if isinstance(f, Const) and f.val == 0: return Const(0)
        if isinstance(g, Const) and g.val == 0: return Const(0)
        if isinstance(f, Const) and f.val == 1: return g
        if isinstance(g, Const) and g.val == 1: return f
        if isinstance(f, Const) and isinstance(g, Const): return Const(f.val * g.val)
        return Mul(f, g)
        
    elif isinstance(expr, Power):
        f = simplify(expr.f)
        if expr.n == 0: return Const(1)
        if expr.n == 1: return f
        return Power(f, expr.n)
        
    elif isinstance(expr, Sin):
        return Sin(simplify(expr.f))
    elif isinstance(expr, Cos):
        return Cos(simplify(expr.f))
        
    return expr


# ==========================================
# 4. 主程式：10 個 TeX 字串測試範例
# ==========================================

if __name__ == "__main__":
    # 10 個用字串表示的 TeX 數學表達式
    tex_examples = [
        "5",                                    # 1. 常數
        "x^3",                                  # 2. 單一冪次
        "4x^{2} + 3x + 7",                      # 3. 多項式 (帶 TeX 括號^{2} 與隱式乘法)
        "\\sin(x)",                             # 4. 標準正弦
        "\\cos(3x)",                            # 5. 三角函數加倍角
        "\\sin(x) + \\cos(x)",                  # 6. 三角函數加法
        "x^{2} \\sin(x)",                       # 7. 乘法法則 (x^2 * sin(x))
        "(2x + 5)^{4}",                         # 8. 連鎖律複合式
        "\\sin(x^{2})",                         # 9. 函數內嵌套次方
        "3x^{2} + \\sin(2x) \\cos(x)"           # 10. 複雜組合式
    ]

    print("=" * 70)
    print("TeX Parser 符號微分測試：diff(tex_str) = exp2")
    print("=" * 70)

    for idx, tex_str in enumerate(tex_examples, 1):
        # 1. 將 TeX 字串解析為 AST
        ast_expr = parse_tex(tex_str)
        
        # 2. 對 AST 進行遞迴微分與化簡
        raw_diff = sym_diff(ast_expr, 'x')
        simplified_diff = simplify(raw_diff)
        
        # 3. 輸出結果
        print(f"[{idx:2d}] diff(\"{tex_str}\") = {simplified_diff}")