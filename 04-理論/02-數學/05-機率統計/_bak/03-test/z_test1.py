import numpy as np
from scipy import stats

# 1. 數據與已知參數準備
# 模擬一個大樣本的新版網頁用戶停留時間數據 (n=50)
np.random.seed(42)  # 設定隨機種子以確保結果可重現
# 假設新設計略微提升了平均值到 125 秒
new_design_times = np.random.normal(loc=125, scale=28, size=50) 

# Z 檢定所需參數：
X_bar = new_design_times.mean()  # 樣本平均數
n = len(new_design_times)        # 樣本大小 (n=50, 視為大樣本)
mu_0 = 120                       # 虛無假設下的母體平均數 (歷史平均)
sigma = 25                       # **已知**的母體標準差 (歷史標準差)

# 2. 手動計算 Z 統計量
# 標準誤 (Standard Error of the Mean, SE)
SE = sigma / np.sqrt(n)

# Z 統計量公式: Z = (X_bar - mu_0) / SE
Z_stat = (X_bar - mu_0) / SE

# 3. 計算 P 值
# 由於 Z 統計量服從標準常態分佈 N(0, 1)，我們使用 stats.norm
# 這是單尾檢定 (Ha: >)，我們計算 P(Z > Z_stat)。
# stats.norm.sf(Z_stat) = 1 - stats.norm.cdf(Z_stat)
p_value_one_sided = stats.norm.sf(Z_stat)

# 4. 輸出結果
alpha = 0.05
print("--- 單樣本 Z 檢定 (One-Sample Z-Test) ---")
print(f"樣本大小 (n): {n}")
print(f"已知母體標準差 (sigma): {sigma:.2f} 秒")
print(f"新版網頁平均停留時間 (X_bar): {X_bar:.2f} 秒")
print(f"虛無假設平均值 (mu_0): {mu_0} 秒")
print("-" * 45)
print(f"標準誤 (SE): {SE:.4f}")
print(f"Z 統計量: {Z_stat:.4f}")
print(f"單尾 P 值 (Ha: > 120): {p_value_one_sided:.4f}")
print("-" * 45)

if p_value_one_sided < alpha:
    print("結論：**拒絕 H0**。新網站的平均停留時間顯著高於 120 秒。")
else:
    print("結論：**無法拒絕 H0**。沒有足夠證據顯示新網站平均停留時間更高。")