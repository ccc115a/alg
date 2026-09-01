import numpy as np
from scipy import stats

# 假設的學生考試成績數據 (10 名學生)
# 成績單位：分

# 新教學法前的成績 (Before)
scores_before = np.array([75, 80, 68, 92, 70, 85, 78, 95, 65, 88])

# 新教學法後的成績 (After)
scores_after = np.array([80, 85, 75, 95, 72, 88, 80, 98, 70, 90])

# --- 1. 設定假設 ---
# 虛無假設 (H0): 教學法前後的平均成績**沒有**顯著差異 (μ_diff = 0)
# 對立假設 (Ha): 教學法前後的平均成績**有**顯著差異 (μ_diff ≠ 0)

# --- 2. 進行配對樣本 t 檢定 ---
# stats.ttest_rel() 函數用於配對 (相關) 樣本 t 檢定
t_statistic, p_value = stats.ttest_rel(scores_after, scores_before)

# --- 3. 輸出樣本統計量 ---
print("--- 原始數據平均數 ---")
print(f"新教學法前平均成績: {scores_before.mean():.2f}")
print(f"新教學法後平均成績: {scores_after.mean():.2f}")

# 計算差異的平均數和標準差 (t 檢定實質上檢定的是這個差異)
difference = scores_after - scores_before
print(f"差異值平均數 (x̄_diff): {difference.mean():.2f}")
print(f"差異值標準差 (s_diff): {np.std(difference, ddof=1):.2f}")
print("-" * 35)

# --- 4. 輸出檢定結果 ---
print(f"t 統計量 (t-statistic): {t_statistic:.4f}")
print(f"P 值 (P-value): {p_value:.4f}")
print(f"自由度 (df): {len(scores_before) - 1}")
print("-" * 35)

# --- 5. 做出決策 ---
alpha = 0.05  # 設定顯著水準
print(f"顯著水準 (α): {alpha}")

if p_value < alpha:
    print("結論：由於 P 值 < α，我們拒絕虛無假設。")
    print("有足夠證據證明新教學法**顯著改變了**學生的平均成績。")
else:
    print("結論：由於 P 值 ≥ α，我們不拒絕虛無假設。")
    print("沒有足夠證據證明新教學法顯著改變了學生的平均成績。")