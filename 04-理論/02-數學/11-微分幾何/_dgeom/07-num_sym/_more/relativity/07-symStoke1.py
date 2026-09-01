from sympy import symbols, Function, diff

# 1. 定義符號變數和函數
# x, y 是空間座標
x, y = symbols('x y')
# f 是定義在 R^2 上的光滑純量函數 (0-形式)
f = Function('f')(x, y)

print(f"原始 0-形式 f: {f}\n")

# 2. 模擬外微分算子 d (適用於 0-形式)
def exterior_derivative_d(scalar_function, coordinates):
    """
    計算 0-形式 (純量函數) 的外微分 (d f)。
    結果是一個 1-形式，形式為 (df/dx) * dx + (df/dy) * dy + ...
    這裡我們只返回偏導函數組成的元組/列表。
    """
    derivatives = [diff(scalar_function, coord) for coord in coordinates]
    # 在實際的微分幾何中，df 是 derivatives[0]*dx + derivatives[1]*dy
    return derivatives

# 3. 計算 d f (1-形式)
# d_f_parts 相當於 [ df/dx, df/dy ]
d_f_parts = exterior_derivative_d(f, [x, y])

print(f"計算 d f (1-形式的係數):")
print(f"  df/dx = {d_f_parts[0]}")
print(f"  df/dy = {d_f_parts[1]}\n")

# 4. 計算 d(d f) (2-形式)
# d(d f) = d(df/dx) ^ dx + d(df/dy) ^ dy
# d(df/dx) ^ dx 包含項: (d^2f / dy dx) * dy ^ dx
# d(df/dy) ^ dy 包含項: (d^2f / dx dy) * dx ^ dy

# 計算 d(df/dx) 的 dy 係數: d^2f / dy dx
term_a_coeff = diff(d_f_parts[0], y)
# 計算 d(df/dy) 的 dx 係數: d^2f / dx dy
term_b_coeff = diff(d_f_parts[1], x)

print(f"計算 d(d f) 的關鍵係數:")
print(f"  項 A 係數 (d^2f / dy dx): {term_a_coeff} (乘以 dy ^ dx)")
print(f"  項 B 係數 (d^2f / dx dy): {term_b_coeff} (乘以 dx ^ dy)\n")

# 5. 驗證 d(d f) = 0
# d(d f) = (d^2f / dy dx) * dy ^ dx  +  (d^2f / dx dy) * dx ^ dy
# 利用外積的反交換律: dy ^ dx = - (dx ^ dy)
# d(d f) = -(d^2f / dy dx) * dx ^ dy + (d^2f / dx dy) * dx ^ dy
# 由於 SymPy 適用於光滑函數，克萊羅定理保證: d^2f / dy dx == d^2f / dx dy

# 總和的係數 (如果 dx ^ dy 獨立於零):
# total_coeff = term_b_coeff - term_a_coeff (因為 term_a_coeff 來自 -dy ^ dx)
total_coeff = term_b_coeff - term_a_coeff

# SymPy 的 simplify() 函數會利用克萊羅定理自動將混合偏導數相減簡化為 0
result = total_coeff.simplify()

print(f"驗證結果 (總和係數 term_b_coeff - term_a_coeff):")
print(f"  {term_b_coeff} - {term_a_coeff} = {result}")

if result == 0:
    print("\n✅ 驗證成功: 由於克萊羅定理 (混合偏導數相等)，SymPy 證明了 d(d f) 的係數總和為 0。")
    print("這體現了龐加萊引理 d(d f) = 0。")