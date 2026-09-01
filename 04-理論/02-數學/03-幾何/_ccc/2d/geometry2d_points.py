import math

class Point:
    """代表二維平面上的點 (x, y)。"""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __repr__(self):
        return f"Point({self.x:.4f}, {self.y:.4f})"

class Line:
    """
    代表直線，由兩個點 P1, P2 定義。
    內部轉換為一般式 Ax + By = C。
    """
    def __init__(self, P1: Point, P2: Point):
        self.P1 = P1
        self.P2 = P2
        
        # 轉換為一般式 Ax + By = C
        
        # A = y2 - y1
        self.A = P2.y - P1.y
        # B = x1 - x2
        self.B = P1.x - P2.x
        # C = A*x1 + B*y1 (或 A*x2 + B*y2)
        self.C = self.A * P1.x + self.B * P1.y

        # 檢查是否為同一個點
        if abs(self.A) < 1e-9 and abs(self.B) < 1e-9:
             raise ValueError("無法用兩個相同的點定義一條直線")

    def __repr__(self):
        # 顯示一般式，以便閱讀
        return f"Line(P1={self.P1}, P2={self.P2}, Eq:{self.A:.2f}x + {self.B:.2f}y = {self.C:.2f})"

class Circle:
    """
    代表圓，由圓心 (center) 和半徑 (radius) 定義。
    內部轉換為標準式 (x-h)^2 + (y-k)^2 = r^2。
    """
    def __init__(self, center: Point, radius):
        self.center = center
        self.radius = float(radius)
        
        if self.radius <= 0:
             raise ValueError("半徑必須為正數")

        # 內部儲存一般式參數，方便交點計算
        # x^2 + y^2 - 2hx - 2ky + (h^2+k^2-r^2) = 0
        self.D = -2 * center.x
        self.E = -2 * center.y
        self.F = center.x**2 + center.y**2 - self.radius**2

    def __repr__(self):
        return f"Circle(Center={self.center}, Radius={self.radius:.4f})"

def solve_quadratic(a, b, c, tolerance=1e-9):
    """手動解一元二次方程 ax^2 + bx + c = 0。"""
    
    discriminant = b**2 - 4 * a * c
    
    if discriminant < -tolerance:
        return "No intersection (imaginary roots)"
    elif abs(discriminant) < tolerance:
        root = -b / (2 * a)
        return [root]
    else:
        sqrt_disc = math.sqrt(discriminant)
        root1 = (-b + sqrt_disc) / (2 * a)
        root2 = (-b - sqrt_disc) / (2 * a)
        return [root1, root2]

# --- 1. 兩直線交點 ---
def intersect_two_lines(L1: Line, L2: Line):
    """計算兩條直線的交點，使用克萊默法則。"""
    
    # 提取一般式參數
    A1, B1, C1 = L1.A, L1.B, L1.C
    A2, B2, C2 = L2.A, L2.B, L2.C

    # 計算主行列式 Delta
    det = A1 * B2 - A2 * B1
    
    if abs(det) < 1e-9: # 直線平行或重合
        # 檢查是否重合 (檢查 C 是否也滿足比例關係)
        is_proportional_ac = abs(A1 * C2 - A2 * C1) < 1e-9
        is_proportional_bc = abs(B1 * C2 - B2 * C1) < 1e-9
        
        if is_proportional_ac and is_proportional_bc:
            return "Infinite intersections (lines are coincident)"
        else:
            return "No intersection (lines are parallel)"
    else:
        # 計算 Delta_x 和 Delta_y
        det_x = C1 * B2 - C2 * B1
        det_y = A1 * C2 - A2 * C1
        
        # 求解 x 和 y
        x = det_x / det
        y = det_y / det
        
        return Point(x, y)

