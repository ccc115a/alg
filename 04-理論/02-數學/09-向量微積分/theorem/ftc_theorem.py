import sympy as sp

def verify_ftc_part1():
    """
    驗證微積分基本定理第一部分:
    d/dx [ ∫(a to x) f(t) dt ] = f(x)
    說明: 累積函數的瞬時變化率就是當下的函數值。
    """
    print("=== 驗證 FTC 第一部分: 積分的微分 ===")
    
    # 1. 定義符號
    x, t, a = sp.symbols('x t a')
    
    # 2. 定義一個函數 f(t)
    # 我們選一個稍微複雜一點的函數來測試，例如: f(t) = t * sin(t)
    f_t = t * sp.sin(t)
    print(f"原始函數 f(t): {f_t}")

    # 3. 定義累積函數 g(x) = ∫(a to x) f(t) dt
    # 讓 SymPy 執行積分運算
    g_x = sp.integrate(f_t, (t, a, x))
    print(f"累積函數 g(x) (積分結果): {g_x}")

    # 4. 對 g(x) 進行微分: g'(x)
    dg_dx = sp.diff(g_x, x)
    
    # 這裡通常需要簡化 (simplify) 才能看出它等於 f(x)
    # 因為 f(t) 用的是變數 t，比較時我們把 t 換成 x
    f_x = f_t.subs(t, x)
    
    print(f"g(x) 的導數 g'(x): {dg_dx}")
    print(f"原始函數 f(x):       {f_x}")

    # 5. 驗證
    if sp.simplify(dg_dx - f_x) == 0:
        print("✅ 驗證成功！ d/dx (∫ f(t) dt) = f(x)")
    else:
        print("❌ 驗證失敗。")
    print("-" * 40)


def verify_ftc_part2():
    """
    驗證微積分基本定理第二部分 (牛頓-萊布尼茨公式):
    ∫(a to b) f(x) dx = F(b) - F(a)
    其中 F'(x) = f(x)
    """
    print("=== 驗證 FTC 第二部分: 定積分計算 ===")

    # 1. 定義符號
    x, a, b = sp.symbols('x a b')
    
    # 2. 定義函數 f(x)
    # 例如: f(x) = 3x^2 + 2x
    f_x = 3*x**2 + 2*x
    print(f"被積函數 f(x): {f_x}")

    # 3. 計算左邊 (LHS): 直接運算定積分
    lhs = sp.integrate(f_x, (x, a, b))
    print(f"左邊 (定積分結果): {lhs}")

    # 4. 計算右邊 (RHS): F(b) - F(a)
    # 先求不定積分 (反導數) F(x)
    F_x = sp.integrate(f_x, x)
    print(f"反導數 F(x): {F_x}")
    
    # 代入端點計算差值
    rhs = F_x.subs(x, b) - F_x.subs(x, a)
    print(f"右邊 (F(b) - F(a)): {rhs}")

    # 5. 驗證
    # 使用 simplify 確保代數形式一致
    if sp.simplify(lhs - rhs) == 0:
        print("✅ 驗證成功！ 定積分等於反導數之差。")
    else:
        print("❌ 驗證失敗。")
    print("-" * 40)

if __name__ == "__main__":
    verify_ftc_part1()
    verify_ftc_part2()