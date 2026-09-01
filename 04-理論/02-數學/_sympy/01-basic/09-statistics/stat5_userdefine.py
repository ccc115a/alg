# stats5_custom.py
from sympy.stats import FiniteRV, P, E, density
from sympy import S

def main():
    # 定義一個有限隨機變數 (Finite Random Variable)
    # 格式: {結果: 機率}
    # 假設一個不公正的硬幣 (Unfair Coin) 或自訂骰子
    # 1 出現機率 0.1
    # 2 出現機率 0.2
    # 3 出現機率 0.7
    density_dict = {1: 0.1, 2: 0.2, 3: 0.7}
    
    X = FiniteRV('X', density_dict)

    print("自定義分佈:")
    print(density(X).dict)

    print(f"\n期望值 E(X): {E(X)}")
    # E = 1*0.1 + 2*0.2 + 3*0.7 = 0.1 + 0.4 + 2.1 = 2.6
    
    print(f"P(X >= 2): {P(X >= 2)}")
    # P = 0.2 + 0.7 = 0.9

    # 也可以進行採樣 (Sampling)
    # 注意：採樣需要依賴外部庫(如 numpy/scipy) 或 sympy 內建隨機生成
    from sympy.stats import sample
    print(f"\n隨機採樣 5 次: {[sample(X) for _ in range(5)]}")

if __name__ == "__main__":
    main()