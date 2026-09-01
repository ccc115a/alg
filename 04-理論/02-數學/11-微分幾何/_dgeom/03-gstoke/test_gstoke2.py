import numpy as np
from dgeom import Form, TangentVector, d, integrate_form, HyperCube, ParametrizedDomain, ParametricPatch

# ==========================================
# 測試案例
# ==========================================

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

if __name__ == "__main__":
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