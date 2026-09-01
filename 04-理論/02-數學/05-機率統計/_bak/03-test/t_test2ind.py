import numpy as np
from scipy import stats

# 1. 準備數據 (綠色按鈕組與藍色按鈕組的停留時間)
group_A_green = np.array([110, 105, 112, 118, 108, 115, 111, 116])
group_B_blue = np.array([120, 125, 119, 122, 128, 124, 121, 123])

# 2. 執行獨立樣本 t 檢定
# ttest_ind 默認假設變異數相等 (equal_var=True)。
# 如果 Levene's 檢定顯示變異數不等，可設定 equal_var=False (即 Welch's t-Test)。
t_stat_ind, p_value_ind = stats.ttest_ind(group_A_green, group_B_blue, equal_var=True)

# 3. 輸出結果
alpha = 0.05
print("\n--- 獨立樣本 t 檢定 (Independent Samples t-Test) ---")
print(f"A 組 (綠色) 平均值: {group_A_green.mean():.2f} 秒")
print(f"B 組 (藍色) 平均值: {group_B_blue.mean():.2f} 秒")
print(f"T 統計量: {t_stat_ind:.4f}")
print(f"雙尾 P 值: {p_value_ind:.4f}")
print("-" * 49)

if p_value_ind < alpha:
    print("結論：**拒絕 H0**。綠色按鈕組和藍色按鈕組的平均停留時間有顯著差異。")
else:
    print("結論：**無法拒絕 H0**。兩組的平均停留時間沒有顯著差異。")