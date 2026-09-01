# 範例 2：多項式除法
from sympy import symbols, div, expand

def main():
    # 1. 定義符號
    x = symbols('x')

    # 2. 定義被除式 f(x) 和除式 g(x)
    # f(x) = x^3 + 2x^2 - x - 2
    # g(x) = x^2 + 2x + 1
    f = x**3 + 2*x**2 - x - 2
    g = x**2 + 2*x + 1

    # 3. 執行除法
    # div 回傳一個 tuple: (商, 餘式)
    q, r = div(f, g)

    print(f"被除式 f(x): {f}")
    print(f"除式 g(x): {g}")
    print(f"商式 q(x): {q}")
    print(f"餘式 r(x): {r}")

    # 4. 驗證結果: f = g * q + r
    check = expand(g * q + r)
    print(f"驗證 (g*q + r): {check}")
    print(f"驗證成功? {check == f}")

if __name__ == "__main__":
    main()