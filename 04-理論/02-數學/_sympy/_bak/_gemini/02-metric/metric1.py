from sympy import symbols, diag, Array, pprint
from sympy.tensor.tensor import TensorIndexType, tensor_indices, tensor_heads

def main():
    print("=== 1. 自動生成的度規張量 (Abstract Metric) ===")
    # 創建一個空間，這裡我們命名度規符號為 'g' (預設通常是 metric)
    # metric_symmetry=1 代表對稱張量 (g_ij = g_ji)
    Riemann = TensorIndexType('Riemann', metric_name='g', metric_symmetry=1, dummy_name='R')
    
    # 取得度規張量物件
    g = Riemann.metric
    
    print(f"度規物件: {g}")
    
    i, j, k = tensor_indices('i j k', Riemann)
    A = tensor_heads('A', [Riemann])

    # 顯示度規張量的形式 g(i, j)
    print("度規張量形式 g(i, j):")
    pprint(g(i, j))
    print()


    print("=== 2. 使用度規進行指標升降 (Index Manipulation) ===")
    # 抽象代數中，度規的作用是收縮指標來改變其變性 (Covariant <-> Contravariant)
    
    # 原始向量 A^i (上標)
    expr_up = A(-i) 
    print("原始向量 A(-i) (上標):")
    pprint(expr_up)
    
    # 手動用度規降指標: A_j = g_{ji} * A^i
    # g(j, i) * A(-i) -> 自動縮並 i
    expr_lowered = g(j, i) * A(-i)
    
    print("利用度規降指標 g(j, i) * A(-i):")
    pprint(expr_lowered)
    
    # SymPy 的 canon_bp() 會自動識別這就是 A(j) (下標)
    print("化簡後 (SymPy 自動識別為 A 的下標形式):")
    pprint(expr_lowered.canon_bp())
    print()


    print("=== 3. 定義具體度規矩陣 (Minkowski Metric - Special Relativity) ===")
    # 這裡示範狹義相對論中的 Minkowski 空間
    # 簽名 (Metric Signature) 為 (+, -, -, -)
    
    Lorentz = TensorIndexType('Lorentz', metric_name='eta', dummy_name='L')
    mu, nu = tensor_indices('mu nu', Lorentz)
    
    # 定義 4-向量 P (動量)
    P = tensor_heads('P', [Lorentz])
    
    # 定義具體的度規矩陣 eta (Minkowski metric)
    # diag(1, -1, -1, -1) 代表時間分量為正，空間分量為負
    minkowski_matrix = diag(1, -1, -1, -1)
    
    # 定義具體的動量向量 P = (E, px, py, pz)
    E, px, py, pz = symbols('E px py pz')
    p_vec = [E, px, py, pz]
    
    # 建立抽象公式：P^2 = P_mu * P^mu (不變質量平方)
    # 注意：這裡的 P(mu) * P(-mu) 其實隱含了 metric 的作用
    # 展開來看就是 P^mu * eta_{mu, nu} * P^nu
    invariant_mass_sq = P(mu) * P(-mu)
    
    print("抽象公式 P^2 (P_mu * P^mu):")
    pprint(invariant_mass_sq)
    
    # 設定替換規則
    # 1. 將 Lorentz 空間的度規 (Lorentz.metric) 替換為 minkowski_matrix
    # 2. 將向量 P 替換為 p_vec
    replacements = {
        Lorentz.metric: Array(minkowski_matrix),
        P(-mu): Array(p_vec), # 定義 P 的上標分量 (Contravariant components)
        P(mu): Array(p_vec)   # 通常只需要定義其中一種，但在 replace_with_arrays 有時需明確指定 metric 關聯
    }
    
    # 計算具體數值
    # 注意：replace_with_arrays 會自動利用提供的 metric 處理 P_mu 和 P^mu 之間的轉換
    # 但更直接的方法是告訴它 metric 是什麼
    
    # 正確做法：將表達式中的隱含 metric 顯式化，或者直接替換
    # 為了讓 SymPy 正確計算內積，我們需要提供 metric 給 replace_with_arrays
    # 或者是直接手寫 P^mu * eta_mu_nu * P^nu 來確保萬無一失
    
    explicit_expr = P(-mu) * Lorentz.metric(mu, nu) * P(-nu)
    
    result = explicit_expr.replace_with_arrays(
        {
            P(-mu): Array(p_vec),            # P^mu
            P(-nu): Array(p_vec),            # P^nu
            Lorentz.metric(mu, nu): Array(minkowski_matrix) # eta_mu_nu
        }
    )
    
    print("\n代入 Minkowski 度規與分量計算:")
    print(f"Metric: diag(1, -1, -1, -1)")
    print(f"Vector: [E, px, py, pz]")
    print("結果 (E^2 - px^2 - py^2 - pz^2):")
    pprint(result)

if __name__ == "__main__":
    main()