import sympy as sp
import numpy as np
from scipy import integrate
from typing import List, Tuple, Callable

# ==============================================================================
# 核心計算引擎
# ==============================================================================

def verify_stokes_theorem(
    name: str,
    F_sym: List[sp.Expr],
    M_param: List[sp.Expr],
    uv_bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    boundaries: List[Tuple[List[sp.Expr], Tuple[float, float]]]
):
    """
    驗證斯托克斯定理：∫_M (∇×F)·dS = ∫_∂M F·dr
    """
    
    # --- 修正開始：確保所有的輸入分量都是 SymPy 物件 ---
    # 這會將 Python 的 int 0 轉換為 SymPy 的 Integer(0)，這樣它就有 .subs() 方法了
    F_sym = [sp.sympify(f) for f in F_sym]
    M_param = [sp.sympify(m) for m in M_param]
    # --- 修正結束 ---

    # 定義符號
    x, y, z = sp.symbols('x y z')
    u, v, t = sp.symbols('u v t')
    
    print(f"\n--- 驗證案例: {name} ---")
    print(f"向量場 F: {F_sym}")
    print(f"流形 M 參數化: {M_param}")

    # ---------------------------------------------------------
    # 1. 左式計算 (LHS): ∫_M dω  =>  Surface Integral of Curl
    # ---------------------------------------------------------
    # 計算旋度 Curl F = (Ry - Qz, Pz - Rx, Qx - Py)
    Fx, Fy, Fz = F_sym
    curl_F = [
        sp.diff(Fz, y) - sp.diff(Fy, z),
        sp.diff(Fx, z) - sp.diff(Fz, x),
        sp.diff(Fy, x) - sp.diff(Fx, y)
    ]
    
    # 計算切向量 dr/du 和 dr/dv
    rx, ry, rz = M_param
    dr_du = [sp.diff(rx, u), sp.diff(ry, u), sp.diff(rz, u)]
    dr_dv = [sp.diff(rx, v), sp.diff(ry, v), sp.diff(rz, v)]
    
    # 計算法向量 N = dr/du × dr/dv (決定方向)
    N = [
        dr_du[1]*dr_dv[2] - dr_du[2]*dr_dv[1],
        dr_du[2]*dr_dv[0] - dr_du[0]*dr_dv[2],
        dr_du[0]*dr_dv[1] - dr_du[1]*dr_dv[0]
    ]
    
    # 將 Curl F 中的 x,y,z 替換為參數 u,v
    subs_dict = {x: rx, y: ry, z: rz}
    curl_F_on_M = [c.subs(subs_dict) for c in curl_F]
    
    # 計算被積函數 integrand = (Curl F) dot N
    lhs_integrand_sym = sum(c * n for c, n in zip(curl_F_on_M, N))
    
    # 轉為 Python 函數以便數值積分
    # 注意：如果被積函數是常數 0，lambdify 有時會產生問題，這裡做個簡單判斷
    if lhs_integrand_sym == 0:
        lhs_value = 0.0
    else:
        lhs_func = sp.lambdify((u, v), lhs_integrand_sym, 'numpy')
        (u_min, u_max), (v_min, v_max) = uv_bounds
        # 使用 dblquad
        # SciPy dblquad 的參數順序是 func(y, x)，對應這裡的 func(v, u)
        lhs_value, _ = integrate.dblquad(
            lambda v_val, u_val: lhs_func(u_val, v_val),
            u_min, u_max,
            lambda _: v_min, lambda _: v_max
        )

    # ---------------------------------------------------------
    # 2. 右式計算 (RHS): ∫_∂M ω  =>  Line Integral over Boundary
    # ---------------------------------------------------------
    rhs_value = 0.0
    
    for i, (gamma, (t_start, t_end)) in enumerate(boundaries):
        # 確保 gamma 也是 SymPy 物件
        gamma = [sp.sympify(g) for g in gamma]

        # 計算 dgamma/dt
        dgamma_dt = [sp.diff(g, t) for g in gamma]
        
        # 將 F 中的 x,y,z 替換為邊界參數 t
        subs_dict_bound = {x: gamma[0], y: gamma[1], z: gamma[2]}
        
        # 這裡原本會報錯，現在 F_sym 已經被 sympify 過了，所以整數 0 變成了 Integer(0)
        F_on_boundary = [f.subs(subs_dict_bound) for f in F_sym]
        
        # 計算被積函數 integrand = F(gamma(t)) dot gamma'(t)
        rhs_integrand_sym = sum(f * dg for f, dg in zip(F_on_boundary, dgamma_dt))
        
        # 積分
        if rhs_integrand_sym == 0:
            val = 0.0
        else:
            rhs_func = sp.lambdify(t, rhs_integrand_sym, 'numpy')
            # 處理 lambdify 對常數函數可能返回純量而非 array 的情況
            def safe_rhs_func(t_val):
                res = rhs_func(t_val)
                return res
            
            val, _ = integrate.quad(safe_rhs_func, t_start, t_end)
            
        rhs_value += val

    # ---------------------------------------------------------
    # 3. 驗證結果
    # ---------------------------------------------------------
    print(f"LHS (Flux of Curl)   = {lhs_value:.8f}")
    print(f"RHS (Circulation)    = {rhs_value:.8f}")
    
    error = abs(lhs_value - rhs_value)
    # 放寬一點誤差容許值，因為浮點數運算
    if error < 1e-5:
        print(f"✅ 驗證成功 (誤差: {error:.2e})")
    else:
        print(f"❌ 驗證失敗 (誤差: {error:.2e})")