# --- 3. 一直線與一個圓之交點 --- (在 2 之前定義，因為 2 會用到 3)
def intersect_line_circle(L: Line, C: Circle):
    """計算直線 L 與圓 C 的交點。"""
    
    A, B, C_L = L.A, L.B, L.C # 直線一般式參數
    D, E, F = C.D, C.E, C.F # 圓一般式參數
    
    if abs(B) < 1e-9: # B 接近 0，直線為鉛直線 x = x_L
        
        x_L = C_L / A
        
        # 整理成 Ay^2 + By + C = 0 的形式
        a = 1.0
        b = E
        c = x_L**2 + D * x_L + F
        
        y_solutions = solve_quadratic(a, b, c)
        
        if isinstance(y_solutions, str):
            return y_solutions
        else:
            intersections = [Point(x_L, y) for y in y_solutions]
            return intersections

    else: # B 不接近 0，解出 y = m*x + b_L
        
        m = -A / B
        b_L = C_L / B
        
        # 代入圓 C 整理成 ax^2 + bx + c = 0
        a = 1 + m**2
        b = 2 * m * b_L + D + E * m
        c = b_L**2 + E * b_L + F
        
        x_solutions = solve_quadratic(a, b, c)
        
        if isinstance(x_solutions, str):
            return x_solutions
        else:
            intersections = [Point(x, m * x + b_L) for x in x_solutions]
            return intersections

# --- 2. 兩個圓交點 ---
def intersect_two_circles(C1: Circle, C2: Circle):
    """計算兩個圓 C1 和 C2 的交點。"""
    
    # 導出公共弦的直線 L_chord: Ax + By = C_L
    # (D1-D2)x + (E1-E2)y = (F2-F1)
    
    A = C1.D - C2.D
    B = C1.E - C2.E
    C_L = C2.F - C1.F
    
    # 如果 A=0 且 B=0，圓心相同。
    if abs(A) < 1e-9 and abs(B) < 1e-9:
        if abs(C_L) < 1e-9:
            return "Infinite intersections (circles are identical)"
        else:
            return "No intersection (concentric circles)"
            
    L_chord = Line(Point(0, C_L/B if abs(B)>1e-9 else 0), Point(C_L/A if abs(A)>1e-9 else 0, 0)) # 隨機兩點定義，只為構造正確的 A, B, C_L
    
    # 手動創建 L_chord 物件，確保使用正確的 A, B, C_L
    # 因為 Line 的 __init__ 參數是 P1, P2，我們需要一個特殊的建構方式
    L_chord_final = Line(Point(0,0), Point(1,1)) # 佔位符
    L_chord_final.A = A
    L_chord_final.B = B
    L_chord_final.C = C_L
    
    # 轉化為直線與圓的交點問題 (使用 C1 和 L_chord_final)
    return intersect_line_circle(L_chord_final, C1)

# --- 4. 給定直線與線外一點，傳回垂直線 ---
def get_perpendicular_line(L: Line, P: Point):
    """
    給定直線 L 和線外一點 P，返回通過 P 且垂直於 L 的新直線 L_perp。
    """
    
    # 1. 決定新直線的法向量 (A_perp, B_perp)
    # L 的法向量 (L.A, L.B) 垂直於 L_perp 的法向量 (-L.B, L.A)
    A_perp = -L.B
    B_perp = L.A
    
    # 2. 決定新直線的常數 C_perp
    # L_perp: A_perp * x + B_perp * y = C_perp 必須通過 P(xp, yp)
    C_perp = A_perp * P.x + B_perp * P.y
    
    # 3. 構造新直線 L_perp (需要兩個點)
    
    # 找到 L_perp 上的兩個點
    
    # 情況一：L_perp 非垂直線 (B_perp != 0)
    if abs(B_perp) > 1e-9:
        # 取 x=0，y0 = C_perp / B_perp
        P_new1 = Point(0, C_perp / B_perp)
        # 取 x=1，y1 = (C_perp - A_perp) / B_perp
        P_new2 = Point(1, (C_perp - A_perp) / B_perp)
    # 情況二：L_perp 是垂直線 (B_perp = 0, A_perp != 0)
    else:
        # x = C_perp / A_perp
        x_val = C_perp / A_perp
        P_new1 = Point(x_val, 0)
        P_new2 = Point(x_val, 1)

    L_perp = Line(P_new1, P_new2) # 使用兩個點定義新直線

    # 找到垂足 (L 和 L_perp 的交點)
    foot_of_perpendicular = intersect_two_lines(L, L_perp)
    
    return {
        "perpendicular_line": L_perp,
        "foot_of_perpendicular": foot_of_perpendicular
    }

