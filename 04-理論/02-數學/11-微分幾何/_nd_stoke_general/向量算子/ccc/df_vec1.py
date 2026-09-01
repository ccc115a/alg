import numpy as np
# 偏導數計算函數
def partial_derivative(f, p, index, h=1e-6):
    """
    計算函數 f 在點 p 處，對第 index 個座標的偏導數
    """
    # 複製點座標以避免修改原始數據
    p_plus = list(p)
    p_plus[index] += h
    # 計算斜率
    return (f(p_plus) - f(p)) / h

def gradient(f, p):
    """
    計算函數 f 在點 p 的梯度向量 (∇f)。
    回傳一個列表。
    """
    n = len(p)
    grad = [0] * n
    
    # 對每個維度計算偏導數
    for i in range(n):
        grad[i] = partial_derivative(f, p, i)
        
    return grad

class Vector:
    def __init__(self, v):
        self.v = v
        
    def __call__(self, f):
        def resulting_field(p):
            grad_f = gradient(f, p)
            return np.dot(grad_f, self.v)
        return resulting_field

    def __repr__(self):
        return f"Vector({self.v})"

def d_operator(f):
    """
    d 算子：接收純量場 f
    回傳：一個 1-form 函數 df(v, p)
    """
    def df(v, p):
        # 1. 算出 f 在 p 點的梯度 (Gradient)
        grad_f = gradient(f, p)
        # 2. 執行 df(v) = ∇f · v
        return np.dot(grad_f, v.v)
        
    return lambda v:lambda p: df(v, p)

# 定義 f
def f(p):
    x,y = p
    return x**2 + y**2

# 1. 產生 df
df = d_operator(f)

# 2. 定義向量 v 和 點 p (純數據)
v = Vector([3, 4])
p = np.array([1, 2])

# 3. 計算
value1 = df(v)(p) # 22.0
value2 = v(f)(p) # 22.0
print(f"在點 {p} 處，沿向量 {v} 的方向導數為: df(v)(p)={value1}, v(f)(p)={value2}")