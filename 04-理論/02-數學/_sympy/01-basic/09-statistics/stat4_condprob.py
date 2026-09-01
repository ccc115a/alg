# stat4_condprob.py
from sympy.stats import Die, Normal, P
from sympy import Eq, Or

def main():
    # --- 離散情況 ---
    X = Die('X', 6)
    
    # 計算 P(X > 3 | X 是偶數)
    # 給定 X 是偶數 (2, 4, 6)，X > 3 的機率是多少？ (4, 6 符合，共 2/3)
    
    # 修正重點：
    # 直接使用 Eq(X % 2, 0) 可能會導致求解器錯誤 (ConditionSet error)。
    # 我們改用 Or 明確列出偶數的情況: X=2 或 X=4 或 X=6
    condition_even = Or(Eq(X, 2), Eq(X, 4), Eq(X, 6))
    
    prob_discrete = P(X > 3, condition_even)
    print(f"P(X > 3 | X is even) = {prob_discrete}")

    # --- 連續情況 ---
    Z = Normal('Z', 0, 1)
    
    # 計算 P(Z > 2 | Z > 0)
    # 標準常態分佈，已知大於 0 (右半邊)，其大於 2 的機率
    prob_continuous = P(Z > 2, Z > 0)
    print(f"P(Z > 2 | Z > 0) = {prob_continuous}")
    print(f"數值近似: {prob_continuous.evalf()}")

if __name__ == "__main__":
    main()