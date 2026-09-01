import sympy as sp
import numpy as np
from scipy import integrate
from typing import List, Tuple, Dict, Union
from itertools import combinations, permutations

# ==============================================================================
# 1. 基礎類別：微分形式 (Differential Form)
# ==============================================================================
class DifferentialForm:
    def __init__(self, dim: int, degree: int, data: Dict[Tuple[int, ...], sp.Expr]):
        self.dim = dim        # 空間維度 N
        self.degree = degree  # 形式階數 k (k-form)
        self.data = data      # 字典: {(0, 1): x0*x1} 代表 x0*x1 dx0^dx1

    def exterior_derivative(self):
        """計算外微分 dω (從 k-form 變 k+1 form)"""
        new_data = {}
        X = [sp.symbols(f'x{i}') for i in range(self.dim)]
        
        for indices, expr in self.data.items():
            # d(f dx_I) = sum( df/dx_j ^ dx_j ^ dx_I )
            for j in range(self.dim):
                # 計算偏導數
                diff_expr = sp.diff(expr, X[j])
                if diff_expr == 0: continue
                
                # 處理新的指標序列 (j, i1, i2...)
                raw_indices = (j,) + indices
                
                # 排序並計算正負號 (楔積的交換律)
                if len(set(raw_indices)) != len(raw_indices):
                    continue # 有重複指標則為 0
                
                # 計算排序所需的交換次數以決定正負號
                sorted_indices = tuple(sorted(raw_indices))
                
                # 計算逆序數 (Inversion count) 來決定符號
                # 簡單做法：模擬冒泡排序計算交換次數
                temp_list = list(raw_indices)
                swaps = 0
                for _ in range(len(temp_list)):
                    for k_idx in range(len(temp_list) - 1):
                        if temp_list[k_idx] > temp_list[k_idx + 1]:
                            temp_list[k_idx], temp_list[k_idx + 1] = temp_list[k_idx + 1], temp_list[k_idx]
                            swaps += 1
                
                sign = (-1) ** swaps
                
                # 累加結果
                if sorted_indices in new_data:
                    new_data[sorted_indices] += sign * diff_expr
                else:
                    new_data[sorted_indices] = sign * diff_expr
                    
        return DifferentialForm(self.dim, self.degree + 1, new_data)

# ==============================================================================
# 2. 核心積分引擎 (支援 nquad 與 通用 Jacobian)
# ==============================================================================
def integrate_form_on_manifold(
    omega: DifferentialForm,
    manifold_map: List[sp.Expr], # [x0(u), x1(u)...]
    bounds: List[Tuple[float, float]] # [(u1_min, u1_max), ...]
) -> float:
    """
    計算 ∫_M ω。
    使用通用的 Pullback 公式：∫ f(r(u)) * det(Jacobian_sub) du
    """
    k = omega.degree
    dim = omega.dim
    assert len(bounds) == k, f"積分維度 {len(bounds)} 與形式階數 {k} 不符"
    
    # 定義參數符號 u0, u1, ... uk-1
    U = [sp.symbols(f'u{i}') for i in range(k)]
    X = [sp.symbols(f'x{i}') for i in range(dim)]
    
    # 轉為 SymPy 物件
    manifold_map = [sp.sympify(m) for m in manifold_map]
    
    # 1. 計算 Jacobian 矩陣 (N x k)
    # J[i][j] = dx_i / du_j
    J = sp.Matrix([[sp.diff(m, U[j]) for j in range(k)] for m in manifold_map])
    
    # 2. 準備代換字典 x_i -> phi(u)
    subs_map = {X[i]: manifold_map[i] for i in range(dim)}
    
    # 3. 構建被積函數 (Integrand)
    # Pullback 公式: Sum ( coeff * det(J_rows) )
    total_integrand = 0
    
    for indices, expr in omega.data.items():
        # indices 是一個 tuple, 例如 (0, 2, 4) 代表 dx0^dx2^dx4
        # 我們需要 Jacobian 矩陣中對應 0, 2, 4 行 (row) 的 kxk 子矩陣
        
        # 提取子矩陣
        sub_matrix = J[list(indices), :]
        det_J = sub_matrix.det()
        
        # 拉回係數函數
        coeff_pulled = expr.subs(subs_map)
        
        total_integrand += coeff_pulled * det_J
        
    if total_integrand == 0:
        return 0.0

    # 4. 使用 nquad 進行數值積分
    func_np = sp.lambdify(U, total_integrand, 'numpy')
    
    # nquad 的範圍格式稍微不同，它需要 [[min, max], [min, max]...] 
    # 且順序通常是 u0, u1... (與 dblquad 相反，要注意)
    # SciPy nquad 參數順序 func(u0, u1, ...) 對應 bounds[0], bounds[1]
    
    ranges = [[b[0], b[1]] for b in bounds]
    
    # 處理 lambdify 輸出常數的問題
    def safe_func(*args):
        return func_np(*args)

    val, error = integrate.nquad(safe_func, ranges)
    return val

