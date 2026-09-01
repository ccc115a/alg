import numpy as np
from scipy.linalg import lu

def determinant_by_lu(matrix):
    """
    使用LU分解計算矩陣的行列式
    
    參數:
    matrix: numpy array, 方形矩陣
    
    返回:
    float: 行列式的值
    """
    # 確保輸入是numpy數組
    A = np.array(matrix, dtype=float)
    
    # 檢查是否為方形矩陣
    if A.shape[0] != A.shape[1]:
        raise ValueError("矩陣必須是方形矩陣")
    
    # 進行LU分解 (帶部分樞軸)
    # P @ A = L @ U，其中P是置換矩陣
    P, L, U = lu(A)
    
    # 計算置換矩陣P的行列式
    # 置換矩陣的行列式是 ±1
    det_P = np.linalg.det(P)
    
    # L是下三角矩陣，對角線元素都是1，所以det(L) = 1
    # U是上三角矩陣，行列式等於對角線元素的乘積
    det_U = np.prod(np.diag(U))
    
    # det(A) = det(P) * det(L) * det(U) = det(P) * 1 * det(U)
    det_A = det_P * det_U
    
    return det_A

def determinant_by_lu_manual(matrix):
    """
    手動實現LU分解計算行列式（不使用scipy）
    使用Doolittle算法進行LU分解
    """
    A = np.array(matrix, dtype=float)
    n = A.shape[0]
    
    if A.shape[0] != A.shape[1]:
        raise ValueError("矩陣必須是方形矩陣")
    
    # 初始化L和U矩陣
    L = np.zeros((n, n))
    U = np.zeros((n, n))
    
    # 記錄行交換次數（用於計算符號）
    row_swaps = 0
    
    # 進行LU分解
    for i in range(n):
        # 尋找主元（部分樞軸法）
        max_row = i
        for k in range(i + 1, n):
            if abs(A[k, i]) > abs(A[max_row, i]):
                max_row = k
        
        # 如果需要行交換
        if max_row != i:
            A[[i, max_row]] = A[[max_row, i]]
            row_swaps += 1
        
        # 檢查是否為奇異矩陣
        if abs(A[i, i]) < 1e-10:
            return 0.0  # 奇異矩陣，行列式為0
        
        # 計算U的第i行
        for j in range(i, n):
            U[i, j] = A[i, j] - sum(L[i, k] * U[k, j] for k in range(i))
        
        # 計算L的第i列
        L[i, i] = 1  # Doolittle分解中L的對角線元素為1
        for j in range(i + 1, n):
            L[j, i] = (A[j, i] - sum(L[j, k] * U[k, i] for k in range(i))) / U[i, i]
    
    # 計算行列式
    # det(A) = (-1)^row_swaps * det(U)
    det_U = np.prod(np.diag(U))
    det_A = ((-1) ** row_swaps) * det_U
    
    return det_A

# 測試範例
if __name__ == "__main__":
    # 測試矩陣1: 2x2矩陣
    matrix1 = [[4, 3],
               [6, 8]]
    
    print("測試矩陣1:")
    print(np.array(matrix1))
    print(f"使用scipy LU分解: {determinant_by_lu(matrix1):.6f}")
    print(f"手動LU分解: {determinant_by_lu_manual(matrix1):.6f}")
    print(f"numpy內建函數: {np.linalg.det(matrix1):.6f}")
    print()
    
    # 測試矩陣2: 3x3矩陣
    matrix2 = [[2, -1, 0],
               [-1, 2, -1],
               [0, -1, 2]]
    
    print("測試矩陣2:")
    print(np.array(matrix2))
    print(f"使用scipy LU分解: {determinant_by_lu(matrix2):.6f}")
    print(f"手動LU分解: {determinant_by_lu_manual(matrix2):.6f}")
    print(f"numpy內建函數: {np.linalg.det(matrix2):.6f}")
    print()
    
    # 測試矩陣3: 4x4矩陣
    matrix3 = [[1, 2, 3, 4],
               [2, 5, 7, 3],
               [3, 7, 12, 1],
               [4, 3, 1, 8]]
    
    print("測試矩陣3:")
    print(np.array(matrix3))
    print(f"使用scipy LU分解: {determinant_by_lu(matrix3):.6f}")
    print(f"手動LU分解: {determinant_by_lu_manual(matrix3):.6f}")
    print(f"numpy內建函數: {np.linalg.det(matrix3):.6f}")
    print()
    
    # 測試奇異矩陣
    singular_matrix = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]]
    
    print("奇異矩陣測試:")
    print(np.array(singular_matrix))
    print(f"使用scipy LU分解: {determinant_by_lu(singular_matrix):.6f}")
    print(f"手動LU分解: {determinant_by_lu_manual(singular_matrix):.6f}")
    print(f"numpy內建函數: {np.linalg.det(singular_matrix):.6f}")