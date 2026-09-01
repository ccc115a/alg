import numpy as np

# 設定 NumPy 浮點數精度
np.set_printoptions(precision=4)

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
        self.normal_vector = np.array([A, B])

    def __repr__(self):
        return f"Line({self.A:.2f}x + {self.B:.2f}y = {self.C:.2f})"

class Circle:
    """
    代表圓，使用一般式 x^2 + y^2 + Dx + Ey + F = 0。
    圓心為 (-D/2, -E/2)，半徑 r = sqrt(D^2/4 + E^2/4 - F)。
    """
    def __init__(self, D, E, F):
        self.D = float(D)
        self.E = float(E)
        self.F = float(F)
        
        # 計算圓心和半徑，方便後續使用
        self.center = Point(-D / 2, -E / 2)
        # 檢查半徑平方是否非負，否則不是實圓
        r_squared = (D**2 + E**2) / 4 - F
        if r_squared < 0:
             raise ValueError("參數定義的不是實數圓 (半徑平方為負)")
        self.radius = np.sqrt(r_squared)

    def __repr__(self):
        return f"Circle(Center={self.center}, Radius={self.radius:.4f})"

def intersect_two_lines(L1: Line, L2: Line):
    """
    計算兩條直線 L1: A1x + B1y = C1 和 L2: A2x + B2y = C2 的交點。
    使用 NumPy 的線性代數功能求解方程組。
    """
    # 係數矩陣 M 和常數向量 V
    M = np.array([
        [L1.A, L1.B],
        [L2.A, L2.B]
    ])
    V = np.array([L1.C, L2.C])
    
    # 計算行列式 (Determinant)
    det = np.linalg.det(M)
    
    # 判斷結果
    if np.isclose(det, 0):
        # 行列式為零，直線平行或重合
        # 檢查是否重合 (透過檢查 C 是否也滿足比例關係)
        if np.isclose(L1.A * L2.C, L2.A * L1.C) and np.isclose(L1.B * L2.C, L2.B * L1.C):
             return "Infinite intersections (lines are coincident)"
        else:
             return "No intersection (lines are parallel)"
    else:
        # 有唯一解
        try:
            solution = np.linalg.solve(M, V)
            return Point(solution[0], solution[1])
        except np.linalg.LinAlgError:
            # 這是標準解法，但以防萬一
            return "Error solving system (unexpected singular matrix)"


def intersect_two_lines(L1: Line, L2: Line):
    """
    計算兩條直線 L1: A1x + B1y = C1 和 L2: A2x + B2y = C2 的交點。
    使用 NumPy 的線性代數功能求解方程組。
    """
    # 係數矩陣 M 和常數向量 V
    M = np.array([
        [L1.A, L1.B],
        [L2.A, L2.B]
    ])
    V = np.array([L1.C, L2.C])
    
    # 計算行列式 (Determinant)
    det = np.linalg.det(M)
    
    # 判斷結果
    if np.isclose(det, 0):
        # 行列式為零，直線平行或重合
        # 檢查是否重合 (透過檢查 C 是否也滿足比例關係)
        if np.isclose(L1.A * L2.C, L2.A * L1.C) and np.isclose(L1.B * L2.C, L2.B * L1.C):
             return "Infinite intersections (lines are coincident)"
        else:
             return "No intersection (lines are parallel)"
    else:
        # 有唯一解
        try:
            solution = np.linalg.solve(M, V)
            return Point(solution[0], solution[1])
        except np.linalg.LinAlgError:
            # 這是標準解法，但以防萬一
            return "Error solving system (unexpected singular matrix)"


