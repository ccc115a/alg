import sympy as sp
import numpy as np
from scipy import integrate
from typing import List, Tuple, Any

# ==============================================================================
# 核心通用函數 1: 左式 LHS (計算 dω 並在 M 上積分)
# ==============================================================================

def compute_lhs_integral(
    dim: int,           # 嵌入空間維度 N
    manifold_dim: int,  # 流形維度 k
    omega_sym: Any,     # 微分形式 ω
    M_param: List[Any], # 流形參數化
    bounds: List[Tuple[float, float]] # 參數範圍
) -> float:
    """
    通用計算左式：∫_M dω
    """
    # 1. 初始化符號
    X = [sp.symbols(f'x{i}') for i in range(dim)]
    # 流形本身的參數化通常使用 u, v, w
    u, v, w = sp.symbols('u v w')
    p_vars = [u, v, w][:manifold_dim]
    
    # 強制轉為 SymPy 物件
    M_param = [sp.sympify(m) for m in M_param]
    omega_sym = sp.sympify(omega_sym) if manifold_dim == 1 else [sp.sympify(c) for c in omega_sym]
    
    # 準備 Pullback 替換字典
    subs_map = {X[i]: M_param[i] for i in range(dim)}

    integrand = 0
    
    # --- Case k=1: Line Integral (Gradient Theorem type) ---
    if manifold_dim == 1:
        f = omega_sym
        t_param = p_vars[0]
        grad_f = [sp.diff(f, x_i) for x_i in X]
        dr_dt = [sp.diff(m, t_param) for m in M_param]
        integrand = sum(g.subs(subs_map) * d for g, d in zip(grad_f, dr_dt))

    # --- Case k=2: Surface Integral (Stokes / Green / General 2-manifold) ---
    elif manifold_dim == 2:
        F = omega_sym
        u_p, v_p = p_vars
        dr_du = [sp.diff(m, u_p) for m in M_param]
        dr_dv = [sp.diff(m, v_p) for m in M_param]
        
        # 廣義斯托克斯：遍歷所有平面投影
        for i in range(dim):
            for j in range(i + 1, dim):
                # Exterior derivative component: (∂Fj/∂xi - ∂Fi/∂xj)
                curl_comp = sp.diff(F[j], X[i]) - sp.diff(F[i], X[j])
                # Jacobian determinant for this projection
                jacobian = dr_du[i] * dr_dv[j] - dr_dv[i] * dr_du[j]
                integrand += curl_comp.subs(subs_map) * jacobian

    # --- Case k=3: Volume Integral (Gauss Divergence type) ---
    elif manifold_dim == 3:
        F = omega_sym
        u_p, v_p, w_p = p_vars
        # Jacobian determinant (Volumetric)
        J_matrix = sp.Matrix([[sp.diff(m, p) for p in p_vars] for m in M_param])
        jac_det = J_matrix.det()
        # Divergence
        div_F = sum(sp.diff(F[i], X[i]) for i in range(dim))
        integrand = div_F.subs(subs_map) * jac_det

    else:
        raise NotImplementedError(f"尚不支援流形維度 k={manifold_dim}")

    # 數值積分
    if integrand == 0: return 0.0

    func_np = sp.lambdify(p_vars, integrand, 'numpy')
    
    if manifold_dim == 1:
        val, _ = integrate.quad(func_np, bounds[0][0], bounds[0][1])
    elif manifold_dim == 2:
        # dblquad order is (y, x) -> (v, u)
        (u1, u2), (v1, v2) = bounds
        val, _ = integrate.dblquad(lambda v_val, u_val: func_np(u_val, v_val), u1, u2, lambda _: v1, lambda _: v2)
    elif manifold_dim == 3:
        # tplquad order is (z, y, x) -> (w, v, u)
        (u1, u2), (v1, v2), (w1, w2) = bounds
        val, _ = integrate.tplquad(
            lambda w_v, v_v, u_v: func_np(u_v, v_v, w_v),
            u1, u2, lambda _: v1, lambda _: v2, lambda _1, _2: w1, lambda _1, _2: w2
        )
    
    return val

