import numpy as np

# --- 1. 基礎數學運算 (保持不變) ---
def partial_derivative(f, p, index, h=1e-6):
    # 這裡稍微優化：確保 p 是浮點數陣列，避免整數運算誤差
    p_arr = np.array(p, dtype=float)
    p_plus = p_arr.copy()
    p_plus[index] += h
    return (f(p_plus) - f(p_arr)) / h

def gradient(f, p):
    n = len(p)
    return np.array([partial_derivative(f, p, i) for i in range(n)])

# --- 2. 向量類別 (核心亮點) ---
class Vector:
    def __init__(self, v):
        # 轉成 array 方便後續計算
        self.v = np.array(v, dtype=float)
        
    def __call__(self, f):
        """
        實作 v(f)：向量作為微分算子
        回傳：一個函數 field(p)
        """
        def resulting_field(p):
            grad_f = gradient(f, p)
            return np.dot(grad_f, self.v)
        return resulting_field

    def __repr__(self):
        return f"Vector({list(self.v)})"

# --- 3. d 算子 (哲學優化版) ---
def d_operator(f):
    """
    d 算子：外微分
    根據定義：df(v) ≡ v(f)
    """
    return lambda v: v(f)

# --- 4. 測試 ---

# 定義地形函數 f
def f(p):
    x, y = p
    return x**2 + y**2

# 產生 df
df = d_operator(f)

# 定義向量 v (常數向量場)
v = Vector([3, 4])
p = np.array([1, 2])

# 計算
# 1. 右式 v(f)(p): 向量主動去微分函數
value_vf = v(f)(p) 

# 2. 左式 df(v)(p): 1-form 吃掉向量
# 注意：因為我們定義 df 回傳 lambda v: v(f)
# 所以這裡其實就是在執行 v(f)(p)，這就是「定義即實作」
value_df = df(v)(p)

print(f"位置 p={p}")
print(f"向量 v={v}")
print(f"v(f)(p) = {value_vf}")
print(f"df(v)(p) = {value_df}")

# 驗證
# assert value_vf == value_df == 22.0