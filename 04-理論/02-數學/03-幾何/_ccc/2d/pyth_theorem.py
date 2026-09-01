import math
from geometry2d_points import Point, Line, Circle, solve_quadratic, get_perpendicular_line

# --- 新增：計算兩點距離 ---
def distance(P1: Point, P2: Point):
    """計算兩點 P1 和 P2 之間的歐幾里得距離。"""
    dx = P2.x - P1.x
    dy = P2.y - P1.y
    return math.sqrt(dx**2 + dy**2)

# --- 新增：驗證畢氏定理 ---
def verify_pythagorean_theorem(L: Line, P0: Point, tolerance=1e-9):
    """
    驗證由 L 的起點 P1、線外點 P0 和垂足 P2 形成的直角三角形是否滿足畢氏定理。
    L 的垂足 P2 是 P0 到 L 上的投影點。
    直角在 P2 處，斜邊為 P1 P0。
    """
    
    P1 = L.P1 # 取原直線的其中一點 P1 (也可取 P2，但 P1 更有代表性)
    
    # 1. 找出垂足 P2
    result = get_perpendicular_line(L, P0)
    P2 = result["foot_of_perpendicular"]
    
    if not isinstance(P2, Point):
        return f"無法找到垂足 (P0 可能在直線上或平行線情況): {P2}"

    # 2. 計算三邊長度
    a = distance(P1, P2) # 股 (直角邊)
    b = distance(P2, P0) # 股 (直角邊)
    c = distance(P1, P0) # 斜邊
    
    # 3. 驗證 a^2 + b^2 = c^2
    a_sq = a**2
    b_sq = b**2
    c_sq = c**2
    
    sum_of_squares = a_sq + b_sq
    
    # 檢查是否在容許誤差範圍內
    is_verified = abs(sum_of_squares - c_sq) < tolerance
    
    print("\n--- 畢氏定理驗證 ---")
    print(f"點 P1 (原直線起點): {P1}")
    print(f"點 P0 (線外點): {P0}")
    print(f"垂足 P2 (交點): {P2}")
    print(f"--- 邊長計算 ---")
    print(f"邊 P1P2 (a): {a:.4f}, a^2: {a_sq:.4f}")
    print(f"邊 P2P0 (b): {b:.4f}, b^2: {b_sq:.4f}")
    print(f"邊 P1P0 (c): {c:.4f}, c^2: {c_sq:.4f}")
    print(f"a^2 + b^2: {sum_of_squares:.4f}")
    
    if is_verified:
        return f"驗證結果: 成功! |a^2 + b^2 - c^2| = {abs(sum_of_squares - c_sq):.12f} (小於容許誤差)"
    else:
        return f"驗證結果: 失敗! a^2 + b^2 - c^2 = {sum_of_squares - c_sq:.4f}"


if __name__ == "__main__":
    # --- 測試數據 (沿用原檔案的測試點) ---
    # 點
    P_1 = Point(1, 2)
    P_2 = Point(4, 5)
    P_out = Point(10, 1)
    Center_C = Point(2, 3)

    # 線 (L1: y=x+1 -> x-y=-1)
    L1 = Line(P_1, P_2)
    # 垂直線測試結果 L_perp: x+y=11，垂足 P2: (5, 6)

    # --- 執行畢氏定理驗證 ---
    print(verify_pythagorean_theorem(L1, P_out))
    
    print("\n--- 另一個測試 (更容易手動驗證的點) ---")
    
    # 測試點 2
    P_A = Point(0, 0)
    P_B = Point(4, 0)
    L_test = Line(P_A, P_B) # 直線 L_test: y=0 (x軸)
    P_C = Point(4, 3) # 線外點 P0

    # 預期垂足 P2 應為 (4, 0)
    # P1P2 (a): distance((0,0), (4,0)) = 4
    # P2P0 (b): distance((4,0), (4,3)) = 3
    # P1P0 (c): distance((0,0), (4,3)) = 5
    # 4^2 + 3^2 = 16 + 9 = 25 = 5^2
    
    print(verify_pythagorean_theorem(L_test, P_C))
