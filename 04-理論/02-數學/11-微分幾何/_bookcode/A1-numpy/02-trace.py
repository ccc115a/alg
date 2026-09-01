import numpy as np

# 2 階張量 (矩陣) T
T = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]])

# 數學： $T^i_i$ (跡)
# 愛因斯坦標記： 'ii->' 表示將第一個索引和第二個索引相同的值相加 (求和)
trace_einsum = np.einsum('ii->', T)

# 傳統 NumPy 做法 (驗證)
trace_numpy = np.trace(T)

print(f"原始張量 T:\n{T}")
print(f"使用 einsum 計算的跡 (Trace, $T^i_i$): {trace_einsum}")
print(f"使用 np.trace 驗證結果: {trace_numpy}")