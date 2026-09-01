import numpy as np
from scipy import stats

# 1. 準備數據 (新版網頁的用戶停留時間, 單位: 秒)
new_design_times = np.array([125, 130, 118, 135, 122, 140, 128, 133, 129, 131])
pop_mean_h0 = 120  # 舊版網站的已知平均停留時間

# 2. 執行單樣本 t 檢定
# ttest_1samp 默認執行雙尾檢定
t_stat, p_value_two_sided = stats.ttest_1samp(new_design_times, pop_mean_h0)

# 3. 處理單尾檢定
# 由於我們的 Ha 是 >，且 t_stat > 0，我們將 p-value 減半。
if t_stat > 0:
    p_value_one_sided = p_value_two_sided / 2
else:
    # 如果 t_stat < 0，則 p-value 應為 1 - (p_value_two_sided / 2)
    # 但在 Ha: > 的情況下，如果 t 統計量為負，則 p 值會非常大，我們可以直接得出結論。
    p_value_one_sided = 1 - (p_value_two_sided / 2)


# 4. 輸出結果
alpha = 0.05
print("--- 單樣本 t 檢定 (One-Sample t-Test) ---")
print(f"新版平均停留時間: {new_design_times.mean():.2f} 秒")
print(f"虛無假設平均值 (H0): {pop_mean_h0} 秒")
print(f"T 統計量: {t_stat:.4f}")
print(f"單尾 P 值 (Ha: > 120): {p_value_one_sided:.4f}")
print("-" * 35)

if p_value_one_sided < alpha:
    print("結論：**拒絕 H0**。新網站的平均停留時間顯著高於 120 秒。")
else:
    print("結論：**無法拒絕 H0**。沒有足夠證據顯示新網站平均停留時間更高。")