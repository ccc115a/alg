import sympy as sp

def verify_gauss_theorem():
    print("=== 驗證高斯散度定理 (Gauss Divergence Theorem) [3D -> 2D] ===")

    # 1. 定義變數
    x, y, z = sp.symbols('x y z')

    # 2. 定義 2-形式 ω (Flux form)
    # 對應向量場 F = (P, Q, R)
    # 讓我們選一個非線性的場: F = (x^2, y^2, z^2)
    P = x**2
    Q = y**2
    R = z**2
    
    # ω = P dy^dz + Q dz^dx + R dx^dy
    # 注意: dz^dx = -dx^dz，順序很重要，這保證了輪換對稱性
    print(f"1. 形式 ω (2-form):\n   F = ({P}, {Q}, {R})\n   ω = ({P})dy∧dz + ({Q})dz∧dx + ({R})dx∧dy")

    # 3. 計算 dω (3-form, Divergence)
    # dω = (Px + Qy + Rz) dx∧dy∧dz
    div_F = sp.diff(P, x) + sp.diff(Q, y) + sp.diff(R, z)
    print(f"2. 外微分 dω (散度) = ({div_F}) dx∧dy∧dz")

    # 4. 定義流形 M (單位立方體)
    # x, y, z ∈ [0, 1]
    print(f"3. 流形 M: 單位立方體 [0,1] x [0,1] x [0,1]")

    # ================= LHS: ∫_M dω (三重積分) =================
    # 直接在體積上積分散度
    lhs_value = sp.integrate(div_F, (x, 0, 1), (y, 0, 1), (z, 0, 1))
    print(f"4. [LHS] 體積積分 (散度總和): {lhs_value}")

    # ================= RHS: ∫_∂M ω (曲面積分) =================
    # 邊界 ∂M 包含 6 個面。
    # 我們必須將 ω 拉回(Pullback)到每個面上。
    # 參數化變數 u, v
    u, v = sp.symbols('u v')
    rhs_total = 0

    print("5. [RHS] 邊界積分 (6個面):")

    # 定義 6 個面的參數化與對應的「外指方向」符號
    # 格式: (Face Name, x_map, y_map, z_map, orientation_sign)
    # orientation_sign 用於修正參數化後的法向量方向，使其永遠指向「外」
    
    # 簡單起見，我們直接觀察 dx^dy 等項在特定面上的行為：
    # 例如在 z=1 面 (Top)，z是常數，dz=0，只剩 R dx^dy。法向量朝上 (+z)。
    # 在 z=0 面 (Bottom)，dz=0，只剩 R dx^dy。法向量朝下 (-z)，所以積分要變號。
    
    faces = [
        # x = 1 (Front), Normal +x. ω 貢獻項: P dy^dz
        {"name": "x=1 (+x)", "sub": {x: 1, y: u, z: v}, "term": "P", "sign": 1},
        # x = 0 (Back), Normal -x. ω 貢獻項: P dy^dz
        {"name": "x=0 (-x)", "sub": {x: 0, y: u, z: v}, "term": "P", "sign": -1},
        
        # y = 1 (Right), Normal +y. ω 貢獻項: Q dz^dx
        {"name": "y=1 (+y)", "sub": {x: v, y: 1, z: u}, "term": "Q", "sign": 1}, 
        # y = 0 (Left), Normal -y. ω 貢獻項: Q dz^dx
        {"name": "y=0 (-y)", "sub": {x: v, y: 0, z: u}, "term": "Q", "sign": -1},
        
        # z = 1 (Top), Normal +z. ω 貢獻項: R dx^dy
        {"name": "z=1 (+z)", "sub": {x: u, y: v, z: 1}, "term": "R", "sign": 1},
        # z = 0 (Bottom), Normal -z. ω 貢獻項: R dx^dy
        {"name": "z=0 (-z)", "sub": {x: u, y: v, z: 0}, "term": "R", "sign": -1},
    ]

    for face in faces:
        # 1. 根據面選擇對應的分量函數 (P, Q, or R)
        if face["term"] == "P": func = P
        elif face["term"] == "Q": func = Q
        else: func = R
        
        # 2. 將變數替換為參數 (u, v) 或常數
        integrand = func.subs(face["sub"])
        
        # 3. 積分 (u, v 都在 [0, 1]) 並乘上方向符號
        val = sp.integrate(integrand, (u, 0, 1), (v, 0, 1)) * face["sign"]
        
        print(f"   - Face {face['name']}: {val}")
        rhs_total += val

    print(f"   [RHS] 總通量: {rhs_total}")
    
    # ================= 結論 =================
    print("---------------------------------------------------------")
    print(f"驗證結果: {lhs_value} == {rhs_total} ? {lhs_value == rhs_total}")

verify_gauss_theorem()