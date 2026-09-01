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
    代表直線，使用一般式 Ax + By = C。
    法向量 n = (A, B)。
    """
    def __init__(self, A, B, C):
        self.A = float(A)
        self.B = float(B)
        self.C = float(C)

    def __repr__(self):
        return f"Line({self.A:.2f}x + {self.B:.2f}y = {self.C:.2f})"

class Circle:
    """
    代表圓，使用一般式 x^2 + y^2 + Dx + Ey + F = 0。
    """
    def __init__(self, D, E, F):
        self.D = float(D)
        self.E = float(E)
        self.F = float(F)
        
        # 檢查是否為實圓並計算圓心和半徑
        r_squared = (D**2 + E**2) / 4 - F
        if r_squared < 0:
             raise ValueError("參數定義的不是實數圓 (半徑平方為負)")
        
        self.center = Point(-D / 2, -E / 2)
        self.radius = math.sqrt(r_squared)

    def __repr__(self):
        return f"Circle(Center={self.center}, Radius={self.radius:.4f})"

def solve_quadratic(a, b, c, tolerance=1e-9):
    """手動解一元二次方程 ax^2 + bx + c = 0。"""
    
    # 判別式
    discriminant = b**2 - 4 * a * c
    
    if discriminant < -tolerance:
        return "No intersection (imaginary roots)"
    elif abs(discriminant) < tolerance:
        # 相切 (一個重根)
        root = -b / (2 * a)
        return [root]
    else:
        # 相交 (兩個根)
        sqrt_disc = math.sqrt(discriminant)
        root1 = (-b + sqrt_disc) / (2 * a)
        root2 = (-b - sqrt_disc) / (2 * a)
        return [root1, root2]

def intersect_two_lines(L1: Line, L2: Line):
    """計算兩條直線的交點，使用克萊默法則。"""
    
    # 計算主行列式 Delta
    det = L1.A * L2.B - L2.A * L1.B
    
    if abs(det) < 1e-9: # 行列式接近零，直線平行或重合
        # 檢查是否重合 (透過比例關係)
        # L1.A / L2.A == L1.B / L2.B == L1.C / L2.C
        
        # 避免除以零，我們檢查交叉相乘的等價關係
        is_proportional_ab = abs(L1.A * L2.B - L2.A * L1.B) < 1e-9
        is_proportional_ac = abs(L1.A * L2.C - L2.A * L1.C) < 1e-9
        is_proportional_bc = abs(L1.B * L2.C - L2.B * L1.C) < 1e-9
        
        if is_proportional_ab and is_proportional_ac and is_proportional_bc:
            return "Infinite intersections (lines are coincident)"
        else:
            return "No intersection (lines are parallel)"
    else:
        # 計算 Delta_x 和 Delta_y
        det_x = L1.C * L2.B - L2.C * L1.B
        det_y = L1.A * L2.C - L2.A * L1.C
        
        # 求解 x 和 y
        x = det_x / det
        y = det_y / det
        
        return Point(x, y)


def intersect_two_circles(C1: Circle, C2: Circle):
    """計算兩個圓 C1 和 C2 的交點。"""
    
    # 1. 導出公共弦的直線 L_chord: Ax + By = C
    # (D1-D2)x + (E1-E2)y = (F2-F1)
    
    A = C1.D - C2.D
    B = C1.E - C2.E
    C = C2.F - C1.F
    
    # 如果 A=0 且 B=0，圓心相同。
    if abs(A) < 1e-9 and abs(B) < 1e-9:
        if abs(C) < 1e-9:
            return "Infinite intersections (circles are identical)"
        else:
            return "No intersection (concentric circles)"
            
    L_chord = Line(A, B, C)
    
    # 2. 轉化為直線與圓的交點問題 (使用 C1 和 L_chord)
    return intersect_line_circle(L_chord, C1)

def intersect_line_circle(L: Line, C: Circle):
    """計算直線 L 與圓 C 的交點。"""
    
    if abs(L.B) < 1e-9: # L.B 接近 0，直線為鉛直線 x = x_L
        
        if abs(L.A) < 1e-9: # L.A 也接近 0，表示 L 是一個無效的 Line 物件 (0x + 0y = C)
            return "Error: Invalid line definition"
            
        x_L = L.C / L.A
        
        # 整理成 Ay^2 + By + C = 0 的形式
        a = 1.0
        b = C.E
        c = x_L**2 + C.D * x_L + C.F
        
        y_solutions = solve_quadratic(a, b, c)
        
        if isinstance(y_solutions, str):
            return y_solutions
        else:
            intersections = [Point(x_L, y) for y in y_solutions]
            return intersections

    else: # L.B 不接近 0，解出 y = m*x + b_L
        
        m = -L.A / L.B
        b_L = L.C / L.B
        
        # 代入圓 C 整理成 ax^2 + bx + c = 0
        a = 1 + m**2
        b = 2 * m * b_L + C.D + C.E * m
        c = b_L**2 + C.E * b_L + C.F
        
        x_solutions = solve_quadratic(a, b, c)
        
        if isinstance(x_solutions, str):
            return x_solutions
        else:
            # 構造交點
            intersections = [Point(x, m * x + b_L) for x in x_solutions]
            return intersections

def get_perpendicular_line(L: Line, P: Point):
    """
    給定直線 L 和線外一點 P，返回通過 P 且垂直於 L 的新直線 L_perp。
    """
    
    # 1. 決定新直線的法向量 (A_perp, B_perp)
    # L 的法向量 (A, B) 垂直於 L_perp 的法向量 (-B, A)
    A_perp = -L.B
    B_perp = L.A
    
    # 2. 決定新直線的常數 C_perp
    # L_perp: A_perp * x + B_perp * y = C_perp 必須通過 P(xp, yp)
    C_perp = A_perp * P.x + B_perp * P.y
    
    L_perp = Line(A_perp, B_perp, C_perp)
    
    # 找到垂足 (呼叫 intersect_two_lines 函數)
    foot_of_perpendicular = intersect_two_lines(L, L_perp)
    
    return {
        "perpendicular_line": L_perp,
        "foot_of_perpendicular": foot_of_perpendicular
    }

if __name__ == "__main__":
    # 測試所有功能
    # 測試
    L_a = Line(2, 3, 6)
    L_b = Line(4, -3, 6)
    print("1. 兩直線交點測試:")
    print(f"   {L_a} 和 {L_b}: {intersect_two_lines(L_a, L_b)}") 
    L_c = Line(1, 1, 1)
    L_d = Line(2, 2, 5)
    print(f"   {L_c} 和 {L_d}: {intersect_two_lines(L_c, L_d)}")
    L_e = Line(1, 1, 1)
    L_f = Line(2, 2, 2)
    print(f"   {L_e} 和 {L_f}: {intersect_two_lines(L_e, L_f)}\n")

    # 測試
    C_g = Circle(-2, 0, -8) 
    C_h = Circle(2, 0, -8)
    print("2. 兩個圓交點測試:")
    print(f"   {C_g} 和 {C_h}: {intersect_two_circles(C_g, C_h)}\n")

    # 測試
    C_i = Circle(0, 0, -25) 
    L_j = Line(2, -1, 5)
    print("3. 直線與圓交點測試:")
    print(f"   {L_j} 和 {C_i}: {intersect_line_circle(L_j, C_i)}")

    L_k = Line(1, 0, 5) 
    print(f"   {L_k} 和 {C_i} (切線): {intersect_line_circle(L_k, C_i)}")

    L_l = Line(1, 0, 10)
    print(f"   {L_l} 和 {C_i} (不相交): {intersect_line_circle(L_l, C_i)}\n")

    # 測試
    L_m = Line(2, 3, 6)
    P_n = Point(5, 4)

    result = get_perpendicular_line(L_m, P_n)

    print("4. 過線外一點作垂直線測試:")
    print(f"   原直線 L: {L_m}")
    print(f"   線外點 P: {P_n}")
    print(f"   垂直線 L_perp: {result['perpendicular_line']}")
    print(f"   垂足 Q (交點): {result['foot_of_perpendicular']}")