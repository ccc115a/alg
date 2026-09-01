import sympy as sp
from sympy.tensor.tensor import ChristoffelSymbols
from sympy.functions.elementary.trigonometric import sin

def calculate_curvature_tensors(coords, metric):
    """
    計算給定度量張量的 Christoffel 符號、Riemann 張量、Ricci 張量、純量曲率，
    並驗證它是否為真空愛因斯坦場方程的解。

    參數:
        coords (tuple): 座標符號 (e.g., (t, r, theta, phi))
        metric (Matrix): 黎曼度量 g_ij
    
    返回值:
        dict: 包含所有計算結果的字典。
    """
    
    dim = len(coords)
    print(f"--- 開始計算 {dim} 維流形 (時空) 的曲率 ---")
    
    # 1. Christoffel 符號 (第二類 Gamma^k_ij)
    print("\n--- 1. Christoffel 符號 (第二類) --- (只顯示部分，因矩陣過大)")
    Cs = ChristoffelSymbols.from_metric(metric, coords)
    christoffel_symbols = Cs.tensor
    
    # 2. 黎曼曲率張量 (上一下三) R^k_lij
    # R = Cs.riemann() # 由於矩陣過大，在此跳過 Riemann 張量的完整計算

    # 3. 里奇張量 (Ricci Tensor) R_ij
    print("\n--- 2. 里奇張量 (Ricci Tensor) R_ij ---")

    # SymPy 提供了內建的 Ricci 張量計算
    Ric = Cs.ricci()
    
    # 簡化 Ricci 張量，檢查是否為零
    Ric_simplified = sp.simplify(Ric)
    print(f"簡化後的 Ricci Tensor R_ij:\n{Ric_simplified}")

    # 4. 純量曲率 (Scalar Curvature) R
    print("\n--- 3. 純量曲率 (Scalar Curvature) R ---")
    
    # 計算逆度量 g^ij
    g_inv = metric.inv()
    
    # 計算純量曲率 R = g^ij R_ij
    R_scalar = sp.simplify((g_inv * Ric).trace())

    print(f"Scalar Curvature R = {R_scalar}")
    
    # 5. 驗證真空愛因斯坦場方程 (EFE)
    print("\n--- 4. 驗證真空愛因斯坦場方程 (R_ij = 0) ---")
    
    is_vacuum_solution = Ric_simplified.is_zero
    
    if is_vacuum_solution:
        print("驗證結果：R_ij = 0。")
        print("該度量是**真空愛因斯坦場方程** (R_ij = 0) 的一個解。")
    else:
        print("驗證結果：R_ij != 0。")
        print("該度量不是真空愛因斯坦場方程的解，或包含物質 (T_ij != 0)。")
        
    return {
        "RicciTensor": Ric_simplified,
        "ScalarCurvature": R_scalar,
        "IsVacuumEFE_Solution": is_vacuum_solution
    }

# --- 史瓦西度量設定 (Schwarzschild Metric, 4D Vacuum Solution) ---

# 符號定義
t, r, theta, phi, M = sp.symbols('t r theta phi M')
coords = (t, r, theta, phi)

# 史瓦西半徑函數 f(r) = 1 - 2M/r
fr = 1 - 2*M/r

# 史瓦西度量 g_ij (對角線矩陣)
# g_tt = -f(r), g_rr = 1/f(r), g_theta_theta = r^2, g_phi_phi = r^2 sin^2(theta)
metric = sp.Matrix([
    [-fr, 0, 0, 0],
    [0, 1/fr, 0, 0],
    [0, 0, r**2, 0],
    [0, 0, 0, r**2 * sin(theta)**2]
])

print("計算史瓦西時空 (4D) 的曲率並驗證 EFE...")
results = calculate_curvature_tensors(coords, metric)