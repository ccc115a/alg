import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# 數學： $C^i_k = A^i_j B^j_k$
# 愛因斯坦標記： 'ij,jk->ik'
C_einsum = np.einsum('ij,jk->ik', A, B)

# 傳統 NumPy 做法 (驗證)
C_dot = A @ B

print(f"矩陣 A:\n{A}")
print(f"矩陣 B:\n{B}")
print(f"矩陣乘法 $A^i_j B^j_k$ 結果:\n{C_einsum}")
print(f"使用 @ 運算符驗證結果:\n{C_dot}")