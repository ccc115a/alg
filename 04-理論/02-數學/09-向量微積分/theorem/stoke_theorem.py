import sympy as sp

def verify_stokes_theorem():
    print("=== 驗證史托克定理 (Stokes' Theorem) ===")
    
    # 1. 定義符號
    # x, y, z 用於定義向量場
    # t 用於曲線參數化
    # r, theta 用於曲面參數化 (極座標)
    x, y, z, t, r, theta = sp.symbols('x y z t r theta')

    # 2. 定義向量場 F = <y, z, x>
    # P=y, Q=z, R=x
    F = sp.Matrix([y, z, x])
    print(f"向量場 F: {F.T}")

    # ==========================================
    # Part 1: 左邊 (LHS) - 線積分 ∮ F • dr
    # 路徑 C: z=0 的單位圓 (逆時針)
    # ==========================================
    print("\n--- 計算左邊: 線積分 (沿著邊界 C) ---")
    
    # 參數化曲線
    path_x = sp.cos(t)
    path_y = sp.sin(t)
    path_z = 0  # 在 xy 平面上
    
    # 位置向量 r(t)
    r_vec = sp.Matrix([path_x, path_y, path_z])
    
    # 計算 dr (對 t 微分)
    dr_dt = sp.diff(r_vec, t)
    
    # 將 F 中的 x,y,z 替換為參數 t 的形式
    F_on_path = F.subs({x: path_x, y: path_y, z: path_z})
    
    # 計算點積 F • dr
    integrand_line = F_on_path.dot(dr_dt)
    
    # 積分範圍: 0 到 2*pi
    lhs_result = sp.integrate(integrand_line, (t, 0, 2*sp.pi))
    print(f"左邊結果 (LHS): {lhs_result}")

    # ==========================================
    # Part 2: 右邊 (RHS) - 面積分 ∬ (Curl F) • dS
    # 曲面 S: 拋物面 z = 1 - x^2 - y^2
    # ==========================================
    print("\n--- 計算右邊: 面積分 (通過曲面 S) ---")
    
    # 1. 計算旋度 Curl F = ∇ × F
    # Curl F = (dR/dy - dQ/dz) i + (dP/dz - dR/dx) j + (dQ/dx - dP/dy) k
    # F = [y, z, x] => P=y, Q=z, R=x
    P, Q, R = F[0], F[1], F[2]
    curl_x = sp.diff(R, y) - sp.diff(Q, z) # d(x)/dy - d(z)/dz = 0 - 1 = -1
    curl_y = sp.diff(P, z) - sp.diff(R, x) # d(y)/dz - d(x)/dx = 0 - 1 = -1
    curl_z = sp.diff(Q, x) - sp.diff(P, y) # d(z)/dx - d(y)/dy = 0 - 1 = -1
    
    Curl_F = sp.Matrix([curl_x, curl_y, curl_z])
    print(f"旋度 (Curl F): {Curl_F.T}")

    # 2. 參數化曲面 S (使用極座標 r, theta)
    # x = r cos(theta), y = r sin(theta)
    # z = 1 - x^2 - y^2 = 1 - r^2
    surf_x = r * sp.cos(theta)
    surf_y = r * sp.sin(theta)
    surf_z = 1 - r**2
    r_surf = sp.Matrix([surf_x, surf_y, surf_z])

    # 3. 計算法向量 dS = (dr/dr X dr/dtheta)
    # 先求偏導數切向量
    T_r = sp.diff(r_surf, r)
    T_theta = sp.diff(r_surf, theta)
    
    # 外積得到法向量 n (包含面積元素因子)
    # 注意方向: 需符合右手定則，這裡 z 分量應該是正的 (指向上方)
    normal_vec = T_r.cross(T_theta)
    # 簡化一下顯示
    normal_vec = sp.simplify(normal_vec)
    # print(f"法向量 dS (未標準化): {normal_vec.T}") 
    
    # 4. 將 Curl F 限制在曲面上 (雖然這裡是常數 <-1,-1,-1>，不需替換變數，但正規步驟需要)
    Curl_on_surf = Curl_F.subs({x: surf_x, y: surf_y, z: surf_z})
    
    # 5. 計算通量: (Curl F) • dS
    integrand_surf = Curl_on_surf.dot(normal_vec)
    
    # 6. 進行二重積分
    # r: 0 到 1, theta: 0 到 2*pi
    rhs_result = sp.integrate(integrand_surf, (r, 0, 1), (theta, 0, 2*sp.pi))
    print(f"右邊結果 (RHS): {rhs_result}")

    # ==========================================
    # 比較驗證
    # ==========================================
    print("-" * 30)
    if lhs_result == rhs_result:
        print("✅ 驗證成功！ 左右兩邊相等。")
    else:
        print("❌ 驗證失敗。")

if __name__ == "__main__":
    verify_stokes_theorem()
