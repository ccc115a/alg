# ==========================================
# 1. 自製 FP 模組 (完全無迴圈，全靠遞迴)
# ==========================================

class FP:
    def each(self, iterable, action):
        """
        自製 each 函數：類似 forEach，接受可迭代物件 (如 range 或 list)
        對每個元素執行 action(item)，完全不使用迴圈
        """
        # 將 iterable 轉為 list 方便以頭尾切片 (head/tail) 進行遞迴
        lst = list(iterable) if not isinstance(iterable, list) else iterable
        
        if not lst:
            return None
        
        # 對第一個元素執行動作
        action(lst[0])
        
        # 遞迴處理剩餘元素
        return self.each(lst[1:], action)

    def map(self, func, lst):
        """自製 map"""
        if not lst:
            return []
        return [func(lst[0])] + self.map(func, lst[1:])

    def filter(self, func, lst):
        """自製 filter"""
        if not lst:
            return []
        head, tail = lst[0], lst[1:]
        return [head] + self.filter(func, tail) if func(head) else self.filter(func, tail)

    def reduce(self, func, lst, initializer=None):
        """自製 reduce"""
        if initializer is None:
            if not lst:
                raise TypeError("reduce() of empty sequence with no initial value")
            return self.reduce(func, lst[1:], lst[0])
        if not lst:
            return initializer
        return self.reduce(func, lst[1:], func(initializer, lst[0]))

# 建立 fp 實例
fp = FP()


# ==========================================
# 2. 泡沫排序主程式 (使用 fp.each)
# ==========================================

def swap(a, i, j):
    a[i], a[j] = a[j], a[i]

def bubbleSort(a):
    n = len(a)
    # 外層「迴圈」: i 從 0 到 n-1
    fp.each(range(0, n), lambda i:
        # 內層「迴圈」: j 從 0 到 i-1
        fp.each(range(0, i), lambda j:
            swap(a, i, j) if a[j] > a[i] else None
        )
    )
    return a


# ==========================================
# 3. 測試程式
# ==========================================

if __name__ == "__main__":
    a = [3, 7, 2, 6, 8, 4]
    print("排序前:", a)
    
    bubbleSort(a)
    
    print("排序後:", a)