def intersect_two_circles(C1: Circle, C2: Circle):
    """
    計算兩個圓 C1 和 C2 的交點。
    首先通過相減得到公共弦的直線方程。
    """
    # 1. 導出公共弦的直線方程 L_chord: Ax + By = C
    # (D1-D2)x + (E1-E2)y = (F2-F1)
    
    A = C1.D - C2.D
    B = C1.E - C2.E
    C = C2.F - C1.F # 注意 C 是在等號右邊

    # 如果 A=0 且 B=0，表示 D1=D2, E1=E2。圓心相同。
    if np.isclose(A, 0) and np.isclose(B, 0):
        if np.isclose(C, 0):
            return "Infinite intersections (circles are identical)"
        else:
            return "No intersection (concentric circles)"
            
    L_chord = Line(A, B, C)
    
    # 2. 轉化為直線與圓的交點問題 (使用 C1 和 L_chord)
    return intersect_line_circle(L_chord, C1)

def intersect_line_circle(L: Line, C: Circle):
    """
    計算直線 L: Ax + By = C_L 與圓 C: x^2 + y^2 + Dx + Ey + F = 0 的交點。
    使用代入消去法，轉化為一元二次方程。
    """
    
    # 將直線方程 L 表示為其中一個變數的表達式 (例如 x = ...)
    # 選擇消去 B 不為 0 的變數
    
    if np.isclose(L.B, 0): # B 接近 0，即 A 不為 0 (直線為鉛直線 x = C_L/A)
        x_L = L.C / L.A
        # 代入圓 C: (x_L)^2 + y^2 + D(x_L) + Ey + F = 0
        
        # 整理成 Ay^2 + By + C = 0 的形式
        a = 1.0 # y^2 係數
        b = C.E # y 係數
        c = x_L**2 + C.D * x_L + C.F # 常數項
        
        # 求解 y
        y_solutions = solve_quadratic(a, b, c)
        
        if isinstance(y_solutions, str):
            return y_solutions # 平行或不相交
        else:
            # 構造交點
            intersections = [Point(x_L, y) for y in y_solutions]
            return intersections

    else: # B 不接近 0 (直線為一般線 y = (C_L - Ax)/B)
        # 解出 y = m*x + b_L
        m = -L.A / L.B
        b_L = L.C / L.B
        
        # 代入圓 C: x^2 + (mx+b_L)^2 + Dx + E(mx+b_L) + F = 0
        # 整理成 ax^2 + bx + c = 0
        
        a = 1 + m**2
        b = 2 * m * b_L + C.D + C.E * m
        c = b_L**2 + C.E * b_L + C.F
        
        # 求解 x
        x_solutions = solve_quadratic(a, b, c)
        
        if isinstance(x_solutions, str):
            return x_solutions
        else:
            # 構造交點
            intersections = [Point(x, m * x + b_L) for x in x_solutions]
            return intersections

# 輔助函數：解一元二次方程
def solve_quadratic(a, b, c, tolerance=1e-9):
    """解 ax^2 + bx + c = 0 並處理判別式。"""
    
    discriminant = b**2 - 4 * a * c
    
    if discriminant < -tolerance:
        return "No intersection (imaginary roots)" # 無實數解
    elif np.isclose(discriminant, 0, atol=tolerance):
        # 只有一個解 (相切)
        root = -b / (2 * a)
        return [root]
    else:
        # 兩個解 (相交)
        sqrt_disc = np.sqrt(discriminant)
        root1 = (-b + sqrt_disc) / (2 * a)
        root2 = (-b - sqrt_disc) / (2 * a)
        return [root1, root2]

def get_perpendicular_line(L: Line, P: Point):
    """
    給定直線 L: Ax + By = C 和線外一點 P(xp, yp)，
    返回通過 P 且垂直於 L 的新直線 L_perp。
    
    新直線的法向量 (A_perp, B_perp) 是原直線的法向量 (A, B) 的垂線向量。
    (A, B) 的垂線向量可以是 (-B, A)。
    """
    
    # 1. 決定新直線的法向量 (A_perp, B_perp)
    A_perp = -L.B
    B_perp = L.A
    
    # 2. 決定新直線的常數 C_perp
    # 新直線 L_perp: A_perp * x + B_perp * y = C_perp 必須通過 P(xp, yp)
    C_perp = A_perp * P.x + B_perp * P.y
    
    L_perp = Line(A_perp, B_perp, C_perp)
    
    # 可選：找到垂足
    # 垂足是 L 和 L_perp 的交點
    foot_of_perpendicular = intersect_two_lines(L, L_perp)
    
    return {
        "perpendicular_line": L_perp,
        "foot_of_perpendicular": foot_of_perpendicular
    }


