import numpy as np
from entropy1 import entropy, cross_entropy

# --- 驗證程式碼 ---
if __name__ == "__main__":
    # 1. 定義真實機率分佈 P
    p = np.array([0.7, 0.2, 0.1])
    print(f"真實機率分佈 P = {p}")

    # 2. 計算交叉熵的最小值 H(P, P)
    # 這裡的 H(P, P) 等於 P 的熵 H(P)
    min_cross_entropy = cross_entropy(p, p)
    print(f"交叉熵最小值 (當 Q = P 時)：H(P, P) = {min_cross_entropy:.4f}")
    
    # 驗證它是否等於 P 的熵
    entropy_of_p = entropy(p)
    print(f"P 的熵：H(P) = {entropy_of_p:.4f}")
    print(f"驗證：H(P, P) == H(P) -> {np.isclose(min_cross_entropy, entropy_of_p)}")

    print("\n" + "="*40 + "\n")

    # 3. 定義一個不等於 P 的機率分佈 Q
    # 為了方便觀察，我們將 Q 設為與 P 差異較大的分佈
    q = np.array([0.1, 0.3, 0.6])
    print(f"比較分佈 Q = {q}")

    # 4. 計算 H(P, Q)
    cross_entropy_pq = cross_entropy(p, q)
    print(f"交叉熵 H(P, Q) = {cross_entropy_pq:.4f}")

    # 5. 驗證 H(P, Q) > H(P, P)
    print(f"H(P, Q) > H(P, P)？ -> {cross_entropy_pq > min_cross_entropy}")

    print("\n" + "="*40 + "\n")

    # 6. 多組 Q 的驗證
    print("--- 多組 Q 的驗證 ---")
    p_true = np.array([0.4, 0.6])
    
    # Q1: 接近 P
    q1 = np.array([0.45, 0.55])
    ce1 = cross_entropy(p_true, q1)
    
    # Q2: 遠離 P
    q2 = np.array([0.9, 0.1])
    ce2 = cross_entropy(p_true, q2)
    
    ce_min = cross_entropy(p_true, p_true)
    
    print(f"真實 P = {p_true}")
    print(f"交叉熵最小值 H(P, P) = {ce_min:.4f}")
    print(f"預測 Q1 = {q1}，交叉熵 H(P, Q1) = {ce1:.4f}")
    print(f"預測 Q2 = {q2}，交叉熵 H(P, Q2) = {ce2:.4f}")
    print(f"H(P, Q1) > H(P, P)？ -> {ce1 > ce_min}")
    print(f"H(P, Q2) > H(P, P)？ -> {ce2 > ce_min}")
    print(f"H(P, Q2) > H(P, Q1)？ -> {ce2 > ce1} (Q2 離 P 較遠，交叉熵較大)")