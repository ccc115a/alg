import numpy as np

# =====================================================================
# 1. 核心通用迭代框架 (Core Abstract Framework)
# =====================================================================
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
        state = next_state
    return state, max_iter


# =====================================================================
# 2. Hopfield 網絡 (聯想記憶 / 狀態檢索)
# =====================================================================
def demo_hopfield_network():
    print("--- Hopfield 網絡 (確定性狀態推進 & 能量極小化) ---")
    
    # 1. 定義要記憶的特徵圖案 (例如：10 維的 0/1 或 -1/+1 向量)
    pattern1 = np.array([ 1,  1,  1,  1,  1, -1, -1, -1, -1, -1])
    pattern2 = np.array([-1, -1, -1,  1,  1,  1,  1, -1, -1, -1])
    
    # 2. 利用 Hebbian 學習律建立對稱權重矩陣 W (W_ii = 0)
    n = len(pattern1)
    W = (np.outer(pattern1, pattern1) + np.outer(pattern2, pattern2)) / n
    np.fill_diagonal(W, 0.0)
    
    # 3. 狀態推進函數：根據鄰居節點的加權和與符號函數更新狀態
    def transition(s):
        raw_activation = np.dot(W, s)
        # 若加權和為 0 則保持原狀，否則取 sign (+1 / -1)
        next_s = np.where(raw_activation == 0, s, np.sign(raw_activation))
        return next_s

    # 4. 判定條件：狀態完全穩定（不動點 Fixed Point）
    converged = lambda old, new, i: np.array_equal(old, new)
    
    # 5. 給定一個帶有雜訊的破損 pattern1 進入系統進行檢索
    corrupted_input = pattern1.copy()
    corrupted_input[0] = -1  # 故意破壞第一個節點
    corrupted_input[1] = -1  # 故意破壞第二個節點
    
    print(f"輸入的破損圖案 : {corrupted_input}")
    restored_state, iters = generic_iterator(transition, converged, initial_state=corrupted_input)
    print(f"修復後的記憶圖案 : {restored_state} (耗時 {iters} 次迭代)")
    print(f"是否完美還原記憶 : {np.array_equal(restored_state, pattern1)}\n")


# =====================================================================
# 3. 受限玻爾茲曼機 RBM (CD-k 採樣迭代)
# =====================================================================
def demo_rbm_contrastive_divergence():
    print("--- 受限玻爾茲曼機 RBM (CD-k 馬爾可夫鏈採樣迭代) ---")
    
    sigmoid = lambda x: 1.0 / (1.0 + np.exp(-x))
    
    n_visible = 6
    n_hidden = 3
    k_steps = 5  # CD-k 採樣步數
    
    np.random.seed(42)
    W = np.random.randn(n_hidden, n_visible) * 0.1
    b_v = np.zeros(n_visible)
    b_h = np.zeros(n_hidden)
    
    # 輸入特徵資料 (例如 2 個訓練樣本)
    v_data = np.array([
        [1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1]
    ])
    
    # 定義 CD-k 採樣推進函數：進行 1 步 v -> h -> v 的交替吉布斯採樣
    def cd1_step(state):
        v, h = state
        # v -> h
        p_h = sigmoid(np.dot(v, W.T) + b_h)
        h_sample = (p_h > np.random.rand(*p_h.shape)).astype(float)
        # h -> v
        p_v = sigmoid(np.dot(h_sample, W) + b_v)
        v_sample = (p_v > np.random.rand(*p_v.shape)).astype(float)
        return (v_sample, h_sample)

    # 判定條件：完成 k 步 MCMC 採樣迭代
    converged = lambda old, new, i: i >= k_steps - 1
    
    # 初始化狀態：用真實資料 v_data 採樣第一個 h
    p_h0 = sigmoid(np.dot(v_data, W.T) + b_h)
    h0 = (p_h0 > np.random.rand(*p_h0.shape)).astype(float)
    
    (v_k, h_k), iters = generic_iterator(cd1_step, converged, initial_state=(v_data, h0))
    
    print(f"原始資料 v_0      : \n{v_data}")
    print(f"CD-{k_steps} 重建資料 v_k : \n{v_k.astype(int)} (完成 {iters} 步吉布斯採樣迭代)\n")


# =====================================================================
# 執行
# =====================================================================
if __name__ == "__main__":
    demo_hopfield_network()
    demo_rbm_contrastive_divergence()