import operator
from functools import reduce

def riemann_n_dim_integral(func, ranges, num_steps_per_dim):
    """
    使用基本的黎曼積分 (矩形近似求和) 計算 n 維定積分。
    不依賴任何外部數學函式庫。

    參數:
    -----
    func : callable
        要積分的函數 f(x1, x2, ..., xn)。
        它必須接受 n 個單獨的浮點數參數。
        範例: func(x1, x2, ..., xn)
        
    ranges : list of tuples
        定義積分區域的界限。格式為 [(a1, b1), (a2, b2), ..., (an, bn)]。
        len(ranges) 即為維度 n。
        
    num_steps_per_dim : int
        每個維度上均勻分割的子區間數量 M。
        總分割數 N = M^n。

    回傳值:
    -------
    float: 積分的近似值 (黎曼和)。
    """
    n = len(ranges)  # 積分的維度 n
    
    # 1. 計算每個維度上的步長 (微分體積元素的一邊長)
    steps = []
    for a, b in ranges:
        if a >= b:
            # 處理無效區間
            return 0.0
        # 每個維度的步長 Δxi = (bi - ai) / M
        step_size = (b - a) / num_steps_per_dim
        steps.append(step_size)
        
    # 2. 計算 n 維微分體積元素 dV = Δx1 * Δx2 * ... * Δxn
    # reduce(operator.mul, steps) 等效於 steps[0] * steps[1] * ...
    dV = reduce(operator.mul, steps)
    
    # 3. 準備 n 層巢狀迴圈所需的索引範圍
    # 這是黎曼積分從頭實現的關鍵難點：需要創建 n 層動態巢狀迴圈。
    
    # 這是所有維度的起始座標 (下界)
    lower_bounds = [a for a, b in ranges]

    # 黎曼和初始化
    riemann_sum = 0.0

    # 4. 執行 n 維累次求和 (使用遞迴模擬巢狀迴圈)
    
    def iterate_and_sum(current_dim, current_coords):
        """
        遞迴函數，用於模擬 n 層巢狀迴圈，遍歷所有子區域。
        """
        nonlocal riemann_sum # 允許修改外部函數的 riemann_sum 變數

        if current_dim == n:
            # 達到最內層 (所有 n 個座標都已確定)
            # current_coords 包含 (x1, x2, ..., xn)
            
            # 使用子區間的左下角點 (這是黎曼積分最簡單的取樣點方式)
            sample_point = tuple(current_coords)
            
            # 構建黎曼和: f(x*) * dV
            riemann_sum += func(*sample_point) * dV
            return
        
        # 遍歷當前維度 (current_dim) 的所有 M 個子區間
        # 第 i 個子區間的起始座標為 a_i + j * Δx_i
        a_i = lower_bounds[current_dim]
        delta_x_i = steps[current_dim]
        
        for j in range(num_steps_per_dim):
            # 確定當前維度的座標 (取左端點)
            x_i = a_i + j * delta_x_i
            
            # 繼續遞迴到下一個維度 (current_dim + 1)
            iterate_and_sum(current_dim + 1, current_coords + [x_i])
    
    # 從第 0 維開始遞迴
    iterate_and_sum(0, [])
    
    return riemann_sum

# --- 範例與驗證 ---

print("--- n 維黎曼積分 (純 Python 實現) ---")

# 1. 函數 f(x1, x2) = x1 + x2 (n=2)
# 解析解: ∫[0,2]∫[0,1] (x1 + x2) dx1 dx2 = 3.0
def f_2d(x1, x2):
    return x1 + x2

ranges_2d = [(0.0, 1.0), (0.0, 2.0)]
steps_2d = 100 # 總分割數 100 * 100 = 10,000

result_2d = riemann_n_dim_integral(f_2d, ranges_2d, steps_2d)
print(f"1. 函數 f(x1, x2) = x1 + x2 (n=2)")
print(f"   積分區域: {ranges_2d}")
print(f"   分割數 (每維): {steps_2d}")
print(f"   黎曼和近似值: {result_2d:.6f}")
print(f"   解析解 (準確值): 3.000000")
print("-" * 30)


# 2. 函數 f(x1, x2, x3) = x1 * x2 * x3 (n=3)
# 解析解: ∫[0,1]∫[0,1]∫[0,1] (x1*x2*x3) dx1 dx2 dx3 = (1/2)^3 = 0.125
def f_3d(x1, x2, x3):
    return x1 * x2 * x3

ranges_3d = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
steps_3d = 50 # 總分割數 50 * 50 * 50 = 125,000

result_3d = riemann_n_dim_integral(f_3d, ranges_3d, steps_3d)
print(f"2. 函數 f(x1, x2, x3) = x1 * x2 * x3 (n=3)")
print(f"   積分區域: {ranges_3d}")
print(f"   分割數 (每維): {steps_3d}")
print(f"   黎曼和近似值: {result_3d:.6f}")
print(f"   解析解 (準確值): 0.125000")
print("-" * 30)


# 3. 函數 f(x1, ..., xn) = 1 (體積計算) (n=4)
# 體積: 1 * 1 * 1 * 1 = 1.0
def f_4d(x1, x2, x3, x4):
    return 1.0

ranges_4d = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
steps_4d = 10 # 總分割數 10^4 = 10,000 (較低，以確保運行速度)

result_4d = riemann_n_dim_integral(f_4d, ranges_4d, steps_4d)
print(f"3. 函數 f(x1, x2, x3, x4) = 1 (n=4)")
print(f"   積分區域: {ranges_4d}")
print(f"   分割數 (每維): {steps_4d}")
print(f"   黎曼和近似值: {result_4d:.6f}")
print(f"   解析解 (準確值): 1.000000")
print("-" * 30)