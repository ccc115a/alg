import numpy as np
from scipy.linalg import eig

def verify_eigen_decomposition(matrix):
    """
    對給定的矩陣進行特徵值分解，並驗證分解後能否還原回原始矩陣。
    
    參數:
    matrix (numpy.ndarray): 待分解的方陣。
    """
    print(f"原始矩陣 A:\n{matrix}\n")

    # 1. 執行特徵值分解
    # eig 函式回傳特徵值 w 和特徵向量矩陣 v
    eigenvalues, eigenvectors = eig(matrix)

    # SciPy 的 eig 回傳的特徵向量是作為 v 的行向量。
    # 特徵值 w 是一個一維陣列。
    print(f"特徵值陣列 (Eigenvalues):\n{eigenvalues}\n")
    print(f"特徵向量矩陣 V (Eigenvector Matrix):\n{eigenvectors}\n")

    # 2. 建立特徵值對角矩陣 Lambda
    # np.diag(eigenvalues) 會將一維特徵值陣列轉換為對角矩陣
    Lambda = np.diag(eigenvalues)
    print(f"特徵值對角矩陣 Lambda:\n{Lambda}\n")

    # 3. 驗證 A = V * Lambda * V_inverse
    # 計算特徵向量矩陣的逆矩陣
    V_inverse = np.linalg.inv(eigenvectors)
    
    # 計算 V * Lambda * V_inverse
    reconstructed_matrix = eigenvectors @ Lambda @ V_inverse
    print(f"分解後還原的矩陣 V * Lambda * V_inverse:\n{reconstructed_matrix}\n")

    # 4. 檢查還原後的矩陣是否與原始矩陣近似
    # 使用 np.allclose 檢查兩個浮點數矩陣是否近似相等
    is_restored = np.allclose(matrix, reconstructed_matrix)
    print(f"還原後的矩陣是否與原始矩陣近似相等？ {is_restored}")
    
    return is_restored

# --- 範例 1：一個簡單的 2x2 對稱矩陣 ---
# 對稱矩陣的特徵分解會更穩定
symmetric_matrix = np.array([[2, 1],
                             [1, 2]])
verify_eigen_decomposition(symmetric_matrix)

print("\n" + "="*50 + "\n")

# --- 範例 2：一個非對稱矩陣 ---
# 非對稱矩陣的特徵值可能是複數
non_symmetric_matrix = np.array([[1, 2],
                                 [3, 4]])
verify_eigen_decomposition(non_symmetric_matrix)