if __name__ == "__main__":
    # --- 測試數據 ---
    # 點
    P_1 = Point(1, 2)
    P_2 = Point(4, 5)
    P_out = Point(10, 1)
    Center_C = Point(2, 3)

    # 線 (L1: y=x+1 -> x-y=-1)
    L1 = Line(P_1, P_2)
    # 線 (L2: 2x+3y=17)
    P_3 = Point(1, 5)
    P_4 = Point(7, 1)
    L2 = Line(P_3, P_4)
    # 圓 (C1: (x-2)^2 + (y-3)^2 = 9)
    C1 = Circle(Center_C, 3) 
    # 圓 (C2: (x-5)^2 + (y-3)^2 = 9)
    Center_C2 = Point(5, 3)
    C2 = Circle(Center_C2, 3)

    # --- 執行測試 ---
    print("--- 幾何交點求解測試 (無 NumPy) ---")
    print("1. 兩直線交點測試:")
    # L1 (x-y=-1) 和 L2 (2x+3y=17) 預期交點: (2.8, 3.8)
    print(f"   L1 和 L2: {intersect_two_lines(L1, L2)}")

    # 測試平行線
    L_par_P1 = Point(0, 0)
    L_par_P2 = Point(1, 1)
    L_par1 = Line(L_par_P1, L_par_P2) # y=x
    L_par_P3 = Point(0, 1)
    L_par_P4 = Point(1, 2)
    L_par2 = Line(L_par_P3, L_par_P4) # y=x+1
    print(f"   L_par1 和 L_par2: {intersect_two_lines(L_par1, L_par2)}\n")


    print("2. 兩個圓交點測試:")
    # C1 ((x-2)^2 + (y-3)^2 = 9) 和 C2 ((x-5)^2 + (y-3)^2 = 9)
    # 預期公共弦 x=3.5，交點 (3.5, 3 +- sqrt(6.75))
    print(f"   C1 和 C2: {intersect_two_circles(C1, C2)}\n")


    print("3. 直線與圓交點測試:")
    # L3 (x=5) (使用兩個點定義)
    L3 = Line(Point(5, 0), Point(5, 1))
    # 圓 C1 ((x-2)^2 + (y-3)^2 = 9)。L3 代入得 (5-2)^2 + (y-3)^2 = 9 -> 9 + (y-3)^2 = 9 -> y=3
    # 預期交點：(5, 3) (相切)
    print(f"   L3 (切線) 和 C1: {intersect_line_circle(L3, C1)}")

    # L4 (y=3)
    L4 = Line(Point(0, 3), Point(1, 3))
    # 預期交點：(2 +- 3, 3) -> (-1, 3) 和 (5, 3)
    print(f"   L4 (割線) 和 C1: {intersect_line_circle(L4, C1)}\n")


    print("4. 過線外一點作垂直線測試:")
    # L1 (x-y=-1)
    # 線外點 P_out (10, 1)
    result = get_perpendicular_line(L1, P_out)
    # 垂直線 L_perp: -(-1)x + 1y = C_perp -> x+y = 10+1 = 11
    # L1 和 L_perp 交點: x-y=-1, x+y=11 -> 2x=10, x=5. y=6. (5, 6)
    print(f"   原直線 L1: {L1}")
    print(f"   線外點 P_out: {P_out}")
    print(f"   垂直線 L_perp: {result['perpendicular_line']}")
    print(f"   垂足 Q (交點): {result['foot_of_perpendicular']}")
