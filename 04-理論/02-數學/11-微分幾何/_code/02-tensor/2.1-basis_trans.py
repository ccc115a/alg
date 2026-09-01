import numpy as np

# 假設空間維度 N=2

# 1. 定義標準基底
# 標準基底 $B = \{\mathbf{e}_1, \mathbf{e}_2\}$
e1_std = np.array([1, 0])
e2_std = np.array([0, 1])
print(f"標準基底 e1: {e1_std}, e2: {e2_std}\n")

# 2. 定義一個新的非標準基底 $B' = \{\mathbf{e}'_1, \mathbf{e}'_2\}$
# 選擇一個非正交的基底來演示變換
e1_new = np.array([1, 1])
e2_new = np.array([-1, 1])
print(f"新基底 e'1: {e1_new}, e'2: {e2_new}")

# 3. 定義變換矩陣 P (從新基底 $B'$ 到 標準基底 $B$)
# P 的列向量是新基底 $B'$ 在標準基底 $B$ 下的坐標。
# $\mathbf{e}'_j = \sum_{i} P^i_j \mathbf{e}_i \implies P = [\mathbf{e}'_1 | \mathbf{e}'_2]$
P_matrix = np.column_stack((e1_new, e2_new))
print(f"\n變換矩陣 P (從 $B'$ 到 $B$):\n{P_matrix}")

# 4. 定義一個向量 $\mathbf{v}$ 在標準基底 $B$ 下的坐標 $v^i$
v_std_coords = np.array([4, 2])
print(f"\n向量 $\mathbf{{v}}$ 在標準基底下的坐標 $v^i$: {v_std_coords}")

# 5. 計算逆變換矩陣 $P^{-1}$ (從 標準基底 $B$ 到 新基底 $B'$)
# $v'^j = (P^{-1})^j_i v^i \implies \mathbf{v}' = P^{-1} \mathbf{v}$
try:
    P_inv = np.linalg.inv(P_matrix)
    print(f"\n逆變換矩陣 $P^{{-1}}$ (從 $B$ 到 $B'$):\n{P_inv.round(4)}") # 顯示四位小數

    # 6. 計算向量 $\mathbf{v}$ 在新基底 $B'$ 下的坐標 $v'^j$
    v_new_coords = P_inv @ v_std_coords
    
    print(f"\n向量 $\mathbf{{v}}$ 在新基底下的坐標 $v'^j$: {v_new_coords.round(4)}")
    
    # 7. 驗證結果：使用新坐標和新基底重建原始向量
    v_reconstructed = v_new_coords[0] * e1_new + v_new_coords[1] * e2_new
    print(f"\n驗證：使用新坐標重建的向量 $\mathbf{{v}}$: {v_reconstructed.round(4)}")
    
    # 驗證 $v'^j$ 的含義: $\mathbf{v} = v'^1 \mathbf{e}'_1 + v'^2 \mathbf{e}'_2$
    # 理論值: 4*e1 + 2*e2 = 3*e'1 + (-1)*e'2
    # 3* [1, 1] + (-1) * [-1, 1] = [3, 3] + [1, -1] = [4, 2]
    # 程式碼結果應為 [3, -1]
    
except np.linalg.LinAlgError:
    print("\n錯誤：變換矩陣是奇異的（Singular），無法計算逆矩陣。")