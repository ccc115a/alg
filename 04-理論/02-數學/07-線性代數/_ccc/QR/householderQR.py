import numpy as np
import numpy.linalg as la

def householder_qr(A):
    """
    使用 Householder Reflection 進行矩陣 A 的 QR 分解 (A = Q @ R)。

    Args:
        A (numpy.ndarray): 待分解的 m x n 矩陣。

    Returns:
        tuple: 包含正交矩陣 Q 和上三角矩陣 R 的元組 (Q, R)。
    """
    # 複製矩陣以避免修改原始輸入
    A_copy = A.copy()
    m, n = A_copy.shape

    # 初始化 Q 為單位矩陣 (m x m)，用於累積所有的 Householder 變換
    Q = np.identity(m)

    # 迭代列數 (只需要處理 n-1 次，因為 R 是 m x n 的)
    for k in range(min(m, n)):
        # 提取當前需要處理的子向量 x（第 k 列，從第 k 行開始）
        # x 是一個 (m-k) x 1 的向量
        x = A_copy[k:, k]

        # 1. 計算 Householder 向量 v
        
        # 歐幾里得範數 (2-範數)
        norm_x = la.norm(x)
        
        # Householder 變換將 x 轉換為 alpha * e_1
        
        # 確定 alpha 的符號：取與 x[0] 相反的符號，以避免數值相消
        # 如果 norm_x 為零（已是零向量），則變換無效，直接跳過
        if norm_x == 0:
            continue
            
        alpha = -np.sign(x[0]) * norm_x

        # 標準基向量 e_1 (長度為 len(x))
        e_1 = np.zeros_like(x)
        e_1[0] = 1.0
        
        # Householder 向量 v = x - alpha * e_1
        v = x - alpha * e_1
        
        # 確保 v 不是零向量，否則 H 是單位矩陣 (此處已由 norm_x 判斷涵蓋)
        norm_v_sq = v @ v  # v 點積 v (v^T v)

        # 2. 構造 Householder 矩陣 H_k (初等反射矩陣)
        # H = I - 2 * (v @ v.T) / (v.T @ v)
        # 這裡我們只構造 H' (m-k) x (m-k) 矩陣
        
        # 外積 v @ v.T
        vv_T = np.outer(v, v)
        
        # H' 矩陣 (尺寸: (m-k) x (m-k))
        H_prime = np.identity(m - k) - 2 * vv_T / norm_v_sq
        
        # 3. 將 H' 擴展為 m x m 的 H
        # H_k = [ I  | 0 ]
        #       [ 0  | H' ]
        H_k = np.identity(m)
        H_k[k:, k:] = H_prime
        
        # 4. 應用變換
        # 應用到 A: R = H_k @ R_prev
        A_copy = H_k @ A_copy
        
        # 應用到 Q: Q = Q_prev @ H_k (累積正交變換)
        Q = Q @ H_k
        
    # 最終 A_copy 就是上三角矩陣 R
    R = A_copy
    
    # 由於浮點運算，R 矩陣對角線以下可能會有極小的非零值，
    # 為了展示效果，將這些極小值設為零
    R[np.abs(R) < 1e-12] = 0
    
    return Q, R

# --- 測試案例 ---

# 測試矩陣 A (與您範例中的矩陣類似)
A = np.array([
    [12.0, -51.0, 4.0],
    [6.0, 167.0, -68.0],
    [-4.0, 24.0, -41.0]
])

print("--- Householder QR 分解 ---")
print("原始矩陣 A:\n", A)

Q, R = householder_qr(A)

print("\n正交矩陣 Q:\n", Q)
print("\n上三角矩陣 R:\n", R)

# --- 驗證 ---
A_reconstructed = Q @ R
print("\n驗證 Q @ R 重建的 A:\n", A_reconstructed)

# 檢查誤差 (應接近零)
error = la.norm(A - A_reconstructed)
print(f"\n重建誤差 ||A - Q@R||: {error:.2e}")

# 檢查 Q 的正交性 (Q^T @ Q 應接近單位矩陣 I)
I_check = Q.T @ Q
print("\n正交性檢查 (Q^T @ Q):\n", I_check)

# 檢查正交性誤差 (應接近零)
ortho_error = la.norm(I_check - np.identity(A.shape[0]))
print(f"\n正交性誤差 ||Q^T@Q - I||: {ortho_error:.2e}")