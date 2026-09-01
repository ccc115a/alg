import sympy as sp

def verify_stokes_theorem():
    print("--- 驗證廣義斯托克斯定理 (Stokes' Theorem) ---")
    print("公式: ∫_M dω = ∫_{∂M} ω\n")
    
    # 定義符號
    x, y, z = sp.symbols('x y z', real=True)
    
    # 1. 定義微分形式 ω (1-form)
    # ω = P dx + Q dy + R dz
    # 讓我們選一個經典場： ω = -y dx + x dy + 0 dz
    # 這對應於向量場 F = (-y, x, 0)，是一個繞 z 軸旋轉的場
    P = -y
    Q = x
    # [修正] 將 0 改為 sp.Integer(0)，這樣它才會有 .diff() 方法
    R = sp.Integer(0) 
    
    print(f"1-形式 ω = ({P}) dx + ({Q}) dy + ({R}) dz")
    
    # 2. 計算外微分 dω (Exterior Derivative)
    # [備註] 或者也可以將下方的 .diff(var) 改為 sp.diff(R, var)，那樣也能接受普通整數
    
    # 計算旋度分量
    curl_x = R.diff(y) - Q.diff(z) # 這裡原本會報錯，現在修復了
    curl_y = P.diff(z) - R.diff(x) 
    curl_z = Q.diff(x) - P.diff(y) 
        
    print(f"\n[計算外微分 dω]")
    print(f"dω = ({curl_x}) dy∧dz + ({curl_y}) dz∧dx + ({curl_z}) dx∧dy")
    # 對於我們的 ω，預期結果應該是 0 dy^dz + 0 dz^dx + 2 dx^dy
    
    # -------------------------------------------------------
    # 3. 左側積分: ∫_M dω (曲面積分)
    # M 是上半球面 x^2 + y^2 + z^2 = 1, z >= 0
    # 我們使用球坐標參數化來計算積分
    # -------------------------------------------------------
    print("\n[左側: 計算 ∫_M dω]")
    phi, theta = sp.symbols('phi theta', real=True)
    # phi: 0->pi/2 (上半球), theta: 0->2pi
    
    # 參數化
    r_sphere = 1
    x_param = r_sphere * sp.sin(phi) * sp.cos(theta)
    y_param = r_sphere * sp.sin(phi) * sp.sin(theta)
    
    # 我們需要計算 pullback (拉回)
    # 在 M 上，dx ∧ dy 對應什麼？
    # Jacobian J = d(x,y)/d(phi, theta)
    J = sp.Matrix([x_param, y_param]).jacobian([phi, theta])
    det_J = J.det()
    
    # 我們的 dω 只有 dx^dy 項 (係數為 2)
    # 所以積分變為 ∫∫ 2 * det_J dphi dtheta
    integrand_M = curl_z * det_J
    
    # 化簡
    integrand_M = sp.simplify(integrand_M)
    print(f"參數化後的被積函數 (拉回): {integrand_M} dφ dθ")
    
    # 執行雙重積分
    lhs = sp.integrate(integrand_M, (phi, 0, sp.pi/2), (theta, 0, 2*sp.pi))
    print(f"左側積分結果: {lhs}")
    
    # -------------------------------------------------------
    # 4. 右側積分: ∫_{∂M} ω (線積分)
    # ∂M 是赤道圓 x^2 + y^2 = 1, z = 0
    # 參數化: t 從 0 到 2pi
    # -------------------------------------------------------
    print("\n[右側: 計算 ∫_{∂M} ω]")
    t = sp.symbols('t', real=True)
    x_b = sp.cos(t)
    y_b = sp.sin(t)
    z_b = 0
    
    # 計算微分 dx, dy, dz
    dx_b = x_b.diff(t)
    dy_b = y_b.diff(t)
    dz_b = 0
    
    # 代入 ω = -y dx + x dy
    # integral ( -y(t)*x'(t) + x(t)*y'(t) ) dt
    integrand_boundary = (P.subs({x:x_b, y:y_b}) * dx_b + 
                          Q.subs({x:x_b, y:y_b}) * dy_b)
    
    integrand_boundary = sp.simplify(integrand_boundary)
    print(f"邊界上的被積函數: {integrand_boundary} dt")
    
    rhs = sp.integrate(integrand_boundary, (t, 0, 2*sp.pi))
    print(f"右側積分結果: {rhs}")
    
    # -------------------------------------------------------
    # 5. 結論
    # -------------------------------------------------------
    print("-" * 30)
    if lhs == rhs:
        print(f"驗證成功！ {lhs} = {rhs}")
        print("廣義斯托克斯定理成立。")
    else:
        print("驗證失敗。請檢查計算步驟。")

if __name__ == "__main__":
    verify_stokes_theorem()