import numpy as np
from scipy import stats

# 假設兩組廣告策略帶來的銷售額數據
# 廣告 A 的數據
ad_A_sales = np.array([120, 150, 130, 160, 145, 135, 155, 125, 140, 165, 150, 130, 125, 140, 155])

# 廣告 B 的數據
ad_B_sales = np.array([110, 125, 105, 135, 115, 120, 130, 100, 115, 125, 110, 105, 120, 115, 130])

# --- 1. 設定假設 ---
# 虛無假設 (H0): 兩組的平均銷售額相等 (μA = μB)
# 對立假設 (Ha): 兩組的平均銷售額不相等 (μA ≠ μB)

# --- 2. 進行 t 檢定 ---
# ttest_ind() 函數會自動計算 t 統計量和 P 值
# equal_var=True 假設兩組母體變異數相等 (這是默認值)
# equal_var=False 則不假設變異數相等 (稱為 Welch's t-test)
# 我們這裡假設變異數不一定相等，因此設定 equal_var=False
t_statistic, p_value = stats.ttest_ind(ad_A_sales, ad_B_sales, equal_var=False)

# --- 3. 輸出結果 ---
print(f"廣告 A 的樣本平均數: {ad_A_sales.mean():.2f}")
print(f"廣告 B 的樣本平均數: {ad_B_sales.mean():.2f}")
print("-" * 40)
print(f"t 統計量 (t-statistic): {t_statistic:.4f}")
print(f"P 值 (P-value): {p_value:.4f}")
print("-" * 40)

# --- 4. 做出決策 ---
alpha = 0.05  # 設定顯著水準
print(f"顯著水準 (α): {alpha}")

if p_value < alpha:
    print("結論：由於 P 值 < α，我們拒絕虛無假設。")
    print("有足夠證據證明兩種廣告策略的平均銷售額有顯著差異。")
else:
    print("結論：由於 P 值 ≥ α，我們不拒絕虛無假設。")
    print("沒有足夠證據證明兩種廣告策略的平均銷售額有顯著差異。")