from sympy.liealgebras import CartanType

# 1. 定義李代數 A2
ct = CartanType("A2")

# 2. 基本屬性
print(f"李代數類型: {ct.series} (rank: {ct.rank()})") # 這裡 rank() 是方法，有些版本是屬性，建議用屬性 ct.rank 即可
print(f"維度 (Dimension): {ct.dimension}") 

# 3. 卡坦矩陣
print("\n卡坦矩陣:")
print(ct.cartan_matrix())

# 4. 修正的部分
# 如果你要的是數量 (Rank)：
print(f"\n單根 (Simple Roots) 的數量: {ct.rank()}")

# 如果你要的是具體向量，可以用迴圈印出：
print("單根向量內容:")
for i in range(1, ct.rank() + 1):
    print(f"Alpha {i}: {ct.simple_root(i)}")

from sympy.liealgebras import CartanType
# 記得要從子模組 import RootSystem
from sympy.liealgebras.root_system import RootSystem
from sympy import Matrix

# 1. 建立 G2 的根系物件
rs = RootSystem("G2")

# 2. 獲取單根 (Simple Roots)
simple_roots = rs.simple_roots()
print(f"G2 的單根 (Simple Roots):")
for idx, vec in simple_roots.items():
    print(f"alpha_{idx}: {vec}")

# 3. 獲取所有根
all_roots = rs.all_roots()
print(f"\nG2 的所有根 (共 {len(all_roots)} 個):")
print(f"{all_roots}")

# --- 4. 修正部分：計算基礎權重 (Fundamental Weights) ---
print(f"\n基礎權重 (Fundamental Weights):")

# 取得卡坦矩陣並計算逆矩陣
c_matrix = rs.cartan_matrix()
c_inv = c_matrix.inv()

print(f"逆卡坦矩陣:\n{c_inv}")

# 根據公式計算權重: omega_i = sum( C_inv[j, i-1] * alpha_j )
# 注意：SymPy 的矩陣索引是從 0 開始，但李代數習慣從 1 開始
rank = rs.cartan_type.rank()
fundamental_weights = {}

for i in range(1, rank + 1):
    # 初始化一個零向量 (維度與單根相同)
    # 這裡我們取 alpha_1 的長度來決定向量維度
    dim = len(simple_roots[1])
    omega = [0] * dim 
    
    # 進行線性組合
    for j in range(1, rank + 1):
        # 係數是逆矩陣的元素 (注意轉置關係與索引偏移)
        # 對應公式 omega_i = sum( (C^-1)_ji * alpha_j )
        coeff = c_inv[j-1, i-1] 
        alpha = simple_roots[j]
        
        # 向量加法
        for k in range(dim):
            omega[k] += coeff * alpha[k]
            
    fundamental_weights[i] = omega
    print(f"omega_{i}: {omega}")

# 5. 卡坦矩陣
print(f"\nCartan Matrix of G2:\n{c_matrix}")