import numpy as np

# 假設空間維度 N=3
N = 3

# 1. 內積 (Dot Product)
# 數學約定： $\mathbf{A} \cdot \mathbf{B} = A_i B^i$
# 這裡我們使用同一下標 $A_i B_i$ 進行歐幾里得空間的內積示範
A = np.array([1.0, 2.0, 3.0])
B = np.array([4.0, 5.0, 6.0])

# einsum 標記 'i,i->' : 從兩個一階張量（i, i）求和得到一個 0 階張量（純量）
dot_product = np.einsum('i,i->', A, B)

print(f"--- 1. 向量內積 (Dot Product) ---")
print(f"向量 A: {A}")
print(f"向量 B: {B}")
print(f"Einsum 標記 'i,i->' 結果 $A_i B_i$: {dot_product} (驗證: 1*4 + 2*5 + 3*6 = 32.0)")
print("-" * 40)


# 2. 矩陣乘法 (Matrix Multiplication)
# 數學約定： $C_{ik} = A_{ij} B_{jk}$
A_mat = np.array([[1, 2],
                  [3, 4]])
B_mat = np.array([[5, 6],
                  [7, 8]])

# einsum 標記 'ij,jk->ik' : $j$ 是啞指標（求和），$i, k$ 是自由指標（決定結果 $C_{ik}$）
matrix_multiplication = np.einsum('ij,jk->ik', A_mat, B_mat)

print(f"--- 2. 矩陣乘法 (Matrix Multiplication) ---")
print(f"矩陣 A:\n{A_mat}")
print(f"矩陣 B:\n{B_mat}")
print(f"Einsum 標記 'ij,jk->ik' 結果 $C_{{ik}}$:\n{matrix_multiplication}")
# 驗證: C[0,0] = A[0,j] B[j,0] = A[0,0]B[0,0] + A[0,1]B[1,0] = 1*5 + 2*7 = 19
print("-" * 40)

# 3. 張量縮並 (Contraction / Trace)
# 數學約定： $\text{Trace}(T) = T^i_i$ (這裡使用 $T_{ii}$)
T_tensor = np.array([[10, 1, 2],
                     [3, 20, 4],
                     [5, 6, 30]])

# einsum 標記 'ii->' : 縮並兩個指標 $i, i$，得到一個純量
trace = np.einsum('ii->', T_tensor)

print(f"--- 3. 張量縮並 (Trace) ---")
print(f"張量 T:\n{T_tensor}")
print(f"Einsum 標記 'ii->' 結果 $T_{{ii}}$ (跡): {trace} (驗證: 10 + 20 + 30 = 60)")