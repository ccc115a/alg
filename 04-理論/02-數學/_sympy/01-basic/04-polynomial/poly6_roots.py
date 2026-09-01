# 範例 6：尋找多項式的根
from sympy import symbols, roots

def main():
    # 1. 定義符號
    x = symbols('x')

    # 2. 定義多項式
    # f(x) = (x - 2)^2 * (x + 3)
    # 展開後是 x^3 - x^2 - 8x + 12
    f = x**3 - x**2 - 8*x + 12
    print(f"多項式: {f}")

    # 3. 計算根
    # roots 回傳一個字典: {根: 重數}
    r = roots(f)
    print(f"根與重數: {r}")

    # 解析輸出
    for root, multiplicity in r.items():
        print(f"  根: {root}, 重數: {multiplicity}")

if __name__ == "__main__":
    main()