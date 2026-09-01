import sympy as sp
import numpy as np
from scipy import integrate
from typing import List, Tuple, Dict, Any
from itertools import permutations
from diff_form import DifferentialForm

# ==============================================================================
# 2. 通用積分引擎 (支援 k-維積分)
# ==============================================================================
def integrate_form_on_manifold(
    omega: DifferentialForm,
    manifold_map: List[sp.Expr], 
    bounds: List[Tuple[float, float]]
) -> float:
    """
    計算 ∫_M ω。使用 Pullback 與 Jacobian。
    """
    k = omega.degree
    dim = omega.dim
    
    # 確保參數化是 SymPy 物件
    manifold_map = [sp.sympify(m) for m in manifold_map]
    
    # 定義符號
    X = [sp.symbols(f'x{i}') for i in range(dim)]
    # 參數符號 u0, u1, ...
    U = [sp.symbols(f'u{i}') for i in range(k)]
    
    # 替換字典 x -> phi(u)
    subs_map = {X[i]: manifold_map[i] for i in range(dim)}
    
    # --- 特殊情況: k=0 (點積分 / 函數求值) ---
    if k == 0:
        # 0-form 只有一項: {(): expression}
        val = 0
        for _, expr in omega.data.items():
            val += float(expr.subs(subs_map))
        return val

    # --- 一般情況: k > 0 ---
    # 計算 Jacobian 矩陣 J[i][j] = dx_i / du_j
    J = sp.Matrix([[sp.diff(m, U[j]) for j in range(k)] for m in manifold_map])
    
    total_integrand = 0
    
    for indices, expr in omega.data.items():
        # indices 對應 dx_i ^ dx_j ...
        # 提取 Jacobian 對應的列 (rows) 構成子矩陣
        sub_matrix = J[list(indices), :]
        det_J = sub_matrix.det()
        
        # Pullback: f(phi(u))
        coeff_pulled = expr.subs(subs_map)
        
        total_integrand += coeff_pulled * det_J
        
    if total_integrand == 0: return 0.0

    # 使用 scipy.integrate.nquad
    # nquad 要求 bounds 順序對應 u0, u1...
    func_np = sp.lambdify(U, total_integrand, 'numpy')
    
    # 包裝函數處理常數返回
    def safe_func(*args):
        return func_np(*args)

    ranges = [[b[0], b[1]] for b in bounds]
    val, _ = integrate.nquad(safe_func, ranges)
    return val

# ==============================================================================
# 3. 驗證函數 (核心邏輯)
# ==============================================================================
def verify_stokes_general(name, dim, k, omega_data, M_map, bounds):
    """
    通用的斯托克斯定理驗證器
    dim: 嵌入空間維度 N
    k:   流形維度
    """
    print(f"\n====== 驗證: {name} (N={dim}, k={k}) ======")
    
    # 前置處理：確保輸入為 SymPy 類型 (修正之前的 int attribute error)
    M_map = [sp.sympify(m) for m in M_map]
    
    # 構建微分形式 (k-1 form)
    omega = DifferentialForm(dim, k-1, omega_data)
    
    # --- LHS: ∫_M dω ---
    d_omega = omega.exterior_derivative()
    lhs = integrate_form_on_manifold(d_omega, M_map, bounds)
    print(f"  LHS (∫_M dω) = {lhs:.6f}")

    # --- RHS: ∫_∂M ω ---
    # 遞迴計算邊界積分。邊界由 2k 個 (k-1) 維面組成。
    rhs = 0.0
    U = [sp.symbols(f'u{i}') for i in range(k)] # 原本 M 的參數
    
    # 遍歷每個參數維度 i
    for i in range(k):
        u_min, u_max = bounds[i]
        
        # 新的參數集 V (k-1 個)
        V = [sp.symbols(f'u{j}') for j in range(k-1)] 
        
        # 輔助函數：建立變數代換字典
        def make_subs(fixed_val):
            mapping = {}
            v_idx = 0
            for j in range(k):
                if j == i: mapping[U[j]] = fixed_val
                else: 
                    mapping[U[j]] = V[v_idx]
                    v_idx += 1
            return mapping

        # 1. 下界 Face (u_i = u_min)
        # 定向規則: (-1)^(i+1)  [或者是 - (-1)^i]
        M_min = [m.subs(make_subs(u_min)) for m in M_map]
        bounds_sub = bounds[:i] + bounds[i+1:]
        val_min = integrate_form_on_manifold(omega, M_min, bounds_sub)
        
        # 2. 上界 Face (u_i = u_max)
        # 定向規則: (-1)^i
        M_max = [m.subs(make_subs(u_max)) for m in M_map]
        val_max = integrate_form_on_manifold(omega, M_max, bounds_sub)
        
        # 累加
        rhs += ((-1)**(i+1)) * val_min + ((-1)**i) * val_max

    print(f"  RHS (∫_∂M ω) = {rhs:.6f}")
    
    # 驗證
    error = abs(lhs - rhs)
    if error < 1e-4:
        print(f"  ✅ 驗證成功 (誤差: {error:.2e})")
    else:
        print(f"  ❌ 驗證失敗 (誤差: {error:.2e})")

