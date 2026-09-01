import sympy as sp

def verify_greens_theorem():
    # 1. 定義符號
    x, y, t, r, theta = sp.symbols('x y t r theta')

    # 2. 定義向量場函數 L(x, y) 和 M(x, y)
    # 這裡我們隨意選定一個非平凡的例子: F = (x^2 - y) i + (x + y^2) j
    L = x**2 - y
    M = x + y**2

    print(f"驗證格林定理:")
    print(f"向量場 F = <{L}, {M}>")
    print(f"區域 D: 單位圓 (半徑=1)")
    print("-" * 30)

    # ==========================================
    # 左邊 (LHS): 線積分 (Line Integral)
    # 公式: ∮ (L dx + M dy)
    # ==========================================
    
    # 參數化單位圓: x = cos(t), y = sin(t), t 從 0 到 2*pi
    x_t = sp.cos(t)
    y_t = sp.sin(t)

    # 計算微分 dx 和 dy
    dx_dt = sp.diff(x_t, t)  # dx = -sin(t) dt
    dy_dt = sp.diff(y_t, t)  # dy = cos(t) dt

    # 將 L 和 M 中的 x, y 替換為參數 t
    L_t = L.subs({x: x_t, y: y_t})
    M_t = M.subs({x: x_t, y: y_t})

    # 組合被積函數: L*dx + M*dy
    integrand_line = L_t * dx_dt + M_t * dy_dt

    # 計算定積分 (從 0 到 2*pi)
    lhs_result = sp.integrate(integrand_line, (t, 0, 2 * sp.pi))
    
    print(f"左邊 (線積分) 結果: {lhs_result}")

    # ==========================================
    # 右邊 (RHS): 二重積分 (Double Integral)
    # 公式: ∬ (∂M/∂x - ∂L/∂y) dA
    # ==========================================

    # 計算偏導數
    dM_dx = sp.diff(M, x)
    dL_dy = sp.diff(L, y)
    curl_z = dM_dx - dL_dy  # 旋度 z 分量

    print(f"旋度 (∂M/∂x - ∂L/∂y) = {curl_z}")

    # 為了方便在圓形區域積分，我們切換到極座標 (Polar Coordinates)
    # x = r*cos(theta), y = r*sin(theta), dA = r dr dtheta
    # 這裡 curl_z 算出來是常數 2，但如果是變數，下方替換就很重要
    curl_polar = curl_z.subs({x: r * sp.cos(theta), y: r * sp.sin(theta)})
    
    # 加入 Jacobian (r)
    integrand_double = curl_polar * r

    # 進行二重積分
    # 內層對 r 積分 (0 到 1)
    # 外層對 theta 積分 (0 到 2*pi)
    rhs_result = sp.integrate(integrand_double, (r, 0, 1), (theta, 0, 2 * sp.pi))

    print(f"右邊 (二重積分) 結果: {rhs_result}")
    print("-" * 30)

    # ==========================================
    # 比較結果
    # ==========================================
    if lhs_result == rhs_result:
        print("✅ 驗證成功！左右兩邊相等。")
    else:
        print("❌ 驗證失敗。")

if __name__ == "__main__":
    verify_greens_theorem()