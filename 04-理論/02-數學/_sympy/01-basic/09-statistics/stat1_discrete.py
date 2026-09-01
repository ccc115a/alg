# stat1_discrete.py
from sympy.stats import Die, Coin, P, E, variance, std, density
from sympy import Eq, symbols

def main():
    # 1. 定義隨機變數
    # X 代表一顆 6 面骰子
    X = Die('X', 6)
    
    # Y 代表一枚硬幣
    Y = Coin('Y')

    # 2. 機率計算 P()
    print(f"骰子點數大於 3 的機率 P(X > 3): {P(X > 3)}")
    print(f"骰子點數是偶數的機率 P(Eq(X % 2, 0)): {P(Eq(X % 2, 0))}")

    # --- 修正重點 ---
    # Eq 不能直接接受字串 'H'，必須定義 H 為符號
    H = symbols('H') 
    
    # 計算 Y 等於 H (正面) 的機率
    print(f"硬幣是正面的機率 P(Y = H): {P(Eq(Y, H))}")

    # 3. 期望值 E(), 變異數 variance(), 標準差 std()
    print(f"\n骰子的期望值 E(X): {E(X)}")      # 應該是 3.5 (7/2)
    print(f"骰子的變異數 Var(X): {variance(X)}")
    print(f"骰子的標準差 Std(X): {std(X)}")

    # 4. 機率密度函數 (對於離散變數則是機率質量函數 PMF)
    # density 回傳一個字典物件
    print(f"\n骰子的機率分布: {density(X).dict}")

if __name__ == "__main__":
    main()