# ==========================================
# 1. 符號數學語法樹結構 (AST Nodes)
# ==========================================

class Expr:
    def __add__(self, other):
        return Add(self, other if isinstance(other, Expr) else Const(other))
    
    def __radd__(self, other):
        return Add(Const(other), self)
    
    def __sub__(self, other):
        return Add(self, Mul(Const(-1), other if isinstance(other, Expr) else Const(other)))

    def __mul__(self, other):
        return Mul(self, other if isinstance(other, Expr) else Const(other))
    
    def __rmul__(self, other):
        return Mul(Const(other), self)

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
        self.f = f
        self.g = g
        
    def diff(self, var):
        return Add(self.f.diff(var), self.g.diff(var))
    
    def __repr__(self):
        return f"({self.f} + {self.g})"

class Mul(Expr):
    def __init__(self, f, g):
        self.f = f
        self.g = g
        
    def diff(self, var):
        # 乘法法則: f' * g + f * g'
        return Add(Mul(self.f.diff(var), self.g), Mul(self.f, self.g.diff(var)))
    
    def __repr__(self):
        return f"({self.f} * {self.g})"

class Power(Expr):
    def __init__(self, f, n):
        self.f = f
        self.n = n
        
    def diff(self, var):
        # 次方律 + 連鎖律: n * f^(n-1) * f'
        return Mul(Mul(Const(self.n), Power(self.f, self.n - 1)), self.f.diff(var))
    
    def __repr__(self):
        return f"({self.f}^{self.n})"

class Sin(Expr):
    def __init__(self, f):
        self.f = f
        
    def diff(self, var):
        # 連鎖律: cos(f) * f'
        return Mul(Cos(self.f), self.f.diff(var))
    
    def __repr__(self):
        return f"sin({self.f})"

class Cos(Expr):
    def __init__(self, f):
        self.f = f
        
    def diff(self, var):
        # 連鎖律: -1 * sin(f) * f'
        return Mul(Mul(Const(-1), Sin(self.f)), self.f.diff(var))
    
    def __repr__(self):
        return f"cos({self.f})"


# ==========================================
# 2. 遞迴微分與遞迴化簡函式
# ==========================================

def sym_diff(expr, var='x'):
    """遞迴進行符號微分"""
    return expr.diff(var)

def simplify(expr):
    """遞迴進行表達式化簡"""
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
# 3. 主程式：測試 10 個數學式
# ==========================================

if __name__ == "__main__":
    x = Var('x')

    # 定義 10 個數學表達式
    expressions = [
        # 1. 常數與線性式: 5
        Const(5),
        
        # 2. 變數次冪: x^3
        x ** 3,
        
        # 3. 多項式: 4*x^2 + 3*x + 7
        Const(4) * (x ** 2) + Const(3) * x + Const(7),
        
        # 4. 基本三角函數: sin(x)
        Sin(x),
        
        # 5. 帶係數三角函數: cos(3*x)
        Cos(Const(3) * x),
        
        # 6. 三角函數加法結合: sin(x) + cos(x)
        Sin(x) + Cos(x),
        
        # 7. 乘法法則 (Product Rule): x^2 * sin(x)
        (x ** 2) * Sin(x),
        
        # 8. 連鎖律複合次冪: (2*x + 5)^4
        (Const(2) * x + Const(5)) ** 4,
        
        # 9. 三角函數與次方結合: sin(x^2)
        Sin(x ** 2),
        
        # 10. 複雜多項式與三角函數組合: 3*x^2 + sin(2*x) * cos(x)
        Const(3) * (x ** 2) + Sin(Const(2) * x) * Cos(x)
    ]

    print("=" * 60)
    print("符號微分測試結果：diff(expr) = expr2")
    print("=" * 60)

    for idx, expr in enumerate(expressions, 1):
        # 求導並進行化簡
        raw_diff = sym_diff(expr, 'x')
        simplified_diff = simplify(raw_diff)
        
        print(f"[{idx:2d}] diff({expr}) = {simplified_diff}")