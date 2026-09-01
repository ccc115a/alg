import numpy as np
from scipy.stats import norm

# --- 1. 設定假設與參數 ---

# 虛無假設 H0: 母體平均壽命 (μ) = 50 小時
mu_0 = 50

# 樣本數據
sample_mean = 48.5  # 樣本平均數 (x̄)
n = 40              # 樣本大小 (n)

# 母體參數
sigma = 5           # 母體標準差 (σ)
alpha = 0.05        # 顯著水準 (α)

# --- 2. 計算 Z 統計量 ---

# 計算標準誤 (standard error)
standard_error = sigma / np.sqrt(n)
print(f"母體標準差 (σ): {sigma}")
print(f"樣本大小 (n): {n}")
print(f"標準誤 (Standard Error): {standard_error:.4f}")
print("-" * 30)

# 計算 Z 統計量
z_statistic = (sample_mean - mu_0) / standard_error
print(f"樣本平均壽命 (x̄): {sample_mean}")
print(f"假設母體平均壽命 (μ): {mu_0}")
print(f"Z 統計量 (Z-statistic): {z_statistic:.4f}")
print("-" * 30)


# --- 3. 計算 P 值 (雙尾檢定) ---

# 計算單尾 P 值：P(Z < -1.897)
# 我們使用 norm.cdf() 來計算累積機率
p_value_one_tailed = norm.cdf(z_statistic)

# 因為是雙尾檢定（判斷「不等於」），所以要將單尾 P 值乘以 2
p_value_two_tailed = p_value_one_tailed * 2
print(f"單尾 P 值 (one-tailed P-value): {p_value_one_tailed:.4f}")
print(f"雙尾 P 值 (two-tailed P-value): {p_value_two_tailed:.4f}")
print("-" * 30)


# --- 4. 做出決策 ---

print(f"顯著水準 (α): {alpha}")
if p_value_two_tailed <= alpha:
    print("結論: 由於 P 值 ≤ α，我們拒絕虛無假設。")
    print("有足夠證據證明這批電池的平均壽命與 50 小時有顯著差異。")
else:
    print("結論: 由於 P 值 > α，我們不拒絕虛無假設。")
    print("沒有足夠證據證明這批電池的平均壽命與 50 小時有顯著差異。")