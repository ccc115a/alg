from sympy import symbols, Function, diff, simplify
from itertools import combinations, product

# 1. 初始化符號變數
x, y, z = symbols('x y z')
coords = [x, y, z] # 空間座標 (我們在 R^3 中操作)

class DifferentialForm:
    """
    用字典來表示微分形式: { (index_tuple): coefficient_function }
    index_tuple e.g., (0, 1) 代表 dx ^ dy (假設 x=0, y=1)
    """
    def __init__(self, degree, components):
        self.k = degree
        # components: { (i1, i2, ...): f(x,y,z) }
        self.components = components
        self.normalize()

    def normalize(self):
        """
        確保所有的 index_tuple 都是遞增排序，並調整係數的符號 (外積的反交換律)
        """
        new_components = {}
        for indices, coeff in self.components.items():
            if not indices: # 0-form
                new_components[()] = coeff
                continue
            
            # 1. 檢查是否有重複索引 (dxi ^ dxi = 0)
            if len(set(indices)) != len(indices):
                # 包含重複的項，係數為 0
                continue
            
            # 2. 進行排序並計算置換符號
            sorted_indices = tuple(sorted(indices))
            num_swaps = 0
            current_list = list(indices)
            
            # 使用冒泡排序計算置換次數
            for i in range(len(current_list)):
                for j in range(i + 1, len(current_list)):
                    if current_list[i] > current_list[j]:
                        current_list[i], current_list[j] = current_list[j], current_list[i]
                        num_swaps += 1
                        
            sign = 1 if num_swaps % 2 == 0 else -1
            
            # 3. 累加到正規化後的字典中
            new_components[sorted_indices] = new_components.get(sorted_indices, 0) + sign * coeff
            
        # 移除係數為零的項，並更新
        self.components = {k: simplify(v) for k, v in new_components.items() if simplify(v) != 0}
        
    def __repr__(self):
        if not self.components: return "0-form"
        
        terms = []
        # 將索引轉換回 dx, dy, dz
        coord_names = [str(c) for c in coords]
        
        for indices, coeff in self.components.items():
            base_str = " ^ ".join([f"d{coord_names[i]}" for i in indices])
            terms.append(f"({coeff}) * {base_str}")
            
        return " + ".join(terms)

def ExteriorDifferential(omega: DifferentialForm) -> DifferentialForm:
    """
    實作外微分算子 d: d(omega) = sum_I d(f_I) ^ (dx_i1 ^ ...)
    """
    new_components = {}
    k = omega.k
    
    # 遍歷原始微分形式的每個項
    for indices_old, coeff_old in omega.components.items():
        
        # 1. 計算係數的微分 d(f_I) = sum_j (df_I / dx_j) * dx_j
        for j, coord_j in enumerate(coords):
            
            # 偏微分: df_I / dx_j
            partial_deriv = diff(coeff_old, coord_j)
            
            if partial_deriv == 0:
                continue
            
            # 2. 外積運算: d(f_I) ^ (dx_i1 ^ ...)
            # 新的基底索引: (j) 加上原來的 (i1, i2, ...)
            new_indices_raw = (j,) + indices_old
            
            # 3. 建立新的項並累加
            # 使用一個臨時的 Form 來處理排序和符號
            temp_form = DifferentialForm(k + 1, {new_indices_raw: partial_deriv})
            
            # 將 temp_form 的正規化結果累加到 new_components
            for indices_new, coeff_new in temp_form.components.items():
                new_components[indices_new] = new_components.get(indices_new, 0) + coeff_new
                
    # 4. 最終結果需要再次正規化 (因為我們是簡單相加)
    result_form = DifferentialForm(k + 1, new_components)
    return result_form


# --- 範例測試 ---

# 1. 測試 d(d f) = 0 (0-形式)
## 1-a. 定義 0-形式 f
f = Function('f')(x, y, z)
omega_0 = DifferentialForm(0, {(): f})

## 1-b. 計算 d f (1-形式)
omega_1 = ExteriorDifferential(omega_0)
print("--- 測試 d(f) ---")
print(f"d(f) = {omega_1}\n")

## 1-c. 計算 d(d f) (2-形式)
omega_2 = ExteriorDifferential(omega_1)
print("--- 測試 d(d f) ---")
print(f"d(d f) = {omega_2}\n")

if not omega_2.components:
    print("✅ 驗證成功: d(d f) 的結果為 0-form，符合龐加萊引理 d(d f) = 0。")
else:
    print("❌ 驗證失敗。")

# 2. 測試 d(omega_1) (1-形式)
## 2-a. 定義 1-形式 omega_1 = P dx + Q dy
P = Function('P')(x, y, z)
Q = Function('Q')(x, y, z)
R = Function('R')(x, y, z)

omega_1_test = DifferentialForm(1, {
    (0,): P, # P dx
    (1,): Q, # Q dy
    (2,): R  # R dz
})

## 2-b. 計算 d(omega_1_test) (2-形式)
# 預期結果 (Curl): (dQ/dx - dP/dy) dx^dy + (dR/dy - dQ/dz) dy^dz + (dP/dz - dR/dx) dz^dx
omega_2_test = ExteriorDifferential(omega_1_test)
print("\n--- 測試 d(P dx + Q dy + R dz) (Curl) ---")
print(f"d(omega_1) = {omega_2_test}")

## 2-c. 驗證 d(d(omega_1)) = 0 (3-形式)
omega_3_test = ExteriorDifferential(omega_2_test)
print("\n--- 測試 d(d(omega_1)) ---")
print(f"d(d(omega_1)) = {omega_3_test}")

if not omega_3_test.components:
    print("✅ 驗證成功: d(d(omega_1)) 的結果為 0-form，符合龐加萊引理 d(d omega) = 0。")