# ==============================================================================
# 核心通用函數 2: 右式 RHS (計算 ω 在 ∂M 上積分)
# ==============================================================================

def compute_rhs_integral(
    dim: int,
    manifold_dim: int,
    omega_sym: Any,
    boundaries: List[Any] 
) -> float:
    """
    通用計算右式：∫_∂M ω
    """
    X = [sp.symbols(f'x{i}') for i in range(dim)]
    
    # 【關鍵修正】：明確定義邊界積分所使用的符號，與測試案例中的符號保持一致
    s = sp.Symbol('s')
    t = sp.Symbol('t') 
    
    omega_sym = sp.sympify(omega_sym) if manifold_dim == 1 else [sp.sympify(c) for c in omega_sym]
    
    total_val = 0.0

    for item in boundaries:
        # --- Case k=2: Boundary is 1D curve (Line Integral F . dr) ---
        if manifold_dim == 2:
            gamma, (t_min, t_max) = item
            gamma = [sp.sympify(g) for g in gamma]
            
            # 這裡必須使用符號 't' 進行微分，因為 gamma 是關於 t 的函數
            dgamma = [sp.diff(g, t) for g in gamma]
            
            subs_b = {X[i]: gamma[i] for i in range(dim)}
            
            # F . dr
            integrand = sum(omega_sym[i].subs(subs_b) * dgamma[i] for i in range(dim))
            
            if integrand != 0:
                func_b = sp.lambdify(t, integrand, 'numpy')
                def safe_func(val): return func_b(val)
                val, _ = integrate.quad(safe_func, t_min, t_max)
                total_val += val

        # --- Case k=3: Boundary is 2D surface (Flux Integral F . n dS) ---
        elif manifold_dim == 3:
            surf, s_bounds, t_bounds = item
            surf = [sp.sympify(g) for g in surf]
            
            # 這裡使用 's' 和 't'
            ds_vec = [sp.diff(g, s) for g in surf]
            dt_vec = [sp.diff(g, t) for g in surf]
            
            # Normal vector (Cross Product, only valid for 3D flux)
            # 注意：對於 N>3 的一般化，這裡需要修改為楔積，但此處針對 Gauss 定理 (3D)
            Nx = ds_vec[1]*dt_vec[2] - ds_vec[2]*dt_vec[1]
            Ny = ds_vec[2]*dt_vec[0] - ds_vec[0]*dt_vec[2]
            Nz = ds_vec[0]*dt_vec[1] - ds_vec[1]*dt_vec[0]
            Normal = [Nx, Ny, Nz]
            
            subs_b = {X[i]: surf[i] for i in range(dim)}
            
            # Flux = F . Normal
            integrand = sum(omega_sym[i].subs(subs_b) * Normal[i] for i in range(dim))
            
            if integrand != 0:
                func_b = sp.lambdify((s, t), integrand, 'numpy')
                val, _ = integrate.dblquad(lambda t_v, s_v: func_b(s_v, t_v), 
                                           s_bounds[0], s_bounds[1], 
                                           lambda _: t_bounds[0], lambda _: t_bounds[1])
                total_val += val
                
    return total_val

# ==============================================================================
# 驗證流程封裝
# ==============================================================================

def verify_stokes(name, dim, manifold_dim, omega, M_param, bounds, boundaries):
    print(f"\n====== 驗證: {name} ======")
    print(f"  配置: 空間 {dim}D, 流形 {manifold_dim}D")
    
    # 1. 計算 LHS
    lhs = compute_lhs_integral(dim, manifold_dim, omega, M_param, bounds)
    
    # 2. 計算 RHS
    if manifold_dim == 1:
        # k=1 的 RHS 為 F(end) - F(start)
        X = [sp.symbols(f'x{i}') for i in range(dim)]
        t = sp.symbols('u') # M_param 定義時使用的符號
        t_start, t_end = boundaries
        
        M_param_sym = [sp.sympify(m) for m in M_param]
        omega_sym = sp.sympify(omega)
        
        pt_start = {X[i]: M_param_sym[i].subs(t, t_start) for i in range(dim)}
        pt_end   = {X[i]: M_param_sym[i].subs(t, t_end) for i in range(dim)}
        
        rhs = float(omega_sym.subs(pt_end) - omega_sym.subs(pt_start))
    else:
        rhs = compute_rhs_integral(dim, manifold_dim, omega, boundaries)
        
    # 3. 輸出比較
    print(f"  LHS (∫ dω) = {lhs:.8f}")
    print(f"  RHS (∫ ω)  = {rhs:.8f}")
    
    error = abs(lhs - rhs)
    if error < 1e-5:
        print(f"  ✅ 驗證成功 (誤差: {error:.2e})")
    else:
        print(f"  ❌ 驗證失敗 (誤差: {error:.2e})")

