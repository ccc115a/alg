import numpy as np
from scipy import stats

# 1. 準備數據 (注意：兩個陣列的順序必須是配對好的，代表同一批用戶的前後測數據)
# 假設只有 10 位用戶
user_N_pairs = 10
time_off = np.array([100, 115, 105, 120, 110, 108, 112, 125, 118, 102])  # 關閉功能時的停留時間
time_on = np.array([115, 125, 109, 135, 120, 115, 120, 130, 125, 110])    # 開啟功能後的停留時間

# 2. 執行配對樣本 t 檢定
# ttest_rel 是 't-test related' 的縮寫
t_stat_rel, p_value_rel = stats.ttest_rel(time_on, time_off)

# 3. 輸出結果
alpha = 0.05
diff_mean = time_on.mean() - time_off.mean()

print("\n--- 配對樣本 t 檢定 (Paired Samples t-Test) ---")
print(f"關閉功能時平均值: {time_off.mean():.2f} 秒")
print(f"開啟功能時平均值: {time_on.mean():.2f} 秒")
print(f"平均差異 (開 - 關): {diff_mean:.2f} 秒")
print(f"T 統計量: {t_stat_rel:.4f}")
print(f"雙尾 P 值: {p_value_rel:.4f}")
print("-" * 46)

if p_value_rel < alpha:
    print("結論：**拒絕 H0**。開啟功能後，用戶的平均停留時間有顯著變化。")
else:
    print("結論：**無法拒絕 H0**。沒有足夠證據顯示功能對平均停留時間有顯著影響。")