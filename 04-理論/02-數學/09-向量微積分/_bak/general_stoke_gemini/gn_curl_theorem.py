# $$\int_{M} d\omega = \int_{\partial M} \omega$$

import sympy as sp

def verify_stokes_theorem():
    # 1. 定義 R^3 空間的座標與微分基底
    # ---------------------------------------------------------
    # 我們使用 SymPy 的符號變數
    x, y, z = sp.symbols('x y z')
    dx, dy, dz = sp.symbols('dx dy dz') # 這裡暫時視為符號，後續透過替換規則處理運算

    # 2. 定義 1-形式 omega (任意選擇)
    # ---------------------------------------------------------
    # 假設 omega = z*dx + x*dy + y*dz
    # 這是我們要驗證的被積量
    P, Q, R = z, x, y
    omega_str = f"({P})dx + ({Q})dy + ({R})dz"
    
    print(f"1. 定義 1-形式 omega:\n   ω = {omega_str}\n")

    # 3. 計算外微分 d(omega) -> 2-形式
    # ---------------------------------------------------------
    # d(P dx + Q dy + R dz) 
    # = (Ry - Qz) dy^dz + (Pz - Rx) dz^dx + (Qx - Py) dx^dy
    # 這裡手動實現外微分規則 (Curl in R3)
    
    # 偏微分計算
    Ry, Qz = sp.diff(R, y), sp.diff(Q, z)
    Pz, Rx = sp.diff(P, z), sp.diff(R, x)
    Qx, Py = sp.diff(Q, x), sp.diff(P, y)

    # 係數
    c_dydz = Ry - Qz
    c_dzdx = Pz - Rx
    c_dxdy = Qx - Py
    
    print(f"2. 計算外微分 dω:\n   dω = ({c_dydz}) dy∧dz + ({c_dzdx}) dz∧dx + ({c_dxdy}) dx∧dy\n")

    # 4. 定義流形 M (參數化曲面)
    # ---------------------------------------------------------
    # 參數 u, v 定義域為 [0, 1] x [0, 1]
    u, v = sp.symbols('u v')
    
    # 定義曲面: z = u^2 + v^2 (拋物面), x=u, y=v
    map_x = u
    map_y = v
    map_z = u**2 + v**2
    
    print(f"3. 定義流形 M (參數化):\n   x(u,v)={map_x}, y(u,v)={map_y}, z(u,v)={map_z}")
    print(f"   區域 D: u ∈ [0, 1], v ∈ [0, 1]\n")

    # =========================================================
    # LHS: 計算 M 上的 dω 積分 (Surface Integral)
    # =========================================================
    
    # 計算 Jacobian 轉換 (Pullback)
    # dx = (dx/du)du + (dx/dv)dv
    xu, xv = sp.diff(map_x, u), sp.diff(map_x, v)
    yu, yv = sp.diff(map_y, u), sp.diff(map_y, v)
    zu, zv = sp.diff(map_z, u), sp.diff(map_z, v)

    # 計算外積項轉換成 du^dv (Jacobian Determinants)
    # dy^dz -> (yu*zv - yv*zu) du^dv
    J_dydz = yu * zv - yv * zu
    # dz^dx -> (zu*xv - zv*xu) du^dv
    J_dzdx = zu * xv - zv * xu
    # dx^dy -> (xu*yv - xv*yu) du^dv
    J_dxdy = xu * yv - xv * yu

    # 將 dω 拉回到 u, v 空間
    # 代入 x, y, z 的參數式到係數中
    integrand_LHS = (
        c_dydz.subs({x: map_x, y: map_y, z: map_z}) * J_dydz +
        c_dzdx.subs({x: map_x, y: map_y, z: map_z}) * J_dzdx +
        c_dxdy.subs({x: map_x, y: map_y, z: map_z}) * J_dxdy
    )

    # 雙重積分
    lhs_value = sp.integrate(integrand_LHS, (u, 0, 1), (v, 0, 1))
    print(f"4. [LHS] ∫_M dω 計算結果: {lhs_value}")

    # =========================================================
    # RHS: 計算 ∂M 上的 ω 積分 (Line Integral)
    # =========================================================
    # 邊界 ∂M 對應參數域 D 的四個邊界:
    # C1: (t, 0) t: 0->1 (下)
    # C2: (1, t) t: 0->1 (右)
    # C3: (t, 1) t: 1->0 (上, 注意方向!)
    # C4: (0, t) t: 1->0 (左, 注意方向!)
    
    t = sp.symbols('t')
    rhs_value = 0
    
    # 定義四段路徑的參數化 (u(t), v(t))
    paths = [
        {'u': t, 'v': 0, 'range': (0, 1), 'name': 'Bottom'},
        {'u': 1, 'v': t, 'range': (0, 1), 'name': 'Right'},
        {'u': t, 'v': 1, 'range': (1, 0), 'name': 'Top'},    # 反向
        {'u': 0, 'v': t, 'range': (1, 0), 'name': 'Left'}    # 反向
    ]

    print("5. [RHS] ∫_∂M ω 計算過程:")
    
    for path in paths:
        # 1. 取得路徑參數
        u_t = path['u']
        v_t = path['v']
        
        # 2. 將路徑代入曲面參數，得到空間曲線 (x(t), y(t), z(t))
        # 複合函數: t -> (u,v) -> (x,y,z)
        curr_x = map_x.subs({u: u_t, v: v_t})
        curr_y = map_y.subs({u: u_t, v: v_t})
        curr_z = map_z.subs({u: u_t, v: v_t})

        # 3. 計算 dx, dy, dz (關於 t)
        dx_dt = sp.diff(curr_x, t)
        dy_dt = sp.diff(curr_y, t)
        dz_dt = sp.diff(curr_z, t)

        # 4. 拉回 ω = P dx + Q dy + R dz
        # P, Q, R 本身也要代入 curr_x, curr_y, curr_z
        P_t = P.subs({x: curr_x, y: curr_y, z: curr_z})
        Q_t = Q.subs({x: curr_x, y: curr_y, z: curr_z})
        R_t = R.subs({x: curr_x, y: curr_y, z: curr_z})

        integrand_line = P_t * dx_dt + Q_t * dy_dt + R_t * dz_dt
        
        # 5. 定積分
        t_start, t_end = path['range']
        line_val = sp.integrate(integrand_line, (t, t_start, t_end))
        
        print(f"   - Path {path['name']}: {line_val}")
        rhs_value += line_val

    print(f"   [RHS] 總和: {rhs_value}\n")

    # =========================================================
    # 結論
    # =========================================================
    print("---------------------------------------------------------")
    print(f"驗證結果: {lhs_value} == {rhs_value} ? {lhs_value == rhs_value}")
    if lhs_value == rhs_value:
        print("🎉 廣義斯托克斯定理在此例中成立！")
    else:
        print("⚠️ 驗證失敗，請檢查計算邏輯。")

if __name__ == "__main__":
    verify_stokes_theorem()