# ==============================================================================
# 3. 驗證函數 (遞迴處理邊界)
# ==============================================================================
def verify_stokes_general(name, dim, k, omega_data, M_map, bounds):
    """
    name: 案例名稱
    dim: 空間維度 N
    k: 流形維度 (積分維度)
    omega_data: 字典定義的 (k-1)-form
    M_map: 流形參數化列表
    bounds: 參數範圍
    """
    print(f"\n====== 驗證: {name} (N={dim}, k={k}) ======")
    
    # --- 修正：確保 M_map 中的所有元素都是 SymPy 物件 (例如將 int 1 轉為 Integer(1)) ---
    M_map = [sp.sympify(m) for m in M_map]
    # -------------------------------------------------------------------------------

    # 建構 (k-1)-form
    omega = DifferentialForm(dim, k-1, omega_data)
    
    # --- LHS: ∫_M dω ---
    d_omega = omega.exterior_derivative()
    lhs = integrate_form_on_manifold(d_omega, M_map, bounds)
    print(f"  LHS (∫_M dω) = {lhs:.6f}")

    # --- RHS: ∫_∂M ω ---
    rhs = 0.0
    U = [sp.symbols(f'u{i}') for i in range(k)] # 原本 M 的參數
    
    # 遍歷每個參數 u_i
    for i in range(k):
        u_min, u_max = bounds[i]
        
        # 定義新的參數集 V (長度 k-1) 用於邊界參數化
        V = [sp.symbols(f'u{j}') for j in range(k-1)] 
        
        # 1. 下界 Face (u_i = u_min)
        # Orientation: (-1)^(i+1)
        sub_map_min = {}
        v_idx = 0
        for j in range(k):
            if j == i: sub_map_min[U[j]] = u_min
            else: 
                sub_map_min[U[j]] = V[v_idx]
                v_idx += 1
        
        # 因為前面已經 sympify 過了，這裡的 m 肯定是 SymPy 物件，具有 .subs() 方法
        M_min = [m.subs(sub_map_min) for m in M_map]
        
        # 邊界的參數範圍 (移除了第 i 個)
        bounds_sub = bounds[:i] + bounds[i+1:]
        
        val_min = integrate_form_on_manifold(omega, M_min, bounds_sub)
        rhs += ((-1)**(i+1)) * val_min 
        
        # 2. 上界 Face (u_i = u_max)
        # Orientation: (-1)^i
        sub_map_max = {}
        v_idx = 0
        for j in range(k):
            if j == i: sub_map_max[U[j]] = u_max
            else: 
                sub_map_max[U[j]] = V[v_idx]
                v_idx += 1
                
        M_max = [m.subs(sub_map_max) for m in M_map]
        val_max = integrate_form_on_manifold(omega, M_max, bounds_sub)
        rhs += ((-1)**i) * val_max

    print(f"  RHS (∫_∂M ω) = {rhs:.6f}")
    
    if abs(lhs - rhs) < 1e-4:
        print("  ✅ 驗證成功")
    else:
        print(f"  ❌ 驗證失敗 (Diff: {abs(lhs-rhs):.2e})")

# ==============================================================================
# 4. 測試案例：4D Tesseract (超立方體)
# ==============================================================================
def run_4d_test():
    # 符號
    x0, x1, x2, x3, x4 = sp.symbols('x0 x1 x2 x3 x4')
    u0, u1, u2, u3 = sp.symbols('u0 u1 u2 u3')
    
    # -------------------------------------------------------------
    # 案例：驗證 4-Manifold in R^5
    # -------------------------------------------------------------
    # 我們定義一個 5D 空間中的 4D "平面" (Tesseract)
    # Param: x0=u0, x1=u1, x2=u2, x3=u3, x4=1
    # 範圍: 0~1
    M_map = [u0, u1, u2, u3, 1]
    bounds = [(0,1), (0,1), (0,1), (0,1)]
    
    # 定義一個 3-form ω
    # 譬如: ω = x0 * dx1^dx2^dx3 + x4 * dx0^dx1^dx2
    # 注意字典 key 必須是排序過的 tuple
    omega_data = {
        (1, 2, 3): x0,       # 係數為 x0
        (0, 1, 2): x4**2     # 係數為 x4^2
    }
    
    # 預期 LHS 計算:
    # dω:
    # 1. d(x0 dx1^dx2^dx3) = dx0^dx1^dx2^dx3 (係數 1)
    # 2. d(x4^2 dx0^dx1^dx2) = 2*x4 dx4^dx0^dx1^dx2 
    #    = 2*x4 * (-1)^3 dx0^dx1^dx2^dx4 (交換 3 次把 dx4 移到後面)
    #    = -2*x4 dx0^dx1^dx2^dx4
    #
    # 在 M 上:
    # x4 = 1 (常數) => dx4 = 0. 所以第二項 Pullback 後為 0.
    # 第一項 Pullback: x0=u0. Jacobian 是 Identity. 
    # ∫_M 1 * det(I) du0...du3 = Volume = 1.
    
    verify_stokes_general("4D Tesseract in R^5", dim=5, k=4, 
                          omega_data=omega_data, M_map=M_map, bounds=bounds)

    # -------------------------------------------------------------
    # 複雜案例：彎曲的 4-Manifold
    # -------------------------------------------------------------
    # M: x0=u0, x1=u1, x2=u2, x3=u3, x4 = u0^2 + u1^2
    M_map_curved = [u0, u1, u2, u3, u0**2 + u1**2]
    
    # 使用相同的 form
    verify_stokes_general("Curved 4-Manifold in R^5", dim=5, k=4, 
                          omega_data=omega_data, M_map=M_map_curved, bounds=bounds)

if __name__ == "__main__":
    run_4d_test()