# ==============================================================================
# 測試案例集
# ==============================================================================

def run_all_examples():
    # 定義符號
    x0, x1, x2, x3, x4 = sp.symbols('x0 x1 x2 x3 x4')
    u, v, w = sp.symbols('u v w')
    s, t = sp.symbols('s t') # 這些符號必須與 compute_rhs_integral 內的定義一致

    # 1. 微積分基本定理 (3D)
    verify_stokes(
        name="1. 微積分基本定理 (k=1, N=3)",
        dim=3,
        manifold_dim=1,
        omega=x0*x1 + x2,
        M_param=[sp.cos(u), sp.sin(u), u],
        bounds=[(0, 2*np.pi)],
        boundaries=[0, 2*np.pi]
    )

    # 2. 格林定理 (2D)
    # 這裡的邊界參數使用 t，對應 compute_rhs_integral 內的 sp.Symbol('t')
    verify_stokes(
        name="2. 格林定理 (k=2, N=2)",
        dim=2,
        manifold_dim=2,
        omega=[x0*x1, -x0**2],
        M_param=[u, v],
        bounds=[(0, 1), (0, 1)],
        boundaries=[
            ([t, 0], (0, 1)),       
            ([1, t], (0, 1)),       
            ([1-t, 1], (0, 1)),     
            ([0, 1-t], (0, 1))      
        ]
    )

    # 3. 斯托克斯定理 (3D)
    verify_stokes(
        name="3. 斯托克斯定理 (k=2, N=3)",
        dim=3,
        manifold_dim=2,
        omega=[x2, x0, x1],
        M_param=[u*sp.cos(v), u*sp.sin(v), 1-u**2],
        bounds=[(0, 1), (0, 2*np.pi)],
        boundaries=[
            ([sp.cos(t), sp.sin(t), 0], (0, 2*np.pi))
        ]
    )

    # 4. 高斯散度定理 (3D)
    # 這裡使用 s, t 作為參數
    verify_stokes(
        name="4. 高斯散度定理 (k=3, N=3)",
        dim=3,
        manifold_dim=3,
        omega=[x0, x1, x2],
        M_param=[u, v, w],
        bounds=[(0, 1), (0, 1), (0, 1)],
        boundaries=[
            ([0, t, s], (0,1), (0,1)), 
            ([1, s, t], (0,1), (0,1)),
            ([s, 0, t], (0,1), (0,1)),
            ([t, 1, s], (0,1), (0,1)),
            ([t, s, 0], (0,1), (0,1)),
            ([s, t, 1], (0,1), (0,1))
        ]
    )

    # 5. 高維度測試 (5D)
    verify_stokes(
        name="5. 高維度測試 (k=2, N=5)",
        dim=5,
        manifold_dim=2,
        omega=[x1, -x0, x4, 0, x2],
        M_param=[u, v, u**2 + v**2, u - v, 1],
        bounds=[(0, 1), (0, 1)],
        boundaries=[
            ([t, 0, t**2, t, 1], (0, 1)),
            ([1, t, 1+t**2, 1-t, 1], (0, 1)),
            ([1-t, 1, (1-t)**2+1, (1-t)-1, 1], (0, 1)),
            ([0, 1-t, (1-t)**2, 0-(1-t), 1], (0, 1))
        ]
    )

if __name__ == "__main__":
    run_all_examples()