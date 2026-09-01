# 數學原理解說 -- 
from dgeom.num import TangentVector, Form, d, HyperCube, integrate_form, ParametricPatch
import numpy as np

def test_dd_f_is_zero():
    print("=== 通用外微分 d 測試 ===\n")
    
    # 定義測試點
    p_test = [1.0, 2.0, 3.0] 
    print(f"測試點 p: {p_test}\n")

    # --- 案例 1: 0-form -> 1-form ---
    # f = x^2 y
    def f_func(p): return (p[0]**2) * p[1]
    
    form0 = Form(0, f_func)
    print(f"0-form f = x^2 y")
    print(f"f(p) = {f_func(p_test)}")

    # 計算 df
    form1 = d(form0) # 這是 1-form
    
    # 定義向量 v = (1, 3, 0)
    v = TangentVector(lambda p: [1, 3, 0], name="v")
    
    # df(v) 應該等於 v(f)
    res_df = form1(v)(p_test)
    res_vf = v(form0())(p_test) # form0() 回傳 f 本身
    
    print(f"向量 v = {v.at(p_test)}")
    print(f"df(v) = {res_df:.5f}")
    print(f"v(f)  = {res_vf:.5f}")
    print(f"驗證: {np.isclose(res_df, res_vf)}\n")

    # --- 案例 2: 1-form -> 2-form ---
    # 定義一個 1-form ω = y dx
    # 數學定義：ω(v) = v_x * y
    def omega_func(v):
        def field(p):
            v_val = v.at(p)
            return v_val[0] * p[1] # v_x * y
        return field
    
    omega = Form(1, omega_func)
    
    # 理論計算：
    # ω = y dx
    # dω = dy ∧ dx = - dx ∧ dy
    # 如果我們選 u=(1,0,0) (x方向), v=(0,1,0) (y方向)
    # dω(u, v) 應該是 -1
    
    u = TangentVector(lambda p: [1, 0, 0], name="∂x")
    v = TangentVector(lambda p: [0, 1, 0], name="∂y")
    
    d_omega = d(omega) # 這是 2-form
    
    val = d_omega(u, v)(p_test)
    print(f"1-form ω = y dx")
    print(f"計算 dω(∂x, ∂y) 數值: {val:.5f}")
    print(f"理論值應為 -1.0")
    print(f"驗證: {np.isclose(val, -1.0)}\n")

    # --- 案例 3: 驗證 d^2 = 0 (從 1-form 到 3-form) ---
    # 我們讓上面那個 ω 繼續被微分
    # dω 已經是 2-form 了
    # d(dω) 應該是 3-form，且值為 0
    
    d2_omega = d(d_omega) # 3-form
    
    # 隨便選三個向量
    w = TangentVector(lambda p: [0, 0, 1], name="∂z")
    
    # 這裡我們使用稍複雜的變動向量場來確保 Lie Bracket 項有被運算到
    v_complex = TangentVector(lambda p: [p[1], p[0], 0], name="V_mix")
    
    val_zero = d2_omega(u, v_complex, w)(p_test)
    print(f"驗證 d^2 = 0")
    print(f"計算 d(dω)(u, v_mix, w): {val_zero:.10f}")
    
    if abs(val_zero) < 1e-4:
        print("✅ 通用算子 d 運作正常，平方性質驗證成功。")
    else:
        print("❌ 驗證失敗。")

