import numpy as np

# 假設 N=3
N = 3

# 度量張量 $g_{ij}$ (這裡使用一個非歐幾里得的度量示例)
g_ij = np.array([[2, 0, 0],
                 [0, 1, 0],
                 [0, 0, 3]])

# 逆變向量 $v^j$
v_upper = np.array([10.0, 5.0, 1.0])

# 數學： $v_i = g_{ij} v^j$
# 愛因斯坦標記： 'ij,j->i'
v_lower = np.einsum('ij,j->i', g_ij, v_upper)

print(f"度量張量 $g_{{ij}}$:\n{g_ij}")
print(f"逆變向量 $v^j$: {v_upper}")
print(f"協變向量 $v_i$ (降低指標): {v_lower}")
# 驗證: v_lower[0] = g_0j v^j = g_00 v^0 = 2 * 10.0 = 20.0
# 驗證: v_lower[1] = g_1j v^j = g_11 v^1 = 1 * 5.0 = 5.0
# 驗證: v_lower[2] = g_2j v^j = g_22 v^2 = 3 * 1.0 = 3.0