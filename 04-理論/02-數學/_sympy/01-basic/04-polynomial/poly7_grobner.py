# 範例 7：計算格羅布納基 (Gröbner Basis)
from sympy import symbols, groebner

def main():
    # 1. 定義符號
    x, y, z = symbols('x y z')

    # 2. 定義一組多項式方程 (F)
    # 這裡使用一個簡單的循環系統例子
    polys = [
        x + y + z,
        x*y + y*z + z*x,
        x*y*z - 1
    ]
    
    print("多項式系統:")
    for p in polys:
        print(f"  {p}")

    # 3. 計算 Gröbner Basis
    # 這裡使用 lex (lexicographic) 排序，這是解方程最常用的排序
    gb = groebner(polys, x, y, z, order='lex')

    print("\nGröbner Basis (lex order):")
    for g in gb:
        print(f"  {g}")

    # 結果解讀：
    # 最後一個式子通常只包含最後一個變數 (z)，
    # 這讓我們可以解出 z，然後代回求 y，再求 x。

if __name__ == "__main__":
    main()