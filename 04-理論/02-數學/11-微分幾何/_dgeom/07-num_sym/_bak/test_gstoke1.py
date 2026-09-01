from dgeom.num import TangentVector, Form, d, HyperCube, integrate_form
import numpy as np
# ==========================================
# Part 4: 驗證廣義史托克定理
# ==========================================

if __name__ == "__main__":
    print("=== 廣義史托克定理驗證 (Generalized Stokes' Theorem) ===\n")
    print("定理: ∫_Ω dω = ∫_∂Ω ω\n")

    # --- 設定場景：2維平面上的正方形 ---
    # 區域 Ω: [0, 1] x [0, 1]
    cube = HyperCube([(0, 1), (0, 1)])
    
    # 定義一個 1-form ω
    # ω = P dx + Q dy
    # 我們選一個非線性的: ω = (x^2 + y) dx + (x * y) dy
    # 這是一個 1-form
    
    def omega_func(v): # v 是向量場
        def field(p):
            x, y = p
            vx, vy = v.at(p)
            # ω(v) = (x^2 + y)*vx + (xy)*vy
            return (x**2 + y) * vx + (x * y) * vy
        return field
    
    omega = Form(1, omega_func)
    
    print("1. 定義形式 ω = (x^2 + y) dx + (xy) dy")
    print("2. 定義區域 Ω = [0, 1] x [0, 1] (正方形)")
    
    # --- 計算左側 (LHS): ∫_∂Ω ω ---
    print("\n--- 計算左側: 邊界積分 (∫_∂Ω ω) ---")
    lhs_total = 0.0
    boundaries = cube.get_boundaries()
    
    # 邊界包含 4 個線段 (下, 上, 左, 右)
    boundary_names = ["Left (x=0)", "Right (x=1)", "Bottom (y=0)", "Top (y=1)"] 
    # 注意：順序取決於 get_boundaries 的實作迴圈
    
    for i, (domain_face, sign) in enumerate(boundaries):
        # 這裡 domain_face 是一維線段
        val = integrate_form(omega, domain_face)
        contribution = val * sign
        lhs_total += contribution
        print(f"  邊界片段 {i}: 積分值 = {val:8.5f}, 定向 = {sign:2d} -> 貢獻 = {contribution:8.5f}")

    print(f">> 左側總和 (∫_∂Ω ω) = {lhs_total:.6f}")

    # --- 計算右側 (RHS): ∫_Ω dω ---
    print("\n--- 計算右側: 區域積分 (∫_Ω dω) ---")
    
    # 1. 先計算 dω (變成 2-form)
    d_omega = d(omega)
    
    # 2. 在區域 Ω 上積分
    rhs_total = integrate_form(d_omega, cube)
    
    print(f">> 右側積分 (∫_Ω dω) = {rhs_total:.6f}")

    # --- 結論 ---
    print("\n" + "="*40)
    diff = abs(lhs_total - rhs_total)
    print(f"誤差: {diff:.8e}")
    if diff < 1e-5:
        print("✅ 驗證成功！ 廣義史托克定理成立。")
    else:
        print("❌ 驗證失敗。")

    # --- 加碼：3D 驗證 (高斯散度定理) ---
    print("\n" + "-"*40)
    print("加碼測試：3D 立方體 (對應高斯散度定理)")
    print("-" * 40)
    
    # Ω: [0,1]^3
    cube_3d = HyperCube([(0, 1), (0, 1), (0, 1)])
    
    # 定義 2-form: ω = x dy^dz + y dz^dx + z dx^dy (這對應向量場 F=(x,y,z) 的通量形式)
    # 這裡我們用簡單的定義：ω 吃兩個向量 u, v
    # ω(u, v) = det([F, u, v]) roughly... let's keep it simpler for implementation
    # Let's use ω = x dy^dz. 
    # dy^dz(u, v) = u_y*v_z - u_z*v_y
    
    def omega_3d_func(u, v):
        def field(p):
            x, y, z = p
            # component P = x, acting on dy^dz
            # The value is x * (u_y * v_z - u_z * v_y)
            u_val = u.at(p); v_val = v.at(p)
            det_yz = u_val[1]*v_val[2] - u_val[2]*v_val[1]
            return x * det_yz
        return field
        
    omega_3d = Form(2, omega_3d_func) # 2-form in 3D
    
    # LHS: Integral over 6 faces
    print("計算 3D 邊界積分 (6個面)...")
    lhs_3d = 0.0
    for domain_face, sign in cube_3d.get_boundaries():
        # domain_face is 2D square
        val = integrate_form(omega_3d, domain_face)
        lhs_3d += val * sign
        
    # RHS: Integral of dω over volume
    print("計算 3D 體積積分 (dω)...")
    d_omega_3d = d(omega_3d) # 3-form
    rhs_3d = integrate_form(d_omega_3d, cube_3d)
    
    print(f"LHS (邊界) = {lhs_3d:.6f}")
    print(f"RHS (內部) = {rhs_3d:.6f}")
    
    if abs(lhs_3d - rhs_3d) < 1e-5:
         print("✅ 3D 驗證成功！")