# ==========================================
# 1. 核心數值微分算子 (沿用上一段的邏輯)
# ==========================================

def get_gradient(f, x, y, z, h=1e-5):
    """計算純量 f 的梯度 -> 回傳向量 [gx, gy, gz]"""
    df_dx = (f(x + h, y, z) - f(x - h, y, z)) / (2 * h)
    df_dy = (f(x, y + h, z) - f(x, y - h, z)) / (2 * h)
    df_dz = (f(x, y, z + h) - f(x, y, z - h)) / (2 * h)
    return [df_dx, df_dy, df_dz]

def get_divergence(F, x, y, z, h=1e-5):
    """計算向量 F 的散度 -> 回傳純量 div"""
    dFx_dx = (F(x + h, y, z)[0] - F(x - h, y, z)[0]) / (2 * h)
    dFy_dy = (F(x, y + h, z)[1] - F(x, y - h, z)[1]) / (2 * h)
    dFz_dz = (F(x, y, z + h)[2] - F(x, y, z - h)[2]) / (2 * h)
    return dFx_dx + dFy_dy + dFz_dz

def get_curl(F, x, y, z, h=1e-5):
    """計算向量 F 的旋度 -> 回傳向量 [Rx, Ry, Rz]"""
    dFz_dy = (F(x, y + h, z)[2] - F(x, y - h, z)[2]) / (2 * h)
    dFy_dz = (F(x, y, z + h)[1] - F(x, y, z - h)[1]) / (2 * h)
    Rx = dFz_dy - dFy_dz
    
    dFx_dz = (F(x, y, z + h)[0] - F(x, y, z - h)[0]) / (2 * h)
    dFz_dx = (F(x + h, y, z)[2] - F(x - h, y, z)[2]) / (2 * h)
    Ry = dFx_dz - dFz_dx
    
    dFy_dx = (F(x + h, y, z)[1] - F(x - h, y, z)[1]) / (2 * h)
    dFx_dy = (F(x, y + h, z)[0] - F(x, y - h, z)[0]) / (2 * h)
    Rz = dFy_dx - dFx_dy
    
    return [Rx, Ry, Rz]

# ==========================================
# 2. 定義測試用的場 (Fields)
# ==========================================

# 定義一個複雜一點的純量場 f(x,y,z) = x^3 * y^2 * z
# 這樣可以確保二階導數不為 0，測試更有意義
def my_scalar_field(x, y, z):
    return (x**3) * (y**2) * z

# 定義一個向量場 F(x,y,z) = [yz, xz, xy] (這其實是 xyz 的梯度，保守場)
# 或者更亂一點： F = [z*y, x*z, x*y*z]
def my_vector_field(x, y, z):
    return [z*y, x*z, x*y*z]

# ==========================================
# 3. 驗證邏輯 (Wrapper Functions)
# ==========================================

def verify_curl_of_gradient():
    """驗證 ∇ × (∇f) = 0"""
    print("=== 驗證 1: 梯度的旋度 (Curl of Gradient) ===")
    
    # 這裡是最關鍵的一步：
    # 我們定義一個「梯度場函數」，它內部呼叫 get_gradient
    # 這樣我們就可以把 gradient_field 當作一個向量場，傳給 get_curl
    def gradient_field(x, y, z):
        return get_gradient(my_scalar_field, x, y, z)
    
    # 測試點
    x, y, z = 1.0, 2.0, 3.0
    
    # 計算 ∇ × (gradient_field)
    result = get_curl(gradient_field, x, y, z)
    
    print(f"純量場 f = x^3 * y^2 * z")
    print(f"在點 ({x}, {y}, {z}) 的計算結果: {result}")
    
    # 檢查誤差 (應極接近 0)
    error = sum(abs(v) for v in result)
    print(f"絕對誤差總和: {error:.2e}")
    if error < 1e-8:
        print(">> 驗證成功！結果趨近於 0向量")
    else:
        print(">> 驗證失敗 (誤差過大)")
    print("-" * 40)

def verify_divergence_of_curl():
    """驗證 ∇ · (∇ × F) = 0"""
    print("=== 驗證 2: 旋度的散度 (Divergence of Curl) ===")
    
    # 同樣技巧：
    # 定義一個「旋度場函數」，內部呼叫 get_curl
    # 這樣就可以把 curl_field 當作向量場，傳給 get_divergence
    def curl_field(x, y, z):
        return get_curl(my_vector_field, x, y, z)
    
    # 測試點
    x, y, z = 1.0, 2.0, 3.0
    
    # 計算 ∇ · (curl_field)
    result = get_divergence(curl_field, x, y, z)
    
    print(f"向量場 F = [zy, xz, xyz]")
    print(f"在點 ({x}, {y}, {z}) 的計算結果: {result}")
    
    # 檢查誤差
    if abs(result) < 1e-8:
        print(f">> 驗證成功！結果 {result:.2e} 趨近於 0")
    else:
        print(">> 驗證失敗")
    print("-" * 40)

# ==========================================
# 4. 執行
# ==========================================
if __name__ == "__main__":
    verify_curl_of_gradient()
    verify_divergence_of_curl()
    