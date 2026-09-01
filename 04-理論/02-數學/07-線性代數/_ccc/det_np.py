import numpy as np

def determinant_numpy_recursive(matrix):
    """
    使用 NumPy 和遞迴方式計算行列式。
    """
    # 將輸入轉換為 NumPy 陣列，方便後續操作
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)

    n = matrix.shape[0]

    # 基礎情況：1x1 矩陣
    if n == 1:
        return matrix[0, 0]

    det = 0
    # 遍歷第一列
    for j in range(n):
        # 使用 np.delete 建立子矩陣
        # axis=0 刪除第一列，axis=1 刪除第 j 行
        sub_matrix = np.delete(matrix, 0, axis=0)
        sub_matrix = np.delete(sub_matrix, j, axis=1)

        # 計算餘因子
        det += ((-1)**j) * matrix[0, j] * determinant_numpy_recursive(sub_matrix)

    return det

# 範例
matrix_np = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])
print(f"NumPy 輔助遞迴計算結果：{determinant_numpy_recursive(matrix_np)}")

matrix_np2 = np.array([
    [1, 2],
    [3, 4]
])
print(f"NumPy 輔助遞迴計算結果：{determinant_numpy_recursive(matrix_np2)}")