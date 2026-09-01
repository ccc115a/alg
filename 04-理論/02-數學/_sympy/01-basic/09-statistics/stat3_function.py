# stats3_operations.py
from sympy.stats import Normal, E, variance, density
from sympy import symbols, simplify, pprint

def main():
    # 定義兩個獨立的常態分佈
    # X ~ N(0, 1)
    # Y ~ N(0, 1)
    X = Normal('X', 0, 1)
    Y = Normal('Y', 0, 1)

    # 1. 隨機變數的加法
    # Z = X + Y
    # 理論上 Z 應該也是常態分佈，平均 0，變異數 1+1=2
    Z = X + Y

    print(f"Z = X + Y 的期望值: {E(Z)}")
    print(f"Z = X + Y 的變異數: {variance(Z)}")

    # 2. 查看 Z 的 PDF
    z = symbols('z')
    z_pdf = density(Z)(z)
    print("\nZ = X + Y 的機率密度函數 (化簡後):")
    pprint(simplify(z_pdf))
    
    # 3. 更複雜的運算 V = X^2 (卡方分佈的特例)
    V = X**2
    print(f"\nV = X^2 的期望值: {E(V)}")

if __name__ == "__main__":
    main()