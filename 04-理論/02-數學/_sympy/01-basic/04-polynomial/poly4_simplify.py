# 範例 4：有理函數化簡與部分分式分解
from sympy import symbols, cancel, apart

def main():
    # 1. 定義符號
    x = symbols('x')

    # 2. 有理函數約分 (Cancel)
    # (x^2 - 1) / (x + 1) 應該等於 x - 1
    expr1 = (x**2 - 1) / (x + 1)
    canceled_expr = cancel(expr1)
    
    print(f"原始分數: {expr1}")
    print(f"約分後: {canceled_expr}")

    # 3. 部分分式分解 (Partial Fraction Decomposition)
    # 將複雜分數拆解成簡單分數的和
    # 1 / ((x + 2)(x + 1)) -> 1/(x+1) - 1/(x+2)
    expr2 = 1 / ((x + 2) * (x + 1))
    apart_expr = apart(expr2)
    
    print(f"\n原始分數: {expr2}")
    print(f"部分分式分解: {apart_expr}")

if __name__ == "__main__":
    main()