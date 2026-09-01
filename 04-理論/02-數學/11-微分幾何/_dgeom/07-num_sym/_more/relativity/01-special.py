import numpy as np
from sympy import symbols, diff, Matrix

# 設置時空維度
D = 4
# 定義時空座標 (t, x, y, z)
# 雖然閔可夫斯基度量是常數，但我們仍然需要定義 SymPy 符號來進行一般化操作
coords = symbols('t x y z') 

## 函式定義：計算克里斯托費爾符號
def calculate_christoffel_symbols(g_uv_matrix, dimensions, coordinates):
    """
    根據給定的度量張量矩陣，計算所有克里斯托費爾符號 Gamma^lambda_mu_nu。

    輸入:
    g_uv_matrix: SymPy Matrix 形式的度量張量 g_{\mu\nu}。
    dimensions: 時空維度 D (例如: 4)。
    coordinates: SymPy 符號形式的座標 (t, x, y, z, ...)。

    輸出:
    christoffel_symbols: 包含所有 Gamma^lambda_mu_nu 的字典。
    """
    
    # 1. 計算逆度量張量 g^{\lambda\rho}
    g_contra = g_uv_matrix.inv()
    
    christoffel_symbols = {}
    
    # 遍歷所有可能的索引組合 (lambda, mu, nu)
    for lambda_idx in range(dimensions):
        for mu_idx in range(dimensions):
            for nu_idx in range(dimensions):
                
                # 每個 Gamma^lambda_mu_nu 的計算結果
                gamma_value = 0
                
                # 根據公式，對 rho 進行求和 (愛因斯坦求和約定)
                for rho_idx in range(dimensions):
                    
                    # 計算三個偏導數項:
                    # 1. \partial_{\mu} g_{\nu\rho}
                    partial_mu_g_nu_rho = diff(g_uv_matrix[nu_idx, rho_idx], coordinates[mu_idx])
                    
                    # 2. \partial_{\nu} g_{\mu\rho}
                    partial_nu_g_mu_rho = diff(g_uv_matrix[mu_idx, rho_idx], coordinates[nu_idx])
                    
                    # 3. -\partial_{\rho} g_{\mu\nu}
                    partial_rho_g_mu_nu = diff(g_uv_matrix[mu_idx, nu_idx], coordinates[rho_idx])
                    
                    # 公式中的中括號項: (\partial_{\mu} g_{\nu\rho} + \partial_{\nu} g_{\mu\rho} - \partial_{\rho} g_{\mu\nu})
                    bracket_term = partial_mu_g_nu_rho + partial_nu_g_mu_rho - partial_rho_g_mu_nu
                    
                    # 加上求和項 (1/2 * g^{\lambda\rho} * bracket_term)
                    sum_term = 0.5 * g_contra[lambda_idx, rho_idx] * bracket_term
                    gamma_value += sum_term
                
                # 將結果存入字典，使用 (lambda, mu, nu) 作為鍵
                # 確保結果被簡化
                christoffel_symbols[(lambda_idx, mu_idx, nu_idx)] = gamma_value.simplify()
                
    return christoffel_symbols

## 應用於狹義相對論 (閔可夫斯基度量)

# 閔可夫斯基度量 (使用 SymPy Matrix，(t, x, y, z) 約定為: (-, +, +, +))
# 注意: 雖然我們用 SymPy 矩陣來表示，但其元素是常數，不依賴於座標符號。
# 狹義相對論中，度量張量 $g_{\mu\nu} = \eta_{\mu\nu}$
eta_uv = Matrix([
    [-1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

print("--- 狹義相對論 (閔可夫斯基度量) 計算 ---")

# 執行計算
christoffel_results_SR = calculate_christoffel_symbols(eta_uv, D, coords)

# 輸出結果
non_zero_count = 0
for indices, value in christoffel_results_SR.items():
    if value != 0:
        # 顯示非零結果，並將其計數
        print(f"Gamma^{indices[0]}_{indices[1]}{indices[2]} = {value}")
        non_zero_count += 1

print("\n--- 總結 ---")
if non_zero_count == 0:
    print(f"計算了 {D**3} 個克里斯托費爾符號。所有結果均為零 (0)。")
    print("這證明了在狹義相對論的平坦時空中，沒有幾何引起的『加速度』（重力），因此克里斯托費爾符號為零。")
else:
    print(f"發現 {non_zero_count} 個非零的克里斯托費爾符號。")

# 輸出一個範例以供確認
example_indices = (0, 0, 0) # Gamma^0_00
print(f"\n範例: Gamma^{example_indices[0]}_{example_indices[1]}{example_indices[2]} 的值為: {christoffel_results_SR[example_indices]}")