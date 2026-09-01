# plot4_implicit.py
from sympy import symbols, Eq, And
from sympy.plotting import plot_implicit

def main():
    x, y = symbols('x y')

    # 1. 繪製圓方程式: x^2 + y^2 = 4
    # 使用 Eq(lhs, rhs)
    print("繪製圓方程式 x^2 + y^2 = 4 ...")
    plot_implicit(Eq(x**2 + y**2, 4), (x, -3, 3), (y, -3, 3), title="Circle Implicit")

    # 2. 繪製不等式區域
    # y > x^2
    print("繪製不等式區域 y > x^2 ...")
    plot_implicit(y > x**2, (x, -2, 2), (y, -1, 4), title="Inequality Region")

    # 3. 邏輯組合 (AND)
    # (y > x) AND (y < -x + 2)
    print("繪製邏輯交集區域...")
    plot_implicit(And(y > x, y < -x + 2), title="Logic Region")

if __name__ == "__main__":
    main()