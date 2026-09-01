import numpy as np
import matplotlib.pyplot as plt

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 生成範例資料
np.random.seed(42)
X = np.linspace(0, 10, 50)
y_true = 2.5 * X + 1.5  # 真實的線性關係
y = y_true + np.random.normal(0, 2, size=X.shape)  # 加入雜訊

# 定義均方誤差(MSE)作為目標函數
def mse(X, y, w, b):
    y_pred = w * X + b
    return np.mean((y - y_pred) ** 2)

# 爬山演算法
def hill_climbing(X, y, iterations=1000, step_size=0.01):
    # 初始化參數
    w = np.random.randn()
    b = np.random.randn()
    
    # 記錄歷史
    history = {'w': [w], 'b': [b], 'mse': [mse(X, y, w, b)]}
    
    best_mse = mse(X, y, w, b)
    
    for i in range(iterations):
        # 嘗試四個方向的移動
        candidates = [
            (w + step_size, b),
            (w - step_size, b),
            (w, b + step_size),
            (w, b - step_size)
        ]
        
        # 找出最佳的移動
        best_candidate = None
        for w_new, b_new in candidates:
            new_mse = mse(X, y, w_new, b_new)
            if new_mse < best_mse:
                best_mse = new_mse
                best_candidate = (w_new, b_new)
        
        # 如果找到更好的解，就移動
        if best_candidate:
            w, b = best_candidate
            history['w'].append(w)
            history['b'].append(b)
            history['mse'].append(best_mse)
        else:
            # 沒有更好的解，可能陷入局部最優
            break
    
    return w, b, history

# 執行爬山演算法
w_final, b_final, history = hill_climbing(X, y, iterations=2000, step_size=0.01)

print(f"最終參數: w = {w_final:.4f}, b = {b_final:.4f}")
print(f"最終 MSE: {history['mse'][-1]:.4f}")
print(f"疊代次數: {len(history['mse'])}")

# 繪製結果
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 子圖1: 資料點與擬合直線
axes[0, 0].scatter(X, y, alpha=0.6, label='資料點', color='blue')
axes[0, 0].plot(X, y_true, 'g--', label='真實線性關係', linewidth=2)
axes[0, 0].plot(X, w_final * X + b_final, 'r-', label='爬山演算法擬合', linewidth=2)
axes[0, 0].set_xlabel('X')
axes[0, 0].set_ylabel('y')
axes[0, 0].set_title('線性回歸結果')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 子圖2: MSE 收斂曲線
axes[0, 1].plot(history['mse'], linewidth=2)
axes[0, 1].set_xlabel('疊代次數')
axes[0, 1].set_ylabel('MSE')
axes[0, 1].set_title('均方誤差收斂過程')
axes[0, 1].grid(True, alpha=0.3)

# 子圖3: 參數 w 的變化
axes[1, 0].plot(history['w'], linewidth=2, color='orange')
axes[1, 0].axhline(y=2.5, color='g', linestyle='--', label='真實值 w=2.5')
axes[1, 0].set_xlabel('疊代次數')
axes[1, 0].set_ylabel('權重 w')
axes[1, 0].set_title('權重參數 w 的變化')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# 子圖4: 參數 b 的變化
axes[1, 1].plot(history['b'], linewidth=2, color='purple')
axes[1, 1].axhline(y=1.5, color='g', linestyle='--', label='真實值 b=1.5')
axes[1, 1].set_xlabel('疊代次數')
axes[1, 1].set_ylabel('偏差 b')
axes[1, 1].set_title('偏差參數 b 的變化')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 計算與真實參數的誤差
print(f"\n與真實參數的差異:")
print(f"w 誤差: {abs(w_final - 2.5):.4f}")
print(f"b 誤差: {abs(b_final - 1.5):.4f}")