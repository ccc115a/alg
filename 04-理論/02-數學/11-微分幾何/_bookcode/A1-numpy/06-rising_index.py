import numpy as np

# 沿用上一例的度量張量 $g_{ij}$
g_ij = np.array([[2, 0, 0],
                 [0, 1, 0],
                 [0, 0, 3]])

# 協變向量 $v_j$ (沿用上一例的結果)
v_lower = np.array([20.0, 5.0, 3.0])

# 1. 計算逆度量張量 $g^{ij}$
# 注意：這一步在一般流形上是局部的，且可能很複雜，這裡用簡單的矩陣逆運算
g_upper = np.linalg.inv(g_ij)

# 2. 數學： $v^i = g^{ij} v_j$
# 愛因斯坦標記： 'ij,j->i'
v_upper_restored = np.einsum('ij,j->i', g_upper, v_lower)

print(f"逆度量張量 $g^{{ij}}$:\n{g_upper}")
print(f"協變向量 $v_j$: {v_lower}")
print(f"還原的逆變向量 $v^i$ (提升指標): {v_upper_restored}")