# ==============================================================================
# 定義 3 個範例
# ==============================================================================

def run_examples():
    x, y, z = sp.symbols('x y z')
    u, v, t = sp.symbols('u v t')

    # -------------------------------------------------------
    # 範例 1: 單位正方形上的格林定理 (Green's Theorem in 3D)
    # -------------------------------------------------------
    # M: z=0 的平面，0<=x<=1, 0<=y<=1
    # F = [-y, x, 0] (典型的旋轉場)
    # 預期結果: Curl F = (0, 0, 2), Area=1, Integral = 2
    
    F1 = [-y, x, 0]
    M1 = [u, v, 0] # x=u, y=v, z=0
    bounds1 = ((0, 1), (0, 1))
    
    # 邊界需逆時針 (右手定則，法向量朝 +z)
    # 1. (t, 0, 0) t: 0->1
    # 2. (1, t, 0) t: 0->1
    # 3. (1-t, 1, 0) t: 0->1 (向左)
    # 4. (0, 1-t, 0) t: 0->1 (向下)
    b1_list = [
        ([t, 0, 0], (0, 1)),
        ([1, t, 0], (0, 1)),
        ([1-t, 1, 0], (0, 1)),
        ([0, 1-t, 0], (0, 1))
    ]
    
    verify_stokes_theorem("1. 平面正方形 (Green's Theorem)", F1, M1, bounds1, b1_list)

    # -------------------------------------------------------
    # 範例 2: 拋物面 (Paraboloid)
    # -------------------------------------------------------
    # M: z = 1 - x^2 - y^2, z >= 0
    # 參數化: x=u*cos(v), y=u*sin(v), z=1-u^2
    # u (半徑): 0 -> 1, v (角度): 0 -> 2pi
    # F = [z, x, y]
    
    F2 = [z, x, y]
    M2 = [u * sp.cos(v), u * sp.sin(v), 1 - u**2]
    bounds2 = ((0, 1), (0, 2*sp.pi))
    
    # 邊界: z=0 的圓 (u=1). 需逆時針 (從上往下看)
    # gamma(t) = [cos(t), sin(t), 0], t: 0 -> 2pi
    b2_list = [
        ([sp.cos(t), sp.sin(t), 0], (0, 2*sp.pi))
    ]
    
    verify_stokes_theorem("2. 拋物面碗 (Paraboloid)", F2, M2, bounds2, b2_list)

    # -------------------------------------------------------
    # 範例 3: 圓柱側面 (Cylinder Surface)
    # -------------------------------------------------------
    # M: x^2 + y^2 = 1, 0 <= z <= 2 (不含上下底面)
    # 參數化: x=cos(u), y=sin(u), z=v
    # u (角度): 0 -> 2pi, v (高度): 0 -> 2
    # 法向量方向: 徑向向外
    # F = [y, -x, z^2]
    
    F3 = [y, -x, z**2]
    M3 = [sp.cos(u), sp.sin(u), v]
    bounds3 = ((0, 2*sp.pi), (0, 2))
    
    # 邊界由兩部分組成 (右手定則):
    # 1. 底部圓 (v=0): 順時針! (因為法向量向外，人在邊界走，區域要在左手邊)
    #    gamma_bottom = [cos(-t), sin(-t), 0]
    # 2. 頂部圓 (v=2): 逆時針!
    #    gamma_top = [cos(t), sin(t), 2]
    
    b3_list = [
        ([sp.cos(-t), sp.sin(-t), 0], (0, 2*sp.pi)), # 底部 (順時針)
        ([sp.cos(t), sp.sin(t), 2], (0, 2*sp.pi))    # 頂部 (逆時針)
    ]
    
    verify_stokes_theorem("3. 圓柱側面 (Cylindrical Shell)", F3, M3, bounds3, b3_list)

if __name__ == "__main__":
    run_examples()