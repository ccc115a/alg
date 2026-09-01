import sympy as sp
from sympy.tensor.tensor import ChristoffelSymbols
from sympy.functions.elementary.trigonometric import sin, cos

def calculate_curvature_tensors(coords, metric):
    """
    計算給定度量張量的 Christoffel 符號、Riemann 張量、Ricci 張量和純量曲率。

    參數:
        coords (tuple): 座標符號 (e.g., (theta, phi))
        metric (Matrix): 黎曼度量 g_ij
    
    返回值:
        dict: 包含所有計算結果的字典。
    """
    
    print("--- 1. Christoffel 符號 (第二類) ---")
    
    # 計算 Christoffel 符號 (第二類 Gamma^k_ij)
    # Cs.tensor 得到的是 Gamma^k_ij
    Cs = ChristoffelSymbols.from_metric(metric, coords)
    christoffel_symbols = Cs.tensor
    
    # 僅顯示非零項
    non_zero_gamma = {}
    for k in range(len(coords)):
        for i in range(len(coords)):
            for j in range(len(coords)):
                val = sp.simplify(christoffel_symbols[k, i, j])
                if val != 0:
                    symbol_k = coords[k]
                    symbol_i = coords[i]
                    symbol_j = coords[j]
                    non_zero_gamma[f'Γ^({symbol_k})_{{{symbol_i}{symbol_j}}}'] = val
                    
    for key, value in non_zero_gamma.items():
        print(f"{key} = {value}")

    print("\n--- 2. 黎曼曲率張量 (上一下三) R^k_lij ---")
    
    # SymPy 提供了內建的 Riemann 張量計算
    R = Cs.riemann()
    
    # 由於 2D 流形只有一個獨立分量 R^theta_phi_theta_phi (R^1_212)
    # 我們將其值轉換為協變形式 R_klij = g_km R^m_lij
    R_cov = sp.simplify(R.lowerindex(0))
    
    # 計算唯一的獨立分量 (R_theta_phi_theta_phi)
    # 座標索引: theta=0, phi=1
    riemann_component = R_cov[0, 1, 0, 1]
    
    print(f"唯一獨立協變分量 R_theta_phi_theta_phi = {riemann_component}")
    
    print("\n--- 3. 里奇張量 (Ricci Tensor) R_ij ---")

    # SymPy 提供了內建的 Ricci 張量計算
    # R_ij = R^k_i k j
    Ric = Cs.ricci()
    
    print(f"Ricci Tensor R_ij:\n{sp.simplify(Ric)}")
    
    # 4. 純量曲率 (Scalar Curvature) R
    print("\n--- 4. 純量曲率 (Scalar Curvature) R ---")
    
    # 計算逆度量 g^ij
    g_inv = metric.inv()
    
    # 計算純量曲率 R = g^ij R_ij
    R_scalar = sp.simplify((g_inv * Ric).trace())

    print(f"Scalar Curvature R = {R_scalar}")

    # 驗證
    print(f"\n--- 驗證: 單位球面的純量曲率理論值為 2 ---")
    if R_scalar == 2:
        print("計算結果與理論值一致。")
    
    return {
        "ChristoffelSymbols": christoffel_symbols,
        "RiemannTensor": R,
        "RicciTensor": Ric,
        "ScalarCurvature": R_scalar
    }

# --- 2D 單位球面設定 (Unit 2-Sphere) ---

# 座標: theta (緯度/極角), phi (經度/方位角)
theta, phi = sp.symbols('theta phi')
coords = (theta, phi)

# 度量張量 g_ij
# g_theta_theta = 1, g_phi_phi = sin(theta)^2
metric = sp.Matrix([
    [1, 0],
    [0, sin(theta)**2]
])

print("計算 2D 單位球面 (極座標) 的曲率...")
results = calculate_curvature_tensors(coords, metric)