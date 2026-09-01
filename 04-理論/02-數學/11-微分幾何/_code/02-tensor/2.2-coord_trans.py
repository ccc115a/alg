import numpy as np

# 假設空間維度 N=2

# 1. 沿用前一節的基底和變換矩陣
e1_new = np.array([1, 1])
e2_new = np.array([-1, 1])

# 變換矩陣 P (從新基底 $B'$ 到 標準基底 $B$)
# P 的列向量是新基底 $B'$ 在標準基底 $B$ 下的坐標。
P_matrix = np.column_stack((e1_new, e2_new))

# P_matrix = [[ 1, -1], [ 1,  1]]
print(f"--- 協變向量 (1-形式) 坐標變換示範 ---")
print(f"新基底 $\\mathbf{{e}}'_j$ 到 標準基底 $\\mathbf{{e}}_i$ 的變換矩陣 P:\n{P_matrix}")

# 2. 定義一個協變向量 (1-形式) $\omega$ 在標準對偶基底 $\mathbf{e}^i$ 下的坐標 $\omega_i$
# $\omega = \omega_1 \mathbf{e}^1 + \omega_2 \mathbf{e}^2$
omega_std_coords = np.array([5.0, 3.0])
print(f"\n協變向量 $\\omega$ 在標準對偶基底下的坐標 $\\omega_i$: {omega_std_coords}")

# 3. 協變向量分量的變換法則： $\omega'_j = P^i_j \omega_i$
# 注意：這裡使用 P 矩陣（而非 $P^{-1}$）進行變換。
# 在 NumPy 矩陣乘法中，這相當於 $\mathbf{\omega}' = \mathbf{\omega} P$ (當 $\omega$ 是行向量時)
# 或者 $\mathbf{\omega}' = P^T \mathbf{\omega}$ (當 $\omega$ 是列向量時)
# 我們使用矩陣乘法 $P^T \omega$
P_T = P_matrix.T # 轉置矩陣

# $P^T = [[ 1, 1], [-1, 1]]$
omega_new_coords = P_T @ omega_std_coords

print(f"\n變換矩陣 $P$ 的轉置 $P^T$ (用於協變向量變換):\n{P_T}")
print(f"\n協變向量 $\\omega$ 在新對偶基底下的坐標 $\\omega'_j$: {omega_new_coords.round(4)}")


# 4. 驗證協變性：向量與協變向量的作用結果必須不變 (張量性質)
# 設 $\mathbf{v}$ 是前一節的逆變向量，其標準坐標 $v^i = [4, 2]$
v_std_coords = np.array([4, 2])
# 逆變向量在新基底下的坐標 $v'^j$ (從前一節的結果)
P_inv = np.linalg.inv(P_matrix)
v_new_coords = P_inv @ v_std_coords # $v'^j = P^{-1} v^i$

# 作用結果（內積）在標準基底 $B$ 下： $\omega(\mathbf{v}) = \omega_i v^i$
result_std = np.einsum('i,i->', omega_std_coords, v_std_coords)

# 作用結果（內積）在新基底 $B'$ 下： $\omega'(\mathbf{v}) = \omega'_j v'^j$
result_new = np.einsum('j,j->', omega_new_coords, v_new_coords)

print("-" * 40)
print(f"驗證：逆變/協變向量的縮並 (內積) 結果必須不變 (張量性質)")
print(f"舊坐標下的作用結果 $\\omega_i v^i$: {result_std}")
print(f"新坐標下的作用結果 $\\omega'_j v'^j$: {result_new.round(4)}")

if np.isclose(result_std, result_new):
    print("驗證成功：作用結果在基底變換下保持不變。")
else:
    print("驗證失敗：作用結果在基底變換下發生改變。")