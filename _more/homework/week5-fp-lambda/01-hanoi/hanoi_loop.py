def move_disk(peg1, peg2, name1, name2):
    """在兩個柱子之間進行唯一合法的移動"""
    if not peg1:  # peg1 為空，將 peg2 的盤子移到 peg1
        disk = peg2.pop()
        peg1.append(disk)
        print(f"將盤子 {disk} 從 {name2} 移動到 {name1}")
    elif not peg2:  # peg2 為空，將 peg1 的盤子移到 peg2
        disk = peg1.pop()
        peg2.append(disk)
        print(f"將盤子 {disk} 從 {name1} 移動到 {name2}")
    elif peg1[-1] < peg2[-1]:  # peg1 頂端盤子較小
        disk = peg1.pop()
        peg2.append(disk)
        print(f"將盤子 {disk} 從 {name1} 移動到 {name2}")
    else:  # peg2 頂端盤子較小
        disk = peg2.pop()
        peg1.append(disk)
        print(f"將盤子 {disk} 從 {name2} 移動到 {name1}")

def hanoi_iterative(n, source, target, auxiliary):
    # 使用串列模擬柱子上的堆疊（數字越大代表盤子越大）
    pegs = {
        source: list(range(n, 0, -1)),
        target: [],
        auxiliary: []
    }
    
    total_moves = (1 << n) - 1  # 2^n - 1 次移動
    
    # 若 n 為奇數，順序為 source -> target -> auxiliary
    # 若 n 為偶數，順序為 source -> auxiliary -> target
    if n % 2 == 1:
        p_seq = [source, target, auxiliary]
    else:
        p_seq = [source, auxiliary, target]
        
    p1_pos = 0  # 盤子 1 當前的索引位置
    
    for i in range(1, total_moves + 1):
        if i % 2 == 1:
            # 奇數步：移動最小的盤子 1 到下一個位置
            prev_pos = p1_pos
            p1_pos = (p1_pos + 1) % 3
            disk = pegs[p_seq[prev_pos]].pop()
            pegs[p_seq[p1_pos]].append(disk)
            print(f"將盤子 {disk} 從 {p_seq[prev_pos]} 移動到 {p_seq[p1_pos]}")
        else:
            # 偶數步：在另外兩根柱子之間做合法移動
            other_peg1 = p_seq[(p1_pos + 1) % 3]
            other_peg2 = p_seq[(p1_pos + 2) % 3]
            move_disk(pegs[other_peg1], pegs[other_peg2], other_peg1, other_peg2)

# 測試：3 個盤子，從 A 移到 C（B 為輔助）
print("=== 非遞迴解法 ===")
hanoi_iterative(3, 'A', 'C', 'B')