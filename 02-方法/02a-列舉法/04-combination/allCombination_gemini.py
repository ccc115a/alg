def combinations(arr, k, current_combo=[], start_index=0):
    """
    從陣列中選擇 k 個元素，並列印所有可能的組合。

    參數：
    arr (list): 原始陣列。
    k (int): 選擇的元素數量。
    current_combo (list): 目前正在建構的組合（預設為空列表）。
    start_index (int): 開始尋找下一個元素的索引（預設為 0）。
    """
    # 基本情況：如果目前組合的元素數量等於 k，就代表找到一個完整的組合。
    if len(current_combo) == k:
        print(current_combo)
        return

    # 遞迴情況：從 start_index 開始，依序選擇元素。
    for i in range(start_index, len(arr)):
        # 選擇當前元素 arr[i]
        current_combo.append(arr[i])
        
        # 遞迴呼叫，從下一個索引 i + 1 開始尋找下一個元素
        combinations(arr, k, current_combo, i + 1)
        
        # 回溯：移除最後一個元素，以便尋找其他可能性
        current_combo.pop()

# --- 範例 ---
# 假設我們有一個陣列 [1, 2, 3, 4]，並想從中選擇 2 個元素。
my_array = [1, 2, 3, 4]
k = 2

print(f"從 {my_array} 中選擇 {k} 個元素的所有組合：")
combinations(my_array, k)