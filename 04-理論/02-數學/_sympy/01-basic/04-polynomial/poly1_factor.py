# 範例 1：展開與因式分解
from sympy import symbols, expand, factor

def main():
    # 1. 定義符號
    x, y = symbols('x y')

    # 2. 定義一個多項式表達式 (x + 2y)^3
    expr = (x + 2*y)**3
    print(f"原始表達式: {expr}")

    # 3. 展開多項式 (Expand)
    expanded_expr = expand(expr)
    print(f"展開後: {expanded_expr}")

    # 4. 因式分解 (Factor)
    # 我們試著分解一個較複雜的式子: x^3 - y^3
    expr2 = x**3 - y**3
    factored_expr = factor(expr2)
    print(f"\n原始表達式 2: {expr2}")
    print(f"因式分解後: {factored_expr}")

if __name__ == "__main__":
    main()