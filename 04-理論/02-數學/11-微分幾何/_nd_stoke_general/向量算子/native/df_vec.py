# ==========================================
# 1. 基礎工具：數值微分
# ==========================================

def numerical_partial_derivative(f, p, index, h=1e-6):
    """
    計算函數 f 在點 p 處，對第 index 個座標的偏導數
    使用中心差分法 (Central Difference)
    """
    # 複製點座標以避免修改原始數據
    p_plus = list(p)
    p_minus = list(p)
    
    # 在指定維度上做微小位移
    p_plus[index] += h
    p_minus[index] -= h
    
    # 計算斜率
    return (f(p_plus) - f(p_minus)) / (2 * h)

# ==========================================
# 2. 向量算子 v(f)
# ==========================================

def create_vector_field(component_funcs):
    """
    建立一個向量場 v
    參數: component_funcs 是一個函數列表，每個函數代表一個分量 v^i(p)
    """
    
    # 這是 v 算子，它接收一個函數 f
    def v_operator(f):
        
        # 回傳一個新的標量場函數 (Directional Derivative Field)
        def resulting_field(p):
            n = len(p)
            
            # 1. 計算該點的向量分量值: v^i(p)
            # 例如：如果向量場是 (2x, y)，這裡會算出具體數字
            v_values = [comp_func(p) for comp_func in component_funcs]
            
            # 2. 計算該點的梯度值: ∂f/∂x^i |p
            grad_values = [numerical_partial_derivative(f, p, i) for i in range(n)]
            
            # 3. 進行點積: Σ v^i * (∂f/∂x^i)
            # 這是 v(f) 的定義
            dot_product = sum(v * g for v, g in zip(v_values, grad_values))
            
            return dot_product
            
        return resulting_field

    return v_operator

# ==========================================
# 3. 1-形式算子 dx^i
# ==========================================

def create_dx_i(index):
    """
    建立 1-形式 dx^i
    它是對偶基底，負責抓取向量的第 i 個分量
    """
    
    # 這是 dx 算子，它接收一個向量場 v
    def dx_operator(vector_field_funcs):
        
        # 回傳一個新的標量場函數
        def resulting_field(p):
            # 1-形式非常簡單：它只是去問向量場「你在這個點的第 i 個分量是多少？」
            # 注意：這裡的 vector_field_funcs 是我們定義向量時傳入的那個函數列表
            target_component_func = vector_field_funcs[index]
            
            return target_component_func(p)
            
        return resulting_field
        
    return dx_operator

# ==========================================
# 實例演示
# ==========================================

# --- 準備工作：定義數學函數 ---

# 地形函數 f(x, y) = x^2 + y^2
# p 是一個列表 [x, y]
def f_mountain(p):
    return p[0]**2 + p[1]**2

# 定義向量場 v 的分量函數
# 假設 v = (3, 4)  <-- 這是常數向量場
def v1_func(p): return 3
def v2_func(p): return 4
v_components = [v1_func, v2_func]

# --- 測試 1: v(f) ---

print("--- 測試 v(f) ---")
# 1. 創建向量算子 v
v = create_vector_field(v_components)

# 2. 讓 v 作用在 f 上，得到方向導數函數 df_v
df_v = v(f_mountain)

# 3. 代入點 p=(1, 2)
p = [1, 2]
result_v = df_v(p)

print(f"函數 f = x^2 + y^2")
print(f"向量 v = (3, 4)")
print(f"點 p = {p}")
print(f"v(f) 在 p 點的計算結果: {result_v:.5f}") # 預期 22.0
# 驗證：∇f=(2x, 2y)|(1,2) = (2, 4)。 v=(3,4)。 dot = 2*3 + 4*4 = 22。

# --- 測試 2: dx(v) ---

print("\n--- 測試 dx^i(v) ---")
# 1. 創建 1-形式 dx (index 0) 和 dy (index 1)
dx = create_dx_i(0)
dy = create_dx_i(1)

# 2. 定義一個變動的向量場 u = (2x, x*y)
# 這需要定義成函數
def u1_func(p): return 2 * p[0]      # 2x
def u2_func(p): return p[0] * p[1]   # x*y
u_components = [u1_func, u2_func]

# 注意：這裡我們不需要先創建 u 的算子物件，
# 因為 dx^i 只需要向量的「分量規則 (u_components)」
# (這取決於你如何定義向量物件，這裡我們直接用分量函數列表代表向量)

# 3. 運算
result_dx = dx(u_components)(p) # 應該抓出 2x = 2*1 = 2
result_dy = dy(u_components)(p) # 應該抓出 xy = 1*2 = 2

print(f"變動向量場 u = (2x, xy)")
print(f"dx(u) 在 p={p} 的值 (應為 2x): {result_dx}")
print(f"dy(u) 在 p={p} 的值 (應為 xy): {result_dy}")

# --- 測試 3: 驗證 v(f) == df(v) ---
# 這是微分幾何最核心的對偶性： v 作用於 f 等同於 df 作用於 v
# df = (∂f/∂x)dx + (∂f/∂y)dy

print("\n--- 測試對偶性: v(f) vs df(v) ---")

# 我們手動構建 df(v)
# df(v) = (∂f/∂x) * dx(v) + (∂f/∂y) * dy(v)

grad_x = numerical_partial_derivative(f_mountain, p, 0) # ∂f/∂x
grad_y = numerical_partial_derivative(f_mountain, p, 1) # ∂f/∂y
val_dx = dx(v_components)(p) # v^x
val_dy = dy(v_components)(p) # v^y

df_v_manual = grad_x * val_dx + grad_y * val_dy

print(f"v(f) 直接計算: {result_v:.5f}")
print(f"df(v) 展開計算: {df_v_manual:.5f}")