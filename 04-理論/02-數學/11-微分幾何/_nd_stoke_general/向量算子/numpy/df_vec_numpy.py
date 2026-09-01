import numpy as np

# ==========================================
# 1. 核心工具：數值梯度 (Numerical Gradient)
# ==========================================

def numerical_gradient(f, p, h=1e-6):
    """
    計算標量場 f 在點 p 的梯度向量 (∇f)。
    回傳一個 numpy array。
    """
    p = np.array(p, dtype=float)
    n = len(p)
    grad = np.zeros(n)
    
    # 對每個維度做微小擾動
    # 雖然 numpy 支援廣播，但為了理解清晰，我們針對每個維度迭代
    for i in range(n):
        # 建立單位基底向量 e_i
        e_i = np.zeros(n)
        e_i[i] = 1.0
        
        # 中心差分法: (f(p + h*e_i) - f(p - h*e_i)) / 2h
        grad[i] = (f(p + h * e_i) - f(p - h * e_i)) / (2 * h)
        
    return grad

# ==========================================
# 2. 向量算子 v(f)
# ==========================================

def create_vector_operator(vector_field_func):
    """
    建立向量算子 v
    
    參數: 
    vector_field_func: 一個函數，接收點 p (array)，回傳向量 v_p (array)
    """
    
    # v 是一個算子，接收函數 f
    def v_operator(f):
        
        # 回傳一個新的標量場函數 (方向導數場)
        def resulting_field(p):
            p = np.array(p, dtype=float)
            
            # 1. 算出該點的向量 v
            v_vec = vector_field_func(p) 
            
            # 2. 算出該點的梯度 ∇f
            grad_vec = numerical_gradient(f, p)
            
            # 3. 核心運算：v(f) = v · ∇f
            # numpy 的 dot 可以直接處理陣列點積
            return np.dot(v_vec, grad_vec)
            
        return resulting_field

    return v_operator

# ==========================================
# 3. 1-形式算子 dx^i
# ==========================================

def create_dx_operator(index):
    """
    建立 1-形式 dx^i
    """
    
    # dx 接收一個向量場函數 v_func
    def dx_operator(vector_field_func):
        
        # 回傳一個新的標量場函數
        def resulting_field(p):
            p = np.array(p, dtype=float)
            
            # 取得向量
            v_vec = vector_field_func(p)
            
            # 1-形式的作用：取第 i 個分量
            return v_vec[index]
            
        return resulting_field
        
    return dx_operator

# ==========================================
# 實例演示
# ==========================================

# --- 準備工作 ---

# 地形函數 f(x, y) = x^2 + y^2
def f_mountain(p):
    # numpy 寫法：直接對陣列平方後求和
    return np.sum(p**2)

# 定義向量場 v = (2x, xy)
# 這是一個 vector valued function
def vector_field_u(p):
    x, y = p
    return np.array([2*x, x*y])

# --- 測試 1: v(f) ---

print("--- 測試 v(f) 使用 Numpy ---")

# 1. 創建向量算子 u
u_op = create_vector_operator(vector_field_u)

# 2. 作用在 f 上
du_f = u_op(f_mountain)

# 3. 代入點 p=(3, 4)
p_val = np.array([3.0, 4.0])
result_u = du_f(p_val)

print(f"點 p = {p_val}")
print(f"向量 u(p) = {vector_field_u(p_val)}") # [6, 12]
print(f"梯度 ∇f(p) = {numerical_gradient(f_mountain, p_val)}") # [6, 8]
print(f"u(f) 計算結果: {result_u}") 
# 驗證: dot([6, 12], [6, 8]) = 36 + 96 = 132

# --- 測試 2: dx^i(v) ---

print("\n--- 測試 dx^i(u) ---")

dx = create_dx_operator(0) # dx
dy = create_dx_operator(1) # dy

# dx 吃掉向量場 u
val_dx = dx(vector_field_u)(p_val)
# dy 吃掉向量場 u
val_dy = dy(vector_field_u)(p_val)

print(f"dx(u) 在 p 的值 (應該是 2x=6): {val_dx}")
print(f"dy(u) 在 p 的值 (應該是 xy=12): {val_dy}")

# --- 測試 3: 驗證 v(f) == df(v) ---

print("\n--- 驗證對偶性 v(f) == df(v) ---")

# 我們來構建 df(v) = (∂f/∂x)dx(v) + (∂f/∂y)dy(v)
grad_at_p = numerical_gradient(f_mountain, p_val) # [6, 8]

# 手動做張量縮併 (Tensor Contraction)
# term1 = (∂f/∂x) * dx(v)
term1 = grad_at_p[0] * val_dx 
# term2 = (∂f/∂y) * dy(v)
term2 = grad_at_p[1] * val_dy

total = term1 + term2

print(f"v(f) (直接點積): {result_u}")
print(f"df(v) (線性組合): {total}")
print(f"是否相等? {np.isclose(result_u, total)}")