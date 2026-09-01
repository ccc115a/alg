from sympy import symbols, Function, diff, simplify
from itertools import combinations, product

# 1. 初始化符號變數
x, y, z = symbols('x y z')
coords = [x, y, z] # 空間座標 (我們在 R^3 中操作)

## ====== 自定義梯度函數 ======
def gradient(f_scalar_function, coordinates):
    """
    計算純量函數 f 在給定座標系下的梯度分量。
    
    Args:
        f_scalar_function (sympy expression): 純量函數 f (0-形式)。
        coordinates (list of sympy symbols): 座標變數 [x1, x2, ...]。
        
    Returns:
        list: 梯度向量的分量 [df/dx1, df/dx2, ...] (1-形式的係數)。
    """
    # 梯度的分量就是 f 對每個座標的偏導數
    gradient_components = [diff(f_scalar_function, coord) for coord in coordinates]
    return gradient_components
## ==============================


# 2. 定義微分形式 (DifferentialForm) 類別 (沿用上次的定義)
class DifferentialForm:
    def __init__(self, degree, components):
        self.k = degree
        # components: { (i1, i2, ...): f(x,y,z) }
        self.components = components
        self.normalize()

    def normalize(self):
        new_components = {}
        for indices, coeff in self.components.items():
            if not indices: new_components[()] = coeff; continue
            if len(set(indices)) != len(indices): continue # dxi ^ dxi = 0
            
            # 計算置換符號
            sorted_indices = tuple(sorted(indices))
            num_swaps = 0
            current_list = list(indices)
            for i in range(len(current_list)):
                for j in range(i + 1, len(current_list)):
                    if current_list[i] > current_list[j]:
                        current_list[i], current_list[j] = current_list[j], current_list[i]
                        num_swaps += 1
                        
            sign = 1 if num_swaps % 2 == 0 else -1
            
            # 累加到正規化後的字典中
            new_components[sorted_indices] = new_components.get(sorted_indices, 0) + sign * coeff
            
        self.components = {k: simplify(v) for k, v in new_components.items() if simplify(v) != 0}
        
    def __repr__(self):
        if not self.components: return "0-form"
        coord_names = [str(c) for c in coords]
        terms = []
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
    
    for indices_old, coeff_old in omega.components.items():
        
        # *** 關鍵變更：呼叫我們自定義的 gradient 函數 ***
        # 梯度分量 df_I / dx_j
        partial_derivs = gradient(coeff_old, coords) 
        
        # 2. 遍歷梯度分量
        for j, partial_deriv in enumerate(partial_derivs):
            
            if partial_deriv == 0:
                continue
            
            # 外積運算: d(f_I) ^ (dx_i1 ^ ...)
            # 新的基底索引: (j) 加上原來的 (i1, i2, ...)
            new_indices_raw = (j,) + indices_old
            
            # 建立臨時的 Form 來處理排序和符號
            temp_form = DifferentialForm(k + 1, {new_indices_raw: partial_deriv})
            
            # 將 temp_form 的正規化結果累加到 new_components
            for indices_new, coeff_new in temp_form.components.items():
                new_components[indices_new] = new_components.get(indices_new, 0) + coeff_new
                
    # 最終結果需要再次正規化
    result_form = DifferentialForm(k + 1, new_components)
    return result_form


# --- 範例測試 ---

# 1. 測試 d(d f) = 0 (0-形式)
f = Function('f')(x, y, z)
omega_0 = DifferentialForm(0, {(): f})

print("--- 測試 d(f) 的梯度分量 ---")
# 呼叫自定義的 gradient 函數
grad_f_components = gradient(f, coords)
print(f"∇f (df/dx, df/dy, df/dz) = {grad_f_components}\n")


print("--- 測試 d(d f) (龐加萊引理) ---")
omega_1 = ExteriorDifferential(omega_0)
omega_2 = ExteriorDifferential(omega_1)
print(f"d(d f) = {omega_2}\n")

if not omega_2.components:
    print("✅ 驗證成功: d(d f) 的結果為 0-form，符合龐加萊引理 d(d f) = 0。")