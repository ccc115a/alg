# ==========================================
# 核心計算模組 (無迴圈，純數學公式)
# ==========================================

def get_gradient(f, x, y, z, h=1e-5):
    """
    計算純量函數 f 在 (x,y,z) 的梯度
    Gradient = [df/dx, df/dy, df/dz]
    """
    # 對 x 微分 (中央差分)
    df_dx = (f(x + h, y, z) - f(x - h, y, z)) / (2 * h)
    
    # 對 y 微分
    df_dy = (f(x, y + h, z) - f(x, y - h, z)) / (2 * h)
    
    # 對 z 微分
    df_dz = (f(x, y, z + h) - f(x, y, z - h)) / (2 * h)
    
    return [df_dx, df_dy, df_dz]

def get_divergence(F, x, y, z, h=1e-5):
    """
    計算向量函數 F 在 (x,y,z) 的散度
    F 回傳 [Fx, Fy, Fz]
    Divergence = dFx/dx + dFy/dy + dFz/dz
    """
    # Fx 對 x 微分 (注意：取 F 回傳列表的第 0 個元素)
    dFx_dx = (F(x + h, y, z)[0] - F(x - h, y, z)[0]) / (2 * h)
    
    # Fy 對 y 微分 (取第 1 個元素)
    dFy_dy = (F(x, y + h, z)[1] - F(x, y - h, z)[1]) / (2 * h)
    
    # Fz 對 z 微分 (取第 2 個元素)
    dFz_dz = (F(x, y, z + h)[2] - F(x, y, z - h)[2]) / (2 * h)
    
    return dFx_dx + dFy_dy + dFz_dz

def get_curl(F, x, y, z, h=1e-5):
    """
    計算向量函數 F 在 (x,y,z) 的旋度
    Curl = [Rx, Ry, Rz]
    """
    # 為了閱讀方便，先算出需要的偏微分項
    
    # dFz/dy 和 dFy/dz
    dFz_dy = (F(x, y + h, z)[2] - F(x, y - h, z)[2]) / (2 * h)
    dFy_dz = (F(x, y, z + h)[1] - F(x, y, z - h)[1]) / (2 * h)
    Rx = dFz_dy - dFy_dz
    
    # dFx/dz 和 dFz/dx
    dFx_dz = (F(x, y, z + h)[0] - F(x, y, z - h)[0]) / (2 * h)
    dFz_dx = (F(x + h, y, z)[2] - F(x - h, y, z)[2]) / (2 * h)
    Ry = dFx_dz - dFz_dx
    
    # dFy/dx 和 dFx/dy
    dFy_dx = (F(x + h, y, z)[1] - F(x - h, y, z)[1]) / (2 * h)
    dFx_dy = (F(x, y + h, z)[0] - F(x, y - h, z)[0]) / (2 * h)
    Rz = dFy_dx - dFx_dy
    
    return [Rx, Ry, Rz]

# ==========================================
# 使用者定義區 (定義你的場函數)
# ==========================================

# 1. 定義純量場 f(x,y,z) = x^2 + y^2 + z^2
def my_scalar_field(x, y, z):
    return x**2 + y**2 + z**2

# 2. 定義向量場 F(x,y,z) = [x, y, z] (向外發散)
def my_vector_field_div(x, y, z):
    return [x, y, z]

# 3. 定義向量場 F(x,y,z) = [-y, x, 0] (旋轉)
def my_vector_field_curl(x, y, z):
    return [-y, x, 0]

# ==========================================
# 測試區
# ==========================================

if __name__ == "__main__":
    # 設定測試點
    x0, y0, z0 = 1.0, 2.0, 3.0
    
    print(f"測試點: ({x0}, {y0}, {z0})")
    print("-" * 30)

    # --- 測試梯度 ---
    # 理論值: [2x, 2y, 2z] -> [2, 4, 6]
    grad = get_gradient(my_scalar_field, x0, y0, z0)
    print("【梯度 Gradient】")
    print(f"計算結果: [{grad[0]:.4f}, {grad[1]:.4f}, {grad[2]:.4f}]")
    print(f"理論結果: [{2*x0:.4f}, {2*y0:.4f}, {2*z0:.4f}]")
    print("-" * 30)

    # --- 測試散度 ---
    # 理論值: dx/dx + dy/dy + dz/dz = 1+1+1 = 3
    div = get_divergence(my_vector_field_div, x0, y0, z0)
    print("【散度 Divergence】")
    print(f"計算結果: {div:.4f}")
    print(f"理論結果: 3.0000")
    print("-" * 30)

    # --- 測試旋度 ---
    # 理論值: [0, 0, 2]
    curl = get_curl(my_vector_field_curl, x0, y0, z0)
    print("【旋度 Curl】")
    print(f"計算結果: [{curl[0]:.4f}, {curl[1]:.4f}, {curl[2]:.4f}]")
    print(f"理論結果: [0.0000, 0.0000, 2.0000]")
