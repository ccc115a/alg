import numpy as np

u = np.array([1, 2])
v = np.array([10, 20, 30])

# 數學： $P^{ij} = u^i v^j$
# 愛因斯坦標記： 'i,j->ij'
P_einsum = np.einsum('i,j->ij', u, v)

# 傳統 NumPy 做法 (驗證)
P_outer = np.outer(u, v)

print(f"向量 u: {u}")
print(f"向量 v: {v}")
print(f"張量積 $u^i v^j$ (形狀 (2, 3)):\n{P_einsum}")
print(f"使用 np.outer 驗證結果:\n{P_outer}")