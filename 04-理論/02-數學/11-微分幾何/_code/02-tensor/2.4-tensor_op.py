import numpy as np

# 假設空間維度 N=3
N = 3

# 1. 定義輸入張量
A_i = np.array([1, 2, 3])          # 1 階協變張量 (向量)
B_jk = np.arange(1, 10).reshape(3, 3) # 2 階協變張量 (矩陣)
T_ijk = np.arange(1, 28).reshape(3, 3, 3) # 3 階張量
v_i = np.array([1, 0, 0])          # 逆變向量 1
w_j = np.array([0, 1, 0])          # 逆變向量 2
g_ij = np.identity(N)              # 度量張量 $g_{ij}$ (這裡使用歐幾里得度量)

print(f"--- 1. 張量積 (Tensor Product) ---")
print(f"輸入張量 A_i (Rank 1):\n{A_i}")
print(f"輸入張量 B_jk (Rank 2):\n{B_jk}")

# 數學： $C_{ijk} = A_i B_{jk}$
# einsum 標記: 'i,jk->ijk' (結果為 Rank 3)
C_ijk = np.einsum('i,jk->ijk', A_i, B_jk)

print(f"\n張量積 $C_{{ijk}}$ (Rank 3, Shape {C_ijk.shape}):\n")
# 打印部分結果，例如 i=0 的平面
print(f"i=0 的分量 (A_0 * B_jk):\n{C_ijk[0]}")
print("-" * 40)


print(f"--- 2. 張量縮並 (Contraction) ---")
print(f"輸入張量 T_ijk (Rank 3, Shape {T_ijk.shape})")

# 數學： $D_i = T_{ijj}$ (縮並後兩個指標 $j$ 和 $k$)
# einsum 標記: 'ijj->i' (將第二個和第三個索引 $j, j$ 縮並)
D_i = np.einsum('ijj->i', T_ijk)

print(f"\n縮並結果 $D_i$ (Rank 1, Shape {D_i.shape}): {D_i}")
# 驗證 D_0 = T_000 + T_011 + T_022 = 1 + 5 + 9 = 15
# 驗證 D_1 = T_100 + T_111 + T_122 = 10 + 14 + 18 = 42
print("-" * 40)


print(f"--- 3. 黎曼內積 (Riemannian Inner Product) ---")
print(f"度量張量 $g_{{ij}}$ (歐幾里得):\n{g_ij}")
print(f"向量 $v^i$: {v_i}")
print(f"向量 $w^j$: {w_j}")

# 數學： $S = g_{ij} v^i w^j$
# einsum 標記: 'ij,i,j->' (將三個張量相乘並對所有指標 $i, j$ 求和，結果為 Rank 0 純量)
S_scalar = np.einsum('ij,i,j->', g_ij, v_i, w_j)

print(f"\n內積 $S = g_{{ij}} v^i w^j$: {S_scalar}")
# 驗證: 由於 v 和 w 是正交的單位向量，且 $g_{ij}$ 是單位矩陣，內積應為 0。
# 實際計算: $g_{01} v^0 w^1 = 1 \times 1 \times 1 = 1$. (因為 $g_{01}=0$, 應為 0)
# 修正：$g_{ij}$ 為對角線上的 1 才有貢獻。
# $S = g_{12} v^1 w^2 + g_{21} v^2 w^1 + \dots$ 
# $S = g_{11} v^1 w^1 + g_{22} v^2 w^2 + \dots$
# $v^0=1, w^1=1$. $g_{01}=0$. $g_{ij} v^i w^j$ 僅在 $i=j$ 時非零。
# 由於 $i=0, j=1$ 且 $g_{01}=0$，結果應為 0。
# Let's verify the calculation step-by-step for the inputs:
# i=0, j=0: g_00 * v_0 * w_0 = 1 * 1 * 0 = 0
# i=0, j=1: g_01 * v_0 * w_1 = 0 * 1 * 1 = 0
# i=1, j=0: g_10 * v_1 * w_0 = 0 * 0 * 0 = 0
# i=1, j=1: g_11 * v_1 * w_1 = 1 * 0 * 1 = 0
# S_scalar = 0.0, 驗證正確。

# 更改內積測試範例：計算向量 $\mathbf{v}$ 的長度的平方 $g_{ij} v^i v^j$
v_i_test = np.array([3, 4, 0])
S_norm_sq = np.einsum('ij,i,j->', g_ij, v_i_test, v_i_test)

print(f"\n計算向量 $\mathbf{{v}}=(3, 4, 0)$ 的長度平方 $g_{{ij}} v^i v^j$: {S_norm_sq}")
# 驗證: $3^2 + 4^2 + 0^2 = 9 + 16 = 25.0$