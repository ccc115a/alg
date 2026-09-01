import numpy as np

def run_einsum_demo():
    print("=== 愛因斯坦求和約定 (Einstein Summation) 實作示範 ===\n")
    
    # 初始化資料
    # 設定隨機種子以確保結果可重現
    np.random.seed(42)
    
    # 向量 (維度 3)
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    
    # 矩陣 (3x3)
    A = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])
    
    B = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]]) # 單位矩陣
    
    print(f"向量 a: {a}")
    print(f"向量 b: {b}")
    print(f"矩陣 A:\n{A}")
    print("-" * 30)

    # ---------------------------------------------------------
    # 1. 向量內積 (Dot Product)
    # 數學公式: s = a_i * b_i (對 i 求和)
    # einsum 字串: 'i,i->' (輸入有兩個 index i，輸出是純量所以右邊為空)
    # ---------------------------------------------------------
    s_traditional = np.dot(a, b)
    s_einsum = np.einsum('i,i->', a, b)
    
    print(f"[1. 內積 a_i b^i]")
    print(f"  傳統 np.dot: {s_traditional}")
    print(f"  Einsum 'i,i->': {s_einsum}")
    assert s_traditional == s_einsum
    print("  -> 驗證成功\n")

    # ---------------------------------------------------------
    # 2. 矩陣乘法 (Matrix Multiplication)
    # 數學公式: C_ij = A_ik * B_kj (對 k 求和)
    # einsum 字串: 'ik,kj->ij' (保留 i, j，對 k 求和消失)
    # ---------------------------------------------------------
    C_traditional = np.matmul(A, B)
    C_einsum = np.einsum('ik,kj->ij', A, B)
    
    print(f"[2. 矩陣乘法 A_ik B^k_j]")
    print(f"  Einsum 'ik,kj->ij':\n{C_einsum}")
    # 驗證所有元素是否接近
    assert np.allclose(C_traditional, C_einsum)
    print("  -> 驗證成功\n")

    # ---------------------------------------------------------
    # 3. 矩陣的跡 (Trace)
    # 數學公式: tr = A_ii (對 i 求和)
    # einsum 字串: 'ii->' (輸入指標相同，代表對角線求和)
    # ---------------------------------------------------------
    tr_traditional = np.trace(A)
    tr_einsum = np.einsum('ii->', A)
    
    print(f"[3. 跡 A^i_i]")
    print(f"  傳統 np.trace: {tr_traditional}")
    print(f"  Einsum 'ii->': {tr_einsum}")
    assert tr_traditional == tr_einsum
    print("  -> 驗證成功\n")

    # ---------------------------------------------------------
    # 4. 矩陣轉置 (Transpose)
    # 數學公式: T_ji = A_ij (交換指標)
    # einsum 字串: 'ij->ji'
    # ---------------------------------------------------------
    T_traditional = np.transpose(A)
    T_einsum = np.einsum('ij->ji', A)
    
    print(f"[4. 轉置 A_ji]")
    print(f"  Einsum 'ij->ji':\n{T_einsum}")
    assert np.allclose(T_traditional, T_einsum)
    print("  -> 驗證成功\n")

    # ---------------------------------------------------------
    # 5. 外積 (Outer Product) - 製作張量
    # 數學公式: T_ij = a_i * b_j (沒有重複指標，不求和)
    # einsum 字串: 'i,j->ij'
    # ---------------------------------------------------------
    O_traditional = np.outer(a, b)
    O_einsum = np.einsum('i,j->ij', a, b)
    
    print(f"[5. 外積 a_i b_j]")
    print(f"  Einsum 'i,j->ij':\n{O_einsum}")
    assert np.allclose(O_traditional, O_einsum)
    print("  -> 驗證成功\n")
    
    # ---------------------------------------------------------
    # 6. 進階：黎曼曲率型縮並 (模擬)
    # 假設我們有一個 4階張量 R_ijkl 和度量張量 g^lm
    # 我們想算出里奇張量 Ricci_jk = g^il R_ijkl
    # ---------------------------------------------------------
    # 建立隨機 4維張量 (2x2x2x2) 僅作示範
    R = np.random.rand(2, 2, 2, 2)
    g_inv = np.eye(2) # 簡單起見用單位矩陣
    
    # 運算: g^{il} * R_{ijkl} -> Ricci_{jk}
    # 字串解析:
    #   g_inv: 'il'
    #   R: 'ijkl'
    #   輸出: 'jk' (因為 i, l 都重複了，會被求和掉)
    Ricci = np.einsum('il,ijkl->jk', g_inv, R)
    
    print(f"[6. 進階張量縮並 g^il R_ijkl -> R_jk]")
    print(f"  輸入張量 R 形狀: {R.shape}")
    print(f"  輸出張量 Ricci 形狀: {Ricci.shape}")
    print("  (成功將 4階張量縮減為 2階張量)")

if __name__ == "__main__":
    run_einsum_demo()