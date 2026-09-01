import sympy as sp

def calculate_gradient(scalar_field, variables):
    """
    計算純量場的梯度 (Gradient)
    公式: [df/dx, df/dy, df/dz]
    """
    return [sp.diff(scalar_field, var) for var in variables]

def calculate_divergence(vector_field, variables):
    """
    計算向量場的散度 (Divergence)
    公式: dFx/dx + dFy/dy + dFz/dz
    """
    assert len(vector_field) == len(variables), "維度不匹配"
    return sum(sp.diff(vector_field[i], variables[i]) for i in range(len(variables)))

def calculate_curl(vector_field, variables):
    """
    計算向量場的旋度 (Curl) - 僅適用於 3D
    公式: determinant of matrix [[i, j, k], [d/dx, d/dy, d/dz], [Fx, Fy, Fz]]
    結果: [dFz/dy - dFy/dz, dFx/dz - dFz/dx, dFy/dx - dFx/dy]
    """
    if len(variables) != 3:
        raise ValueError("旋度計算通常定義在 3D 空間")
        
    x, y, z = variables
    Fx, Fy, Fz = vector_field
    
    curl_x = sp.diff(Fz, y) - sp.diff(Fy, z)
    curl_y = sp.diff(Fx, z) - sp.diff(Fz, x)
    curl_z = sp.diff(Fy, x) - sp.diff(Fx, y)
    
    return [curl_x, curl_y, curl_z]

# ==========================================
# 測試區 (Testing)
# ==========================================

if __name__ == "__main__":
    # 1. 定義符號變數 (x, y, z)
    x, y, z = sp.symbols('x y z')
    vars_3d = (x, y, z)
    
    print("=== 測試 1: 梯度 (Gradient) ===")
    # 定義純量場 f(x,y,z) = x^2 + y^2 + z^2
    f = x**2 + y**2 + z**2
    grad_f = calculate_gradient(f, vars_3d)
    print(f"純量場 f = {f}")
    print(f"梯度 ∇f = {grad_f}")
    print("-" * 30)

    print("=== 測試 2: 散度 (Divergence) ===")
    # 定義向量場 F = [x^2, y^2, z^2]
    F_div = [x**2, y**2, z**2]
    div_val = calculate_divergence(F_div, vars_3d)
    print(f"向量場 F = {F_div}")
    print(f"散度 ∇·F = {div_val}")
    print("-" * 30)

    print("=== 測試 3: 旋度 (Curl) ===")
    # 定義一個旋轉場 F = [-y, x, 0] (這是一個繞 Z 軸旋轉的場)
    F_curl = [-y, x, 0]
    curl_val = calculate_curl(F_curl, vars_3d)
    print(f"向量場 F = {F_curl}")
    print(f"旋度 ∇×F = {curl_val}")
    # 預期結果應該是 [0, 0, 2]，代表 Z 軸方向的旋轉量
    print("-" * 30)

    print("=== 測試 4: 混合測試 (保守場的旋度為 0) ===")
    # 保守場 F = ∇(xyz) = [yz, xz, xy]
    F_conservative = [y*z, x*z, x*y]
    curl_cons = calculate_curl(F_conservative, vars_3d)
    print(f"向量場 F = {F_conservative}")
    print(f"旋度 ∇×F = {curl_cons} (預期應全為 0)")