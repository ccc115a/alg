import math

class Symbol:
    """
    表示表達式樹中的一個節點，用於符號微分。
    節點可以是變數、常數或一個運算。
    """

    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = None
        
        # *** 修正 #1: 將 _prev 從 set 改為 tuple ***
        # 使用 tuple 可以保留子節點的順序，對於減法、除法等非交換運算至關重要
        self._prev = tuple(_children)
        self._op = _op 

    def __add__(self, other):
        other = other if isinstance(other, Symbol) else Symbol(other)
        return Symbol(None, (self, other), '+')

    def __mul__(self, other):
        other = other if isinstance(other, Symbol) else Symbol(other)
        return Symbol(None, (self, other), '*')

    def __pow__(self, other):
        assert isinstance(other, (int, float)), "次方只支援常數"
        return Symbol(other, (self,), '**')

    def diff(self, var_name):
        """
        對 'var_name' 變數進行符號微分。
        """
        # --- 基底情況 (Leaf Nodes) ---
        if self._op == '':
            if isinstance(self.data, (int, float)): # 對常數微分 -> 0
                return Symbol(0)
            if isinstance(self.data, str): # 對變數微分
                return Symbol(1) if self.data == var_name else Symbol(0)

        # --- 遞迴情況 (Operator Nodes) ---
        if self._op == '+':
            u, v = self._prev
            return u.diff(var_name) + v.diff(var_name)

        if self._op == '*':
            u, v = self._prev
            return (u * v.diff(var_name)) + (v * u.diff(var_name))

        if self._op == '**':
            base, = self._prev
            exponent = self.data
            term1 = Symbol(exponent) * (base ** (exponent - 1))
            term2 = base.diff(var_name)
            return term1 * term2
            
        raise NotImplementedError(f"尚未實作 '{self._op}' 運算的微分規則")

    def simplify(self):
        """
        遞迴地簡化表達式樹。
        """
        if self._op == '': # 葉節點無需簡化
            return self

        # 先遞迴簡化子節點
        simplified_prev = [p.simplify() for p in self._prev]
        
        # *** 修正 #2: 建立一個更嚴謹的輔助函式來判斷常數節點 ***
        def is_const(node, value=None):
            # 一個節點是常數，若且唯若它沒有運算子且其 data 是數字
            is_node_const = node._op == '' and isinstance(node.data, (int, float))
            if not is_node_const:
                return False
            # 如果有指定檢查值，則進一步比對
            if value is not None:
                return node.data == value
            return True

        # 根據運算子進行簡化
        if self._op == '+':
            u, v = simplified_prev
            if is_const(u, 0): return v  # 0 + x -> x
            if is_const(v, 0): return u  # x + 0 -> x
            if is_const(u) and is_const(v): # c1 + c2 -> c3
                return Symbol(u.data + v.data)
            return Symbol(None, (u, v), '+')

        if self._op == '*':
            u, v = simplified_prev
            if is_const(u, 0) or is_const(v, 0): return Symbol(0) # 0 * x -> 0
            if is_const(u, 1): return v  # 1 * x -> x
            if is_const(v, 1): return u  # x * 1 -> x
            if is_const(u) and is_const(v): # c1 * c2 -> c3
                return Symbol(u.data * v.data)
            return Symbol(None, (u, v), '*')
        
        if self._op == '**':
            base, = simplified_prev
            exponent = self.data
            if exponent == 1: return base # x ** 1 -> x
            if exponent == 0: return Symbol(1) # x ** 0 -> 1
            if is_const(base):
                if base.data == 1: return Symbol(1) # 1 ** x -> 1
                return Symbol(base.data ** exponent)
            return Symbol(exponent, (base,), '**')

        return self # 若無簡化規則，回傳原節點

    def backward(self):
        topo = []
        visited = set()
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
        build_topo(self)

        variables = [v for v in topo if isinstance(v.data, str) and not v._prev]
        
        for var_node in variables:
            derivative_tree = self.diff(var_node.data)
            var_node.grad = derivative_tree.simplify()

    def __neg__(self):
        return self * -1

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return Symbol(other) + (-self)

    def __rmul__(self, other):
        return self * other

    def __repr__(self):
        if self._op == '':
            return str(self.data)
        
        # 因為 _prev 現在是 tuple，所以順序是固定的
        children_repr = [repr(p) for p in self._prev]

        if self._op == '+':
            return f"({children_repr[0]} + {children_repr[1]})"
        if self._op == '*':
            if children_repr[0] == '-1': return f"-{children_repr[1]}"
            if children_repr[1] == '-1': return f"-{children_repr[0]}"
            return f"({children_repr[0]} * {children_repr[1]})"
        if self._op == '**':
            return f"({children_repr[0]}**{self.data})"
        
        return f"op={self._op}({', '.join(children_repr)})"

# --- 主程式執行區塊 ---

x = Symbol('x')
y = Symbol('y')
z = Symbol('z')

f = x**3 + x*y*z

f.backward()

print(f'gx = {x.grad}')
print(f'gy = {y.grad}')
print(f'gz = {z.grad}')
