def fdot_numerical(f, g, a, b, N=1000):
    """
    使用梯形法近似計算兩個函數 f(x) 和 g(x) 在區間 [a, b] 上的內積。

    參數:
    f: 第一個函數，接受一個數值 x 並回傳一個數值。
    g: 第二個函數，接受一個數值 x 並回傳一個數值。
    a: 積分下限。
    b: 積分上限。
    N: 積分區間的分割數，數值越大，近似越精確。

    回傳:
    內積的近似數值。
    """
    if a >= b:
        raise ValueError("積分下限 a 必須小於上限 b。")

    # 每個小區間的寬度
    delta_x = (b - a) / N
    
    # 初始化總和
    total_sum = 0
    
    # 遍歷每個小區間
    for i in range(N):
        x0 = a + i * delta_x
        x1 = a + (i + 1) * delta_x
        
        # 計算 f(x)g(x) 在兩端的數值
        y0 = f(x0) * g(x0)
        y1 = f(x1) * g(x1)
        
        # 梯形的面積
        trapezoid_area = (y0 + y1) / 2 * delta_x
        
        # 累加到總和
        total_sum += trapezoid_area
        
    return total_sum

# --- 範例 ---
import math

# 範例 1: 計算 f(x) = x^2 和 g(x) = x+1 在區間 [0, 1] 上的內積
# 準確答案是 7/12 (約 0.58333)
def f1(x):
    return x**2

def g1(x):
    return x + 1

a1, b1 = 0, 1
inner_product_1 = fdot_numerical(f1, g1, a1, b1)
print(f"範例 1: f(x) = x^2, g(x) = x+1, 區間為 [{a1}, {b1}]")
print(f"數值內積近似值 = {inner_product_1}")
print("-" * 30)


# 範例 2: 驗證 sin(x) 和 cos(x) 在區間 [-pi, pi] 上的正交性
# 準確答案是 0
def f2(x):
    return math.sin(x)

def g2(x):
    return math.cos(x)

a2, b2 = -math.pi, math.pi
inner_product_2 = fdot_numerical(f2, g2, a2, b2, N=10000) # 增加 N 以提高精確度
print(f"範例 2: f(x) = sin(x), g(x) = cos(x), 區間為 [{a2:.4f}, {b2:.4f}]")
print(f"數值內積近似值 = {inner_product_2}")
print("-" * 30)

# 範例 3: 驗證 sin(2x) 和 sin(3x) 在 [-pi, pi] 上的正交性
# 準確答案是 0
def f3(x):
    return math.sin(2 * x)

def g3(x):
    return math.sin(3 * x)

a3, b3 = -math.pi, math.pi
inner_product_3 = fdot_numerical(f3, g3, a3, b3, N=10000)
print(f"範例 3: f(x) = sin(2x), g(x) = sin(3x), 區間為 [{a3:.4f}, {b3:.4f}]")
print(f"數值內積近似值 = {inner_product_3}")
print("-" * 30)