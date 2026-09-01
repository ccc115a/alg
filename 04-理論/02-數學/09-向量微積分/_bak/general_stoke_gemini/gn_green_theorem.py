import sympy as sp

def verify_greens_theorem():
    print("=== 驗證格林公式 (Green's Theorem) [2D -> 1D] ===")
    
    # 1. 定義變數
    x, y = sp.symbols('x y')
    
    # 2. 定義 1-形式 ω = P dx + Q dy
    # 讓我們選一個非平凡的場: F = (-y, x^2)
    P = -y
    Q = x**2
    print(f"1. 形式 ω = ({P})dx + ({Q})dy")
    
    # 3. 計算 dω (相當於 2D 旋度)
    # dω = (dQ/dx - dP/dy) dx∧dy
    curl_2d = sp.diff(Q, x) - sp.diff(P, y)
    print(f"2. 外微分 dω = ({curl_2d}) dx∧dy")
    
    # 4. 定義流形 M (單位圓盤)
    # 使用極座標參數化: x = r*cos(θ), y = r*sin(θ)
    r, theta = sp.symbols('r theta')
    map_x = r * sp.cos(theta)
    map_y = r * sp.sin(theta)
    
    # 區域 D: r ∈ [0, 1], θ ∈ [0, 2π]
    print(f"3. 流形 M (單位圓盤): x=r*cos(θ), y=r*sin(θ)")

    # ================= LHS: ∫_M dω (二重積分) =================
    # 拉回: dx∧dy = Jacobian * dr∧dθ
    # Jacobian J = det([[xr, xθ], [yr, yθ]])
    xr, xt = sp.diff(map_x, r), sp.diff(map_x, theta)
    yr, yt = sp.diff(map_y, r), sp.diff(map_y, theta)
    Jacobian = xr * yt - xt * yr  # 應該等於 r
    
    integrand_lhs = curl_2d.subs({x: map_x, y: map_y}) * Jacobian
    lhs_value = sp.integrate(integrand_lhs, (r, 0, 1), (theta, 0, 2*sp.pi))
    print(f"4. [LHS] 區域積分結果: {lhs_value}")
    
    # ================= RHS: ∫_∂M ω (線積分) =================
    # 邊界 ∂M 是單位圓 (r=1)，參數是 θ
    # 路徑 γ(θ) = (cos θ, sin θ), θ: 0 -> 2π
    
    # 將 x, y 替換為邊界參數式
    x_b = sp.cos(theta)
    y_b = sp.sin(theta)
    
    # 計算 dx, dy (關於 theta)
    dx_b = sp.diff(x_b, theta)
    dy_b = sp.diff(y_b, theta)
    
    # 拉回 ω 到邊界
    # P dx + Q dy -> P(θ) * (dx/dθ) + Q(θ) * (dy/dθ)
    integrand_rhs = (P.subs({x: x_b, y: y_b}) * dx_b + 
                     Q.subs({x: x_b, y: y_b}) * dy_b)
                     
    rhs_value = sp.integrate(integrand_rhs, (theta, 0, 2*sp.pi))
    print(f"5. [RHS] 邊界積分結果: {rhs_value}")
    
    print(f"驗證: {lhs_value} == {rhs_value} ? {lhs_value == rhs_value}\n")

verify_greens_theorem()
