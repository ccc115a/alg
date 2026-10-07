def hanoi(n, src, aux, target):
    """
    n: 盤子數量
    src: 起始柱（Source）
    aux: 輔助/中介柱（Auxiliary）
    target: 目標柱（Target）
    """
    # 邊界條件 (Base Case)：只剩 1 個盤子時，直接移動到目標柱
    if n == 1:
        print(f"將盤子 1 從 {src} 移動到 {target}")
        return

    # 步驟 1: 將上方 n-1 個盤子從 src 搬到 aux
    hanoi(n - 1, src, target, aux)

    # 步驟 2: 將最大盤子 (第 n 個) 從 src 搬到 target
    print(f"將盤子 {n} 從 {src} 移動到 {target}")

    # 步驟 3: 將 aux 上的 n-1 個盤子搬到 target
    hanoi(n - 1, aux, src, target)


# 執行測試：求解 3 個盤子的河內塔
if __name__ == "__main__":
    n = 64
    print(f"--- {n} 個盤子的河內塔移動步驟 ---")
    hanoi(n, src="A", aux="B", target="C")