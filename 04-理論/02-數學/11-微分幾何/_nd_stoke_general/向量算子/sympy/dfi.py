import sympy as sp

def create_dx_i(index, coords):
    """
    建立一個 1-形式 dx^i
    
    參數:
    index: 座標的索引 (0 對應 x, 1 對應 y...)
    coords: 符號變數列表
    
    回傳:
    一個函數 dx_op(vector_field)，代表 1-形式算子
    """
    
    # 取得對應的座標名稱 (例如 'x' 或 'y')，僅用於顯示
    coord_name = coords[index].name
    
    # 這是核心：dx 是一個接收向量 v 的機器
    def dx_op(vector_field):
        # 1. 數學定義：dx^i(v) = v^i
        # 我們只需要把向量的第 i 個分量「抓」出來
        if len(vector_field) != len(coords):
            raise ValueError("向量維度與座標不符")
            
        result_expr = vector_field[index]
        
        print(f"  [運算中] d{coord_name} 吃掉了向量，抓出了第 {index+1} 個分量: {result_expr}")

        # 2. 回傳一個「新的函數」
        # 這個函數接收點座標 p，並回傳數值
        def evaluator(p):
            # 如果抓出來的結果只是常數 (例如 3)，直接回傳
            if isinstance(result_expr, (int, float)):
                return float(result_expr)
            # 如果是 sympy 表達式 (例如 2*x)，則需要代入
            if hasattr(result_expr, 'subs'):
                subs_dict = dict(zip(coords, p))
                return float(result_expr.subs(subs_dict))
            return result_expr

        return evaluator

    return dx_op

# ==========================================
# 實例演示
# ==========================================

# 1. 定義符號
x, y = sp.symbols('x y')
coords = [x, y]

# 2. 建立 1-形式算子： dx 和 dy
# dx 對應索引 0，dy 對應索引 1
dx = create_dx_i(0, coords)
dy = create_dx_i(1, coords)

# 3. 定義一個「向量場」 (Vector Field)
# 這次我們用稍微複雜一點的，向量的分量是會隨位置變化的
# 向量 v = (2x) ∂/∂x + (x*y) ∂/∂y
vector_field = [2*x, x*y]
print(f"向量場 v = {vector_field}")

# 4. 關鍵步驟：讓 dx 和 dy 作用在向量 v 上
print("\n--- 執行 dx(v) ---")
func_x = dx(vector_field)  # 應該抓出 2x

print("\n--- 執行 dy(v) ---")
func_y = dy(vector_field)  # 應該抓出 x*y

# 5. 代入具體位置 p = (3, 4)
# x=3, y=4
p = [3, 4]

print(f"\n--- 代入點 p={p} ---")
val_x = func_x(p)  # 2*3 = 6
val_y = func_y(p)  # 3*4 = 12

print(f"dx(v) 在 p 點的值: {val_x}")  # 預期 6.0
print(f"dy(v) 在 p 點的值: {val_y}")  # 預期 12.0

# ==========================================
# 進階：通用的 1-形式 ω = 3dx + 5dy
# ==========================================
print("\n--- 進階：線性組合 ω = 3dx + 5dy ---")

# 1-形式也可以線性疊加
def omega(v_field):
    # ω(v) = 3 * dx(v) + 5 * dy(v)
    # 這裡利用我們剛才做出來的 func_x, func_y 的邏輯
    # 但為了簡潔，我們直接操作算子結果
    
    res_dx = dx(v_field) # 得到一個函數
    res_dy = dy(v_field) # 得到一個函數
    
    # 回傳一個新的 evaluator
    def evaluator(p):
        return 3 * res_dx(p) + 5 * res_dy(p)
    return evaluator

# 讓 ω 作用在 v 上
w_v = omega(vector_field)
final_val = w_v(p)
print(f"ω(v) 在 p 點的值: {final_val}")
# 驗證：3*(6) + 5*(12) = 18 + 60 = 78