import sympy as sp

def create_vector_operator(components, coords):
    """
    建立一個現代幾何觀點的向量算子 v
    
    參數:
    components: 向量的分量列表，例如 [3, 4] 對應 (3, 4)
    coords: 符號變數列表，例如 [x, y]
    
    回傳:
    一個函數 v_op(f)，該函數代表向量算子
    """
    
    # 這是核心：v 是一個接收函數 f 的算子
    def v_op(f):
        # 1. 計算 v(f) 的符號表達式
        # 數學公式: v(f) = Σ v^i * (∂f/∂x^i)
        result_expr = 0
        for v_i, x_i in zip(components, coords):
            # sp.diff(f, x_i) 就是偏微分 ∂f/∂x^i
            result_expr += v_i * sp.diff(f, x_i)
            
        # 為了讓使用者看到數學形式，我們先印出產生的新函數長什麼樣
        print(f"  [運算中] v(f) 產生的新函數表達式為: {result_expr}")

        # 2. 回傳一個「新的函數」
        # 這個函數接收點座標 p，並回傳數值
        def evaluator(p):
            # 檢查維度是否匹配
            if len(p) != len(coords):
                raise ValueError("座標點維度與空間維度不符")
            
            # 將符號替換為具體數值 (例如 x=1, y=2)
            subs_dict = dict(zip(coords, p))
            return float(result_expr.subs(subs_dict))
            
        return evaluator

    return v_op

# ==========================================
# 實例演示：重現剛才的登山例子
# ==========================================

# 1. 定義符號 (座標系)
x, y = sp.symbols('x y')
coords = [x, y]

# 2. 定義地形函數 f = x^2 + y^2
f = x**2 + y**2
print(f"原始函數 f(x, y) = {f}")

# 3. 定義向量 v = 3(∂/∂x) + 4(∂/∂y)
# 我們把 v 造成一個算子物件
v = create_vector_operator(components=[3, 4], coords=coords)

# 4. 關鍵步驟：讓 v 作用在 f 上
# 這對應數學上的 vf = v(f)
# 注意：這裡還沒有代入具體的點 (1, 2)
print("\n--- 執行 v(f) ---")
df_v = v(f) 
# 此時 df_v 已經是一個 python 函數了，它代表「沿著 v 方向的變化率函數」

# 5. 最後一步：代入具體的位置 p = (1, 2)
p = [1, 2]
value = df_v(p)

print("\n--- 代入點 p=(1, 2) ---")
print(f"在點 {p} 處，沿向量 v 的方向導數為: {value}")

# 驗證一下： 22.0 嗎？
assert value == 22.0