if __name__ == "__main__":
    # 測試範例 1
    L_a = Line(2, 3, 6)
    L_b = Line(4, -3, 6)
    print("1. 兩直線交點測試:")
    print(f"   {L_a} 和 {L_b}: {intersect_two_lines(L_a, L_b)}")
    L_c = Line(1, 1, 1)
    L_d = Line(2, 2, 5) # 平行線
    print(f"   {L_c} 和 {L_d}: {intersect_two_lines(L_c, L_d)}")
    L_e = Line(1, 1, 1)
    L_f = Line(2, 2, 2) # 重合線
    print(f"   {L_e} 和 {L_f}: {intersect_two_lines(L_e, L_f)}\n")

    print("="*40+"\n")

    # 測試範例 2
    # 圓 C_g: (x-1)^2 + y^2 = 9  -> x^2 - 2x + 1 + y^2 = 9 -> x^2 + y^2 - 2x - 8 = 0
    C_g = Circle(-2, 0, -8) 
    # 圓 C_h: (x+1)^2 + y^2 = 9  -> x^2 + 2x + 1 + y^2 = 9 -> x^2 + y^2 + 2x - 8 = 0
    C_h = Circle(2, 0, -8)
    print("2. 兩個圓交點測試:")
    # 預期交點在 x^2 + y^2 - 2x - 8 - (x^2 + y^2 + 2x - 8) = 0 -> -4x = 0 -> x=0
    # x=0 代入 (0-1)^2 + y^2 = 9 -> 1 + y^2 = 9 -> y^2 = 8 -> y = +- sqrt(8)
    print(f"   {C_g} 和 {C_h}: {intersect_two_circles(C_g, C_h)}\n")

    print("="*40+"\n")

    # 測試範例 3
    # 圓 C_i: x^2 + y^2 = 25 -> D=0, E=0, F=-25
    C_i = Circle(0, 0, -25) 
    # 直線 L_j: y = 2x - 5 -> 2x - y = 5
    L_j = Line(2, -1, 5)
    print("3. 直線與圓交點測試:")
    # 預期交點：(0, -5) 和 (4, 3)
    print(f"   {L_j} 和 {C_i}: {intersect_line_circle(L_j, C_i)}")

    # 切線測試：圓 C_i 和直線 x=5 (5x + 0y = 25)
    L_k = Line(1, 0, 5) 
    print(f"   {L_k} 和 {C_i} (切線): {intersect_line_circle(L_k, C_i)}")

    # 不相交測試：圓 C_i 和直線 x=10
    L_l = Line(1, 0, 10)
    print(f"   {L_l} 和 {C_i} (不相交): {intersect_line_circle(L_l, C_i)}\n")

    print("="*40+"\n")
    # 測試範例 4
    # 直線 L_m: 2x + 3y = 6
    L_m = Line(2, 3, 6)
    # 線外點 P_n: (5, 4)
    P_n = Point(5, 4)

    # 預期垂直線: -3x + 2y = -3(5) + 2(4) = -15 + 8 = -7
    # 預期垂足：(33/13, 4/13) ≈ (2.5385, 0.3077) (來自前一個答案的計算)
    result = get_perpendicular_line(L_m, P_n)

    print("4. 過線外一點作垂直線測試:")
    print(f"   原直線 L: {L_m}")
    print(f"   線外點 P: {P_n}")
    print(f"   垂直線 L_perp: {result['perpendicular_line']}")
    print(f"   垂足 Q (交點): {result['foot_of_perpendicular']}")