# 範例 5：最大公因式 (GCD) 與 最小公倍式 (LCM)
from sympy import symbols, gcd, lcm, expand, factor

def main():
    # 1. 定義符號
    x = symbols('x')

    # 2. 定義兩個多項式
    # f = (x-1)(x+2)
    # g = (x-1)(x+3)
    f = (x - 1) * (x + 2)
    g = (x - 1) * (x + 3)

    # 為了演示，我們先將其展開
    f_expanded = expand(f)
    g_expanded = expand(g)
    
    print(f"多項式 f: {f_expanded}")
    print(f"多項式 g: {g_expanded}")

    # 3. 計算 GCD
    result_gcd = gcd(f_expanded, g_expanded)
    print(f"GCD (最大公因式): {result_gcd}")

    # 4. 計算 LCM
    result_lcm = lcm(f_expanded, g_expanded)
    print(f"LCM (最小公倍式): {factor(result_lcm)}") # 用 factor 讓結果好讀一點

if __name__ == "__main__":
    main()