import numpy as np

def verify_svd_decomposition(matrix):
    """
    對給定的矩陣進行奇異值分解，並驗證分解後能否還原回原始矩陣。
    
    參數:
    matrix (numpy.ndarray): 待分解的矩陣。
    """
    print(f"原始矩陣 A:\n{matrix}\n")

    # 1. 執行奇異值分解
    # np.linalg.svd 回傳 U, 奇異值 s, 和 V^T
    U, s, VT = np.linalg.svd(matrix)

    print(f"奇異值 U 矩陣:\n{U}\n")
    print(f"奇異值陣列 s:\n{s}\n")
    print(f"奇異值 VT 矩陣:\n{VT}\n")

    # 2. 根據奇異值陣列 s 建立對角矩陣 Sigma
    # np.zeros 建立一個正確大小的零矩陣
    # 矩陣大小為 (rows of A, columns of A)
    Sigma = np.zeros(matrix.shape)
    
    # 使用 np.diag 將一維奇異值陣列 s 填入 Sigma 的對角線
    Sigma[:matrix.shape[1], :matrix.shape[1]] = np.diag(s)
    
    # 3. 驗證 A = U * Sigma * VT
    # 使用 @ 運算子進行矩陣乘法
    reconstructed_matrix = U @ Sigma @ VT
    print(f"分解後還原的矩陣 U * Sigma * VT:\n{reconstructed_matrix}\n")

    # 4. 檢查還原後的矩陣是否與原始矩陣近似
    # 使用 np.allclose 檢查兩個浮點數矩陣是否近似相等
    is_restored = np.allclose(matrix, reconstructed_matrix)
    print(f"還原後的矩陣是否與原始矩陣近似相等？ {is_restored}")
    
    return is_restored

# --- 範例 1：一個 3x2 的長方形矩陣 ---
# SVD 適用於任何矩陣，這是它與特徵值分解的主要區別
rectangular_matrix = np.array([[1, 2],
                               [3, 4],
                               [5, 6]])
verify_svd_decomposition(rectangular_matrix)

print("\n" + "="*50 + "\n")

# --- 範例 2：一個 2x2 的方陣 ---
square_matrix = np.array([[1, 2],
                          [3, 4]])
verify_svd_decomposition(square_matrix)