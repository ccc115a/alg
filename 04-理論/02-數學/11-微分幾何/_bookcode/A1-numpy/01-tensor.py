import numpy as np

# 假設空間維度 N=3
N = 3

# 0 階張量 (純量)
scalar = np.array(5.0)
print(f"純量：\n{scalar}\n階數 (ndim): {scalar.ndim}")

# 1 階張量 (逆變向量)
vector_v = np.array([1.0, 2.0, 3.0])
print(f"\n向量：\n{vector_v}\n階數 (ndim): {vector_v.ndim}")

# 2 階張量 (度量張量 $g_{ij}$ 或矩陣)
# 這裡使用單位矩陣作為示例
metric_g = np.identity(N)
print(f"\n二階張量 (度量張量 $g_{{ij}}$)：\n{metric_g}\n階數 (ndim): {metric_g.ndim}")

# 4 階張量 (例如黎曼曲率張量 $R^k_{lij}$ 的分量)
# 僅為演示形狀，內容為隨機
R_tensor = np.random.rand(N, N, N, N)
print(f"\n四階張量 (曲率張量 $R^k_{{lij}}$)：\n形狀 (shape): {R_tensor.shape}\n階數 (ndim): {R_tensor.ndim}")