import numpy as np
from scipy import stats

# 假設的母體平均數 (來自虛無假設)
mu_0 = 50

# 樣本數據
sample_data = np.array([48.5, 49.2, 51.0, 47.8, 50.1, 46.5, 49.8, 52.3, 47.0, 48.9,
                        49.5, 48.0, 50.5, 47.5, 51.5, 48.8, 49.3, 50.8, 47.2, 49.9,
                        51.1, 48.2, 50.2, 46.8, 49.6, 50.6, 47.7, 48.7, 51.2, 49.7,
                        48.1, 49.4, 50.3, 46.7, 50.9, 47.3, 48.6, 51.3, 47.9, 49.1])

# --- 1. 計算樣本統計量 ---
sample_mean = np.mean(sample_data)
sample_std = np.std(sample_data, ddof=1)  # ddof=1 計算樣本標準差
n = len(sample_data)

print(f"樣本平均值 (x̄): {sample_mean:.2f}")
print(f"樣本標準差 (s): {sample_std:.2f}")
print(f"樣本大小 (n): {n}")
print("-" * 30)

# --- 2. 進行 t 檢定 ---
# ttest_1samp 函數會自動計算 t 統計量和 P 值
t_statistic, p_value = stats.ttest_1samp(sample_data, popmean=mu_0)

# --- 3. 輸出結果 ---
print(f"t 統計量 (t-statistic): {t_statistic:.4f}")
print(f"P 值 (P-value): {p_value:.4f}")
print("-" * 30)

# --- 4. 做出決策 ---
alpha = 0.05
print(f"顯著水準 (α): {alpha}")

if p_value < alpha:
    print("結論：由於 P 值 < α，我們拒絕虛無假設。")
    print("有足夠證據證明這批電池的平均壽命與 50 小時有顯著差異。")
else:
    print("結論：由於 P 值 ≥ α，我們不拒絕虛無假設。")
    print("沒有足夠證據證明這批電池的平均壽命與 50 小時有顯著差異。")