# ==============================================================================
# 4. 測試案例集
# ==============================================================================
def run_all_tests():
    # 符號定義
    x0, x1, x2, x3, x4 = sp.symbols('x0 x1 x2 x3 x4')
    u0, u1, u2, u3 = sp.symbols('u0 u1 u2 u3') # 通用參數 u0=u, u1=v, u2=w ...

    # --------------------------------------------------------------------
    # 1. 微積分基本定理 (k=1, N=3)
    # --------------------------------------------------------------------
    # ω = f (0-form). dω = grad f . dr
    # f = x0*x1 + x2
    verify_stokes_general(
        name="1. 微積分基本定理 (FTC)", 
        dim=3, k=1,
        omega_data={(): x0*x1 + x2}, # 0-form key 是空 tuple
        M_map=[sp.cos(u0), sp.sin(u0), u0],
        bounds=[(0, 2*np.pi)]
    )

    # --------------------------------------------------------------------
    # 2. 格林定理 (k=2, N=2)
    # --------------------------------------------------------------------
    # ω = P dx + Q dy. F=[xy, -x^2]
    # P=xy (dx0), Q=-x^2 (dx1)
    verify_stokes_general(
        name="2. 格林定理 (Green's Theorem)",
        dim=2, k=2,
        omega_data={(0,): x0*x1, (1,): -x0**2},
        M_map=[u0, u1],
        bounds=[(0, 1), (0, 1)]
    )

    # --------------------------------------------------------------------
    # 3. 斯托克斯定理 (k=2, N=3)
    # --------------------------------------------------------------------
    # ω = F . dr = z dx + x dy + y dz
    # F = [z, x, y] -> [x2, x0, x1]
    verify_stokes_general(
        name="3. 斯托克斯定理 (Stokes' Theorem)",
        dim=3, k=2,
        omega_data={(0,): x2, (1,): x0, (2,): x1},
        M_map=[u0*sp.cos(u1), u0*sp.sin(u1), 1-u0**2], # Paraboloid
        bounds=[(0, 1), (0, 2*np.pi)]
    )

    # --------------------------------------------------------------------
    # 4. 高斯散度定理 (k=3, N=3)
    # --------------------------------------------------------------------
    # ω 必須是 Flux 2-form: F . n dS
    # 對應形式: Fx dy^dz + Fy dz^dx + Fz dx^dy
    # F = [x, y, z] -> [x0, x1, x2]
    # Terms:
    # x0 * dx1^dx2 -> Key (1, 2)
    # x1 * dx2^dx0 = -x1 * dx0^dx2 -> Key (0, 2) Value -x1
    # x2 * dx0^dx1 -> Key (0, 1)
    verify_stokes_general(
        name="4. 高斯散度定理 (Divergence Theorem)",
        dim=3, k=3,
        omega_data={
            (1, 2): x0,
            (0, 2): -x1, # 注意符號變換
            (0, 1): x2
        },
        M_map=[u0, u1, u2], # Unit Cube
        bounds=[(0, 1), (0, 1), (0, 1)]
    )

    # --------------------------------------------------------------------
    # 5. 高維度測試 (k=2, N=5)
    # --------------------------------------------------------------------
    # F = [x1, -x0, x4, 0, x2]
    # ω = x1 dx0 - x0 dx1 + x4 dx2 + 0 dx3 + x2 dx4
    verify_stokes_general(
        name="5. 高維度 5D 測試",
        dim=5, k=2,
        omega_data={
            (0,): x1,
            (1,): -x0,
            (2,): x4,
            (4,): x2
        },
        M_map=[u0, u1, u0**2 + u1**2, u0 - u1, 1],
        bounds=[(0, 1), (0, 1)]
    )

    # --------------------------------------------------------------------
    # 6. 超立方體測試 (k=4, N=5)
    # --------------------------------------------------------------------
    # 4-Manifold in 5D space (Tesseract geometry)
    # ω is a 3-form. Example: x0 dx1^dx2^dx3 + x4^2 dx0^dx1^dx2
    verify_stokes_general(
        name="6. 超立方體 4D Tesseract",
        dim=5, k=4,
        omega_data={
            (1, 2, 3): x0,
            (0, 1, 2): x4**2
        },
        M_map=[u0, u1, u2, u3, 1],
        bounds=[(0, 1), (0, 1), (0, 1), (0, 1)]
    )

if __name__ == "__main__":
    run_all_tests()