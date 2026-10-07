# ==========================================
# 1. 自製 Higher-Order Functions (完全無迴圈)
# ==========================================

def my_map(func, lst):
    """自製 map: 對串列每個元素套用 func"""
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])

def my_filter(func, lst):
    """自製 filter: 留下滿足 func 的元素"""
    if not lst:
        return []
    head, tail = lst[0], lst[1:]
    if func(head):
        return [head] + my_filter(func, tail)
    return my_filter(func, tail)

def my_reduce(func, lst, initializer=None):
    """自製 reduce: 將串列元素累加/折疊為單一數值"""
    if initializer is None:
        if not lst:
            raise TypeError("my_reduce() of empty sequence with no initial value")
        return my_reduce(func, lst[1:], lst[0])
    if not lst:
        return initializer
    return my_reduce(func, lst[1:], func(initializer, lst[0]))


# ==========================================
# 2. 禁止迴圈的泡沫排序 (Bubble Sort)
# ==========================================

def bubble_pass(acc, current):
    """
    搭配 my_reduce 使用的單次比較與交換函數：
    acc 為 (已處理的串列, 當前較大的元素)
    """
    processed, max_val = acc
    if max_val > current:
        return (processed + [current], max_val)
    else:
        return (processed + [max_val], current)

def bubble_sort_pass(lst):
    """
    執行「單一輪」的泡沫排序 (Single Pass)
    利用 my_reduce 將最大的元素浮到串列末端
    """
    if not lst:
        return []
    # 以 lst[0] 為初始最大值，對剩餘元素 lst[1:] 執行折疊
    processed, max_val = my_reduce(bubble_pass, lst[1:], ([], lst[0]))
    return processed + [max_val]

def bubble_sort(lst, n=None):
    """
    主泡沫排序函數 (完全遞迴，無迴圈)
    需要進行 n 次 pass (n 為串列長度)
    """
    if n is None:
        n = len(lst)
    if n <= 1:
        return lst
    
    # 進行一輪泡沫比較，最大值會抵達末端
    one_passed = bubble_sort_pass(lst)
    
    # 遞迴對前 n-1 個元素繼續做排序，最後拼接已排好的末端元素
    return bubble_sort(one_passed[:-1], n - 1) + [one_passed[-1]]


# ==========================================
# 3. 測試主程式
# ==========================================

if __name__ == "__main__":
    print("=== 1. 測試自製 Higher-Order Functions ===")
    sample = [1, 2, 3, 4, 5]
    
    # 測試 my_map
    mapped = my_map(lambda x: x ** 2, sample)
    print(f"my_map (平方): {mapped}")
    
    # 測試 my_filter
    filtered = my_filter(lambda x: x % 2 == 0, sample)
    print(f"my_filter (偶數): {filtered}")
    
    # 測試 my_reduce
    reduced = my_reduce(lambda acc, x: acc + x, sample, 0)
    print(f"my_reduce (加總): {reduced}")

    print("\n=== 2. 測試無迴圈泡沫排序 ===")
    unsorted_list = [64, 34, 25, 12, 22, 11, 90, 5]
    print(f"原始串列: {unsorted_list}")
    
    sorted_list = bubble_sort(unsorted_list)
    print(f"排序結果: {sorted_list}")