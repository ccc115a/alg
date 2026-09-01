import numpy as np

def entropy(p):
    """
    計算離散機率分佈的熵 (Entropy)。
    公式：H(P) = -sum(p_i * log2(p_i))
    """
    p = p[p > 0]
    return -np.sum(p * np.log2(p))

def cross_entropy(p, q):
    """
    計算兩個機率分佈之間的交叉熵 (Cross-Entropy)。
    公式：H(P, Q) = -sum(p_i * log2(q_i))
    """
    indices = np.where((p > 0) & (q > 0))
    p_valid = p[indices]
    q_valid = q[indices]
    
    return -np.sum(p_valid * np.log2(q_valid))

def kl_divergence(p, q):
    """
    計算兩個機率分佈之間的 KL 散度 (Kullback-Leibler Divergence)。
    公式：D_KL(P || Q) = sum(p_i * log2(p_i / q_i))
    """
    return cross_entropy(p, q) - entropy(p)

def mutual_information(p_xy):
    """
    計算兩個隨機變數之間的互信息 (Mutual Information)。
    公式：I(X; Y) = sum_x sum_y p(x, y) * log2(p(x, y) / (p(x) * p(y)))
    """
    p_x = np.sum(p_xy, axis=1, keepdims=True)
    p_y = np.sum(p_xy, axis=0, keepdims=True)
    
    p_x_p_y = p_x * p_y
    
    p_xy_valid = p_xy[p_xy > 0]
    p_x_p_y_valid = p_x_p_y[p_xy > 0]
    
    return np.sum(p_xy_valid * np.log2(p_xy_valid / p_x_p_y_valid))

# --- 範例應用 ---
if __name__ == "__main__":
    # 1. 熵 (Entropy) 範例
    print("--- 1. 熵 (Entropy) ---")
    p1 = np.array([0.5, 0.5])
    h1 = entropy(p1)
    print(f"p = {p1} 的熵：{h1:.4f}")
    
    print("\n" + "="*40 + "\n")
    
    # 2. 交叉熵 (Cross-Entropy) 範例
    print("--- 2. 交叉熵 (Cross-Entropy) ---")
    p_true = np.array([0.6, 0.4])
    q_pred1 = np.array([0.5, 0.5])
    ce1 = cross_entropy(p_true, q_pred1)
    print(f"p = {p_true}, q = {q_pred1} 的交叉熵：{ce1:.4f}")
    
    print("\n" + "="*40 + "\n")
    
    # 3. KL 散度 (KL Divergence) 範例
    print("--- 3. KL 散度 (KL Divergence) ---")
    d_kl_1 = kl_divergence(p_true, q_pred1)
    print(f"P || Q 的 KL 散度：{d_kl_1:.4f}")
    
    print("\n" + "="*40 + "\n")

    # 4. 互信息 (Mutual Information) 範例
    print("--- 4. 互信息 (Mutual Information) ---")
    p_xy_dependent = np.array([[0.25, 0.25], [0.25, 0.25]])
    mi1 = mutual_information(p_xy_dependent)
    print(f"聯合分佈：\n{p_xy_dependent}")
    print(f"互信息：{mi1:.4f}")