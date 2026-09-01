import cmath
import math

def verify_euler_formula(x_value, tolerance=1e-9):
    """
    使用數值方法驗證歐拉公式 e^(ix) = cos(x) + i*sin(x)。

    參數:
    x_value: 要驗證的實數值。
    tolerance: 比較時允許的誤差值。

    回傳:
    如果驗證成功，回傳 True；否則回傳 False。
    """
    # 計算等號左邊：e^(ix)
    lhs = cmath.exp(1j * x_value)

    # 計算等號右邊：cos(x) + i*sin(x)
    rhs = cmath.cos(x_value) + 1j * cmath.sin(x_value)
    
    # 計算兩者差值的絕對值
    difference = abs(lhs - rhs)
    
    print(f"--- 驗證 x = {x_value:.4f} ---")
    print(f"左邊 (e^(i*{x_value:.4f})) 的值為: {lhs.real:.10f} + {lhs.imag:.10f}j")
    print(f"右邊 (cos({x_value:.4f}) + i*sin({x_value:.4f})) 的值為: {rhs.real:.10f} + {rhs.imag:.10f}j")
    print(f"兩者差值的絕對值為: {difference:.15f}")
    
    # 判斷差值是否在容許誤差範圍內
    return difference < tolerance

# --- 範例驗證 ---
# 驗證幾個常見的 x 值

# 範例 1: x = 0
x1 = 0
result1 = verify_euler_formula(x1)
print(f"驗證結果: {'成功' if result1 else '失敗'}")
print("-" * 40)

# 範例 2: x = pi (歐拉恆等式)
# 這是最著名的歐拉公式特例：e^(i*pi) = -1
x2 = math.pi
result2 = verify_euler_formula(x2)
print(f"驗證結果: {'成功' if result2 else '失敗'}")
print("-" * 40)

# 範例 3: x = pi / 2
x3 = math.pi / 2
result3 = verify_euler_formula(x3)
print(f"驗證結果: {'成功' if result3 else '失敗'}")
print("-" * 40)

# 範例 4: x = 1 (任意實數)
x4 = 1
result4 = verify_euler_formula(x4)
print(f"驗證結果: {'成功' if result4 else '失敗'}")
print("-" * 40)