def test_stoke_theorem():
    def run_test(name, lhs_val, rhs_val):
        diff = abs(lhs_val - rhs_val)
        print(f"--- {name} ---")
        print(f"  LHS (邊界): {lhs_val:.6f}")
        print(f"  RHS (內部): {rhs_val:.6f}")
        print(f"  誤差: {diff:.8e}")
        if diff < 1e-4:
            print("  ✅ 驗證成功")
        else:
            print("  ❌ 驗證失敗")
        print()

    print("==========================================================")
    print("廣義史托克定理全面驗證：∫_Ω dω = ∫_∂Ω ω")
    print("涵蓋：微積分基本定理、格林定理、史托克旋度定理、高斯散度定理")
    print("==========================================================\n")

    # --------------------------------------------------------
    # 案例 1: 微積分基本定理 (Fundamental Theorem of Calculus)
    # 1D 空間: ∫_a^b f'(x) dx = f(b) - f(a)
    # --------------------------------------------------------
    # Ω = [1, 3] (線段)
    # ω = f(x) (0-form)
    # dω = f'(x) dx (1-form)
    
    # 定義函數 f(x) = x^3
    def f_func(p): return p[0]**3
    omega_0 = Form(0, f_func)
    
    # 定義區域 [1, 3]
    line_segment = HyperCube([(1, 3)])
    
    # 計算 RHS (內部積分 ∫ dω)
    d_omega_0 = d(omega_0)
    rhs_ftc = integrate_form(d_omega_0, line_segment)
    
    # 計算 LHS (邊界積分 f(b) - f(a))
    # 注意：HyperCube 的 get_boundaries 會回傳兩個點 (0維區域)
    # 雖然 integrate_form 設計上通常對 >0 維積分，但這裡我們手動算一下邊界值比較直觀
    # 或是透過 dgeom 的架構，0維積分就是「函數求值」
    
    lhs_ftc = 0.0
    for boundary_point, sign in line_segment.get_boundaries():
        # boundary_point 是一個 0維 Domain，它的 map_func 會回傳該點座標
        p_val = boundary_point.map_func([]) 
        val = omega_0()(p_val) # 直接呼叫 0-form
        lhs_ftc += val * sign

    run_test("1. 微積分基本定理 (1D)", lhs_ftc, rhs_ftc)


    # --------------------------------------------------------
    # 案例 2: 格林定理 (Green's Theorem)
    # 2D 平面: ∮ (L dx + M dy) = ∬ (∂M/∂x - ∂L/∂y) dA
    # --------------------------------------------------------
    # Ω = [0, 1] x [0, 1] (正方形)
    # ω = (x^2 - y) dx + (x*y) dy
    
    # 定義 1-form
    def green_form_func(v):
        def field(p):
            x, y = p
            vx, vy = v.at(p)
            return (x**2 - y) * vx + (x * y) * vy
        return field
    omega_green = Form(1, green_form_func)
    
    # 定義區域
    square = HyperCube([(0, 1), (0, 1)])
    
    # RHS: 區域積分 dω
    rhs_green = integrate_form(d(omega_green), square)
    
    # LHS: 邊界積分 ω
    lhs_green = 0.0
    for boundary_line, sign in square.get_boundaries():
        lhs_green += integrate_form(omega_green, boundary_line) * sign
        
    run_test("2. 格林定理 (2D Flat)", lhs_green, rhs_green)


    # --------------------------------------------------------
    # 案例 3: 古典史托克定理 (Classical Stokes' Theorem)
    # 3D 彎曲曲面: ∮_C F·dr = ∬_S (∇xF)·da
    # --------------------------------------------------------
    # Ω: 拋物面 z = x^2 + y^2 的一部分
    # 參數化: u, v ∈ [0, 1], 映射 p(u,v) = [u, v, u^2 + v^2]
    # ω = z dx + x dy + y dz (對應向量場 F = (z, x, y))
    
    def surface_map(uv):
        u, v = uv
        return np.array([u, v, u**2 + v**2])
    
    # 建立「彎曲」的 2D 區域
    paraboloid_patch = ParametricPatch([(0, 1), (0, 1)], surface_map)
    
    # 定義 3D 中的 1-form
    def stokes_form_func(vec):
        def field(p):
            x, y, z = p
            vx, vy, vz = vec.at(p)
            # F = (z, x, y) dot V
            return z*vx + x*vy + y*vz
        return field
    omega_stokes = Form(1, stokes_form_func)
    
    # RHS: 在曲面上積分 dω (Curl)
    rhs_stokes = integrate_form(d(omega_stokes), paraboloid_patch)
    
    # LHS: 在曲面邊界(曲線)上積分 ω (Circulation)
    lhs_stokes = 0.0
    # get_boundaries 會自動處理參數空間的邊界，並透過 map_func 映射到 3D 曲線
    for boundary_curve, sign in paraboloid_patch.get_boundaries():
        lhs_stokes += integrate_form(omega_stokes, boundary_curve) * sign
        
    run_test("3. 史托克旋度定理 (3D Curved Surface)", lhs_stokes, rhs_stokes)


    # --------------------------------------------------------
    # 案例 4: 高斯散度定理 (Gauss's Divergence Theorem)
    # 3D 體積: ∯ (F·n) dS = ∭ (∇·F) dV
    # --------------------------------------------------------
    # Ω = [0, 1]^3 (立方體)
    # ω = x dy∧dz + y dz∧dx + z dx∧dy (通量形式，對應 F=(x,y,z))
    # dω = (1+1+1) dx∧dy∧dz = 3 dV
    
    # 定義 2-form (Flux form)
    def gauss_form_func(u, v):
        def field(p):
            x, y, z = p
            u_vec, v_vec = u.at(p), v.at(p)
            
            # dy^dz (u, v) = uy*vz - uz*vy
            dydz = u_vec[1]*v_vec[2] - u_vec[2]*v_vec[1]
            # dz^dx (u, v) = uz*vx - ux*vz
            dzdx = u_vec[2]*v_vec[0] - u_vec[0]*v_vec[2]
            # dx^dy (u, v) = ux*vy - uy*vx
            dxdy = u_vec[0]*v_vec[1] - u_vec[1]*v_vec[0]
            
            return x*dydz + y*dzdx + z*dxdy
        return field
        
    omega_gauss = Form(2, gauss_form_func)
    
    # 定義區域
    cube = HyperCube([(0, 1), (0, 1), (0, 1)])
    
    # RHS: 體積積分 dω
    rhs_gauss = integrate_form(d(omega_gauss), cube)
    
    # LHS: 表面積分 ω
    lhs_gauss = 0.0
    for boundary_surface, sign in cube.get_boundaries():
        lhs_gauss += integrate_form(omega_gauss, boundary_surface) * sign
        
    run_test("4. 高斯散度定理 (3D Volume)", lhs_gauss, rhs_gauss)

if __name__ == "__main__":
    # 執行 d^2 = 0 測試
    test_dd_f_is_zero()
    # 執行 Stokes 定理測試
    test_stoke_theorem()
