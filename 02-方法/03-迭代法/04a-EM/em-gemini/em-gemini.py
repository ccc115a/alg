import numpy as np

def em_coin_toss(observations, p_A_initial, p_B_initial, max_iterations=100, tolerance=1e-4):
    """
    使用 EM 算法估計兩枚硬幣 A 和 B 的正面朝上概率 (p_A, p_B)。

    參數:
        observations (np.array): 觀測數據，形狀為 (N, 2)，其中 N 是實驗組數，
                                   每行是 [正面次數, 反面次數]。
        p_A_initial (float): 硬幣 A 正面概率的初始猜測值。
        p_B_initial (float): 硬幣 B 正面概率的初始猜測值。
        max_iterations (int): 最大迭代次數。
        tolerance (float): 判斷收斂的閾值。

    回傳:
        tuple: (p_A, p_B) 的最終估計值。
    """
    
    # 參數初始化
    # thetas[0] 是硬幣 A 的參數 [p_A, 1-p_A]
    # thetas[1] 是硬幣 B 的參數 [p_B, 1-p_B]
    thetas = np.array([
        [p_A_initial, 1.0 - p_A_initial],
        [p_B_initial, 1.0 - p_B_initial]
    ])
    
    # 總投擲次數 (每組實驗 10 次)
    num_flips_per_trial = observations.sum(axis=1)[0]
    
    # 用來檢查收斂
    log_likelihood_old = -np.inf

    print(f"--- EM 算法開始 ---")
    print(f"初始參數: p_A = {thetas[0, 0]:.4f}, p_B = {thetas[1, 0]:.4f}")

    for i in range(max_iterations):
        p_A_old = thetas[0, 0]
        p_B_old = thetas[1, 0]
        
        # ----------------------------------------------------
        # E 步驟 (Expectation Step) - 計算責任度 (Responsibility)
        # ----------------------------------------------------
        
        # 1. 計算每組觀測數據由硬幣 A/B 產生的「似然值」 (Binomial PMF)
        # log_likelihood_A[k] = log( P(Data_k | Coin A) )
        # log_likelihood_B[k] = log( P(Data_k | Coin B) )
        # 這裡的計算省略了二項分佈的組合數 C(n, k)，因為它在比較 A 和 B 時會被約掉。
        # log(P(k|p)) = k * log(p) + (n-k) * log(1-p)
        log_likelihood_A = observations[:, 0] * np.log(p_A_old) + observations[:, 1] * np.log(1.0 - p_A_old)
        log_likelihood_B = observations[:, 0] * np.log(p_B_old) + observations[:, 1] * np.log(1.0 - p_B_old)
        
        # 2. 轉換回概率並計算「責任度」(後驗概率)
        # p_i_A ∝ P(Data_i | A) * P(A)
        # p_i_B ∝ P(Data_i | B) * P(B)
        # 這裡假設 P(A) = P(B) = 0.5 (選擇兩枚硬幣的概率相等)
        # 因此，責任度 w_A = P(A | Data) = P(Data | A) / (P(Data | A) + P(Data | B))
        
        likelihood_A = np.exp(log_likelihood_A)
        likelihood_B = np.exp(log_likelihood_B)
        
        sum_likelihood = likelihood_A + likelihood_B
        
        # w_A: 每組實驗由 A 硬幣產生的概率 (責任度)
        w_A = likelihood_A / sum_likelihood
        # w_B: 每組實驗由 B 硬幣產生的概率 (責任度)
        w_B = likelihood_B / sum_likelihood
        
        # ----------------------------------------------------
        # M 步驟 (Maximization Step) - 更新參數
        # ----------------------------------------------------
        
        # 3. 計算 A 和 B 硬幣的「加權正面總數」(期望正面次數)
        # v_A[0]: A 硬幣的正面期望次數 (加權總和)
        # v_A[1]: A 硬幣的反面期望次數 (加權總和)
        # v_A = w_A * [Heads, Tails]
        v_A = w_A[:, None] * observations
        v_B = w_B[:, None] * observations
        
        # 4. 更新參數 (新的最大似然估計)
        # p_A = A 硬幣的總正面期望次數 / A 硬幣的總投擲期望次數
        # np.sum(v_A, axis=0) 是 (總正面期望次數, 總反面期望次數)
        thetas[0] = np.sum(v_A, axis=0) / np.sum(v_A)
        thetas[1] = np.sum(v_B, axis=0) / np.sum(v_B)
        
        p_A_new = thetas[0, 0]
        p_B_new = thetas[1, 0]
        
        # ----------------------------------------------------
        # 檢查收斂 (可選步驟，用於判斷是否停止疊代)
        # ----------------------------------------------------
        
        # 計算不完全數據的對數似然值 L(theta|X) = log( sum_Z P(X, Z|theta) )
        # log_likelihood_new = sum( log( P(Data | A)P(A) + P(Data | B)P(B) ) )
        log_likelihood_new = np.sum(np.log(likelihood_A * 0.5 + likelihood_B * 0.5))

        print(f"迭代 {i+1}: p_A = {p_A_new:.4f}, p_B = {p_B_new:.4f}, Log Likelihood = {log_likelihood_new:.2f}")

        if abs(log_likelihood_new - log_likelihood_old) < tolerance:
            print("達到收斂，停止迭代。")
            break
        
        log_likelihood_old = log_likelihood_new

    return thetas[0, 0], thetas[1, 0]

# --- 數據準備 ---
# 觀測數據：[正面次數, 反面次數]
data = np.array([
    [5, 5],
    [9, 1],
    [8, 2],
    [4, 6],
    [7, 3]
])

# --- 執行 EM 算法 ---
# 使用您例子中提供的初始猜測值
p_A_initial = 0.6
p_B_initial = 0.5

final_p_A, final_p_B = em_coin_toss(data, p_A_initial, p_B_initial)

# --- 輸出結果 ---
print("\n--- 最終結果 ---")
print(f"硬幣 A 正面概率最終估計值 (p_A): {final_p_A:.4f}")
print(f"硬幣 B 正面概率最終估計值 (p_B): {final_p_B:.4f}")