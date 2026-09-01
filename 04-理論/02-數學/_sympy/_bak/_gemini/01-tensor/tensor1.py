from sympy import symbols, sin, cos, Matrix, Array, pprint
from sympy.tensor.tensor import TensorIndexType, tensor_indices, tensor_heads, TensorSymmetry

def main():
    print("=== 1. 環境設置 (Setup) ===")
    # 定義一個歐幾里得空間的指標類型 (Euclidean)
    # dummy_name='E' 用於自動生成的求和指標名稱
    Euclid = TensorIndexType('Euclid', dummy_name='E')
    
    # 定義指標 i, j, k, l
    i, j, k, l = tensor_indices('i j k l', Euclid)
    
    # 定義張量 A (一階, 向量), B (一階, 向量), T (二階, 矩陣)
    A, B = tensor_heads('A B', [Euclid])
    T = tensor_heads('T', [Euclid, Euclid])
    
    print(f"指標類型: {Euclid}")
    print(f"張量符號: A(i), B(j), T(i, j)\n")


    print("=== 2. 張量積 (Tensor Product / Outer Product) ===")
    # 張量積就是簡單的相乘，不會自動縮並，除非指標重複
    # 結果是一個二階張量 P_ij = A_i * B_j
    product_AB = A(i) * B(j)
    
    print("表達式 A(i) * B(j):")
    pprint(product_AB)
    print("\n")


    print("=== 3. 縮並 (Contraction) ===")
    # 這裡示範愛因斯坦求和約定 (Einstein Summation)
    # 透過度規 (Metric) 進行縮並。
    # Euclid 類型預設有度規 metric，可以自動處理升降指標。
    
    # 內積 (Inner Product): A_i * B^i (或者在歐式空間 A_i * B_i)
    # 這裡手動將 B 的指標設為 contravariant (上標, -i) 或 covariant (下標, i)
    # 註: sympy 中，-i 代表上標 (contra)，i 代表下標 (cov)，視 metric 定義而定
    
    contraction = A(i) * B(-i)
    print("內積 A(i) * B(-i) (自動產生 dummy index):")
    pprint(contraction)
    
    # 張量的跡 (Trace): T_k^k
    trace_T = T(k, -k)
    print("張量 T 的跡 T(k, -k):")
    pprint(trace_T)
    print("\n")


    print("=== 4. 張量代數與簡化 (Canonicalization) ===")
    # 示範 sympy 如何識別並合併同類項 (即使指標名稱不同，只要結構相同)
    
    expr1 = A(i) * B(-i)
    expr2 = A(j) * B(-j)
    
    print(f"表達式 1: {expr1}")
    print(f"表達式 2: {expr2}")
    
    # 相加
    total = expr1 + expr2
    print("直接相加 (未化簡):")
    pprint(total)
    
    # 使用 canon_bp() 進行正則化 (Canonicalization)，它會發現這兩項其實是一樣的
    print("化簡後 (canon_bp):")
    pprint(total.canon_bp())
    print("\n")


    print("=== 5. 座標軸轉換/分量代換 (Transformation via Component Substitution) ===")
    # sympy.tensor.tensor 是抽象的，若要進行具體的座標轉換計算，
    # 我們通常定義轉換矩陣，並使用 `replace_with_arrays` 將抽象符號替換為具體分量。
    
    # 假設我們在二維空間
    dim = 2
    
    # 定義具體的符號變數
    theta = symbols('theta')
    a1, a2 = symbols('a1 a2')
    
    # 定義具體向量 V (在原座標系)
    vec_V = [a1, a2] 
    
    # 定義旋轉矩陣 R (座標轉換矩陣)
    # R_ij: i 是新座標，j 是舊座標
    matrix_R = [
        [cos(theta), sin(theta)],
        [-sin(theta), cos(theta)]
    ]
    
    # 定義抽象張量關係: V' = R * V
    # V'_i = R_i^j * V_j
    # 定義新的張量頭
    V = tensor_heads('V', [Euclid])       # 原向量
    V_prime = tensor_heads('V\'', [Euclid]) # 新向量
    R = tensor_heads('R', [Euclid, Euclid]) # 旋轉矩陣
    
    # 抽象運算式
    transform_eq = R(i, -j) * V(j)
    
    print("抽象轉換公式 V'_i = R_i^j * V_j:")
    pprint(transform_eq)
    
    # 將抽象張量替換為具體陣列 (Array/Matrix) 進行計算
    # 注意：這裡需要建立一個字典來映射 抽象張量 -> 具體陣列
    replacements = {
        R(i, -j): Array(matrix_R), # 對應 R 的分量
        V(j): Array(vec_V)         # 對應 V 的分量
    }
    
    # 執行替換與計算
    result_array = transform_eq.replace_with_arrays(replacements, [i])
    
    print(f"\n代入具體分量並計算 (theta, a1, a2):")
    print("結果向量 V' (Array 形式):")
    pprint(result_array)
    
    print("\n以矩陣形式檢視結果:")
    pprint(Matrix(result_array))

if __name__ == "__main__":
    main()