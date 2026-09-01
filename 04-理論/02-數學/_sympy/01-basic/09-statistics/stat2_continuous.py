# stats2_continuous.py
from sympy.stats import Normal, P, E, density, std
from sympy import symbols, simplify, pprint

def main():
    # 1. 定義標準常態分佈 N(0, 1)
    # Normal(name, mean, std_dev)
    Z = Normal('Z', 0, 1)
    
    # 定義一個變數 z 用來顯示函數圖形
    z = symbols('z')

    # 2. 獲取機率密度函數 (PDF)
    pdf = density(Z)(z)
    print("標準常態分佈的 PDF:")
    pprint(pdf)

    # 3. 計算機率
    # P(Z > 1)
    prob_gt_1 = P(Z > 1)
    print(f"\nP(Z > 1) 的符號解: {prob_gt_1}")
    print(f"P(Z > 1) 的數值解: {prob_gt_1.evalf()}")

    # 4. 帶有符號參數的分佈
    # 定義平均數 mu 和標準差 sigma 為符號
    mu, sigma = symbols('mu sigma', positive=True)
    X = Normal('X', mu, sigma)
    
    print(f"\n符號化期望值 E(X): {E(X)}")
    
    # 計算 P(X > mu) -> 應該要是 1/2
    print(f"P(X > mu): {P(X > mu)}")

if __name__ == "__main__":
    main()