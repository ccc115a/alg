import sympy as sp

def verify_divergence_theorem():
    print("=== 驗證高斯散度定理 (Gauss Divergence Theorem) ===")
    
    # 1. 定義符號
    x, y, z = sp.symbols('x y z')
    
    # 2. 定義向量場 F = <2x, y^2, z^2>
    # 這裡選擇 P=2x, Q=y^2, R=z^2
    F = sp.Matrix([2*x, y**2, z**2])
    print(f"向量場 F: {F.T}")
    print("區域 V: 單位立方體 [0,1] x [0,1] x [0,1]")
    print("-" * 40)

    # ==========================================
    # Part 1: 右邊 (RHS) - 體積分 (Volume Integral)
    # 公式: ∭ (∇ • F) dV
    # ==========================================
    print("--- 計算右邊: 體積分 (散度總和) ---")
    
    # 1. 計算散度 (Divergence) = dP/dx + dQ/dy + dR/dz
    div_F = sp.diff(F[0], x) + sp.diff(F[1], y) + sp.diff(F[2], z)
    print(f"散度 (Div F): {div_F}")
    
    # 2. 進行三重積分
    # 積分順序 dz dy dx (對於立方體，順序不影響)
    # 範圍都是 0 到 1
    rhs_result = sp.integrate(div_F, (z, 0, 1), (y, 0, 1), (x, 0, 1))
    print(f"右邊結果 (RHS): {rhs_result}")

    # ==========================================
    # Part 2: 左邊 (LHS) - 表面積分 (Surface Integral)
    # 公式: ∯ F • n dS
    # 立方體有 6 個面，我們需要分別計算並相加
    # ==========================================
    print("\n--- 計算左邊: 表面積分 (6個面的通量總和) ---")
    
    total_flux = 0
    
    # 定義 6 個面的參數: (固定軸, 固定值, 法向量符號, 積分變數1, 積分變數2)
    # 注意: 法向量必須指向"外部"
    faces = [
        # x 軸方向的面
        ('Right (x=1)', x, 1,  1, y, z), # n = <1, 0, 0>
        ('Left  (x=0)', x, 0, -1, y, z), # n = <-1, 0, 0>
        
        # y 軸方向的面
        ('Top   (y=1)', y, 1,  1, x, z), # n = <0, 1, 0>
        ('Bottom(y=0)', y, 0, -1, x, z), # n = <0, -1, 0>
        
        # z 軸方向的面
        ('Front (z=1)', z, 1,  1, x, y), # n = <0, 0, 1>
        ('Back  (z=0)', z, 0, -1, x, y), # n = <0, 0, -1>
    ]
    
    for name, axis_sym, val, sign, v1, v2 in faces:
        # 1. 根據法向量方向，取出對應的 F 分量 (x->F[0], y->F[1], z->F[2])
        # 若是 x 面，法向量只有 x 分量非 0，點積後只剩 F[0]*sign
        if axis_sym == x:
            component = F[0]
        elif axis_sym == y:
            component = F[1]
        else:
            component = F[2]
            
        # 2. 將固定的軸變數替換為數值 (例如 x=1)
        integrand = component.subs(axis_sym, val) * sign
        
        # 3. 對該面進行二重積分 (範圍 0 到 1)
        flux = sp.integrate(integrand, (v1, 0, 1), (v2, 0, 1))
        
        print(f"面 {name:<12}: 通量 = {flux}")
        total_flux += flux

    print("-" * 30)
    print(f"左邊結果 (LHS 總通量): {total_flux}")

    # ==========================================
    # 比較驗證
    # ==========================================
    print("-" * 30)
    if total_flux == rhs_result:
        print("✅ 驗證成功！ 體積分等於表面通量總和。")
    else:
        print("❌ 驗證失敗。")

if __name__ == "__main__":
    verify_divergence_theorem()