def hanoi_recursive(n, source, target, auxiliary):
    """
    n: 盤子數量
    source: 起始柱子
    target: 目標柱子
    auxiliary: 輔助柱子
    """
    if n == 1:
        print(f"將盤子 1 從 {source} 移動到 {target}")
        return
    
    # 步驟 1: 將 n-1 個盤子從 source 移到 auxiliary
    hanoi_recursive(n - 1, source, auxiliary, target)
    
    # 步驟 2: 將第 n 個盤子從 source 移到 target
    print(f"將盤子 {n} 從 {source} 移動到 {target}")
    
    # 步驟 3: 將 n-1 個盤子從 auxiliary 移到 target
    hanoi_recursive(n - 1, auxiliary, target, source)

# 測試：3 個盤子，從 A 移到 C（B 為輔助）
print("=== 遞迴解法 ===")
hanoi_recursive(3, 'A', 'C', 'B')