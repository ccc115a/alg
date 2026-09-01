def determinant_recursive(matrix):
    """
    使用遞迴方式計算行列式（不使用 NumPy）。
    """
    n = len(matrix)

    # 基礎情況：如果矩陣是 1x1，直接回傳其唯一元素
    if n == 1:
        return matrix[0][0]

    det = 0
    # 遍歷第一列的每個元素
    for j in range(n):
        # 建立一個新的子矩陣（不包含第一列和第 j 行）
        sub_matrix = []
        for i in range(1, n):
            row = []
            for k in range(n):
                if k != j:
                    row.append(matrix[i][k])
            sub_matrix.append(row)

        # 計算餘因子，並加到總和中
        # 餘因子 = (-1)^(1+j+1) * 元素 * 子矩陣的行列式
        # 這裡的 (1+j+1) 是指 row_index + col_index，但我們從 0 開始
        # 所以是 (0+j)
        det += ((-1)**j) * matrix[0][j] * determinant_recursive(sub_matrix)

    return det

# 範例
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
print(f"純 Python 遞迴計算結果：{determinant_recursive(matrix)}")

matrix2 = [
    [1, 2],
    [3, 4]
]
print(f"純 Python 遞迴計算結果：{determinant_recursive(matrix2)}")