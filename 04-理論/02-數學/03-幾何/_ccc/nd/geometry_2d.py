import numpy as np
from typing import List, Tuple, Union, Optional
from geometry_nd import Point, Vector, Line

# --- 2D 擴展類 ---

class Circle:
    """表示 2D 空間中的圓形"""
    def __init__(self, center: Point, radius: float):
        if center.ndim != 2:
            raise ValueError("Circle must be in 2D space (Point dimension must be 2).")
        if radius <= 0:
            raise ValueError("Radius must be positive.")
            
        self.center = center
        self.radius = radius
        self.ndim = 2

    def __repr__(self):
        return f"Circle(Center: {list(self.center.coordinates):.2f}, Radius: {self.radius:.4f})"

# --- 2D 核心幾何函數 ---

def ensure_2d(*objects):
    """檢查所有輸入物件是否都是 2D 的。"""
    for obj in objects:
        if hasattr(obj, 'ndim') and obj.ndim != 2:
            raise ValueError(f"{type(obj).__name__} must be 2-dimensional for this operation.")

def distance(obj1, obj2) -> float:
    """計算兩個 Point 之間的距離。"""
    if isinstance(obj1, Point) and isinstance(obj2, Point):
        ensure_2d(obj1, obj2)
        return obj1.to_vector(obj2).magnitude
    raise TypeError("Unsupported object types for distance calculation.")

def intersection_line_line(line1: Line, line2: Line) -> Union[Optional[Point], str]:
    """計算兩條直線的交點。"""
    ensure_2d(line1, line2)
    A, u = line1.point.coordinates, line1.direction.components
    B, v = line2.point.coordinates, line2.direction.components
    
    M = np.array([[u[0], -v[0]], [u[1], -v[1]]])
    b = B - A
    det = np.linalg.det(M)
    
    if np.isclose(det, 0):
        # 檢查是否重合 (A是否在L2上)
        vec_AB = A - B
        # 檢查 AB 是否平行於 v
        if np.isclose(vec_AB[0] * v[1] - vec_AB[1] * v[0], 0):
            return "Coincident"
        else:
            return None # 平行不重合
    
    t_s = np.linalg.solve(M, b)
    t = t_s[0]
    return Point(A + t * u)

def intersection_line_circle(line: Line, circle: Circle) -> Union[Tuple[Point, Point], Point, None]:
    """計算直線與圓形的交點。"""
    ensure_2d(line, circle)
    A, u = line.point.coordinates, line.direction.components
    C, r = circle.center.coordinates, circle.radius
    
    d = A - C
    a = 1.0 
    b = 2 * np.dot(u, d)
    c = np.dot(d, d) - r**2
    
    discriminant = b**2 - 4 * a * c
    
    if discriminant < 0 and not np.isclose(discriminant, 0):
        return None
    
    if np.isclose(discriminant, 0):
        t = -b / (2 * a)
        return line.get_point_at(t)
    
    sqrt_disc = np.sqrt(discriminant)
    t1 = (-b + sqrt_disc) / (2 * a)
    t2 = (-b - sqrt_disc) / (2 * a)
    
    p1 = line.get_point_at(t1)
    p2 = line.get_point_at(t2)
    return (p1, p2)

def intersection_circle_circle(c1: Circle, c2: Circle) -> Union[Tuple[Point, Point], Point, None, str]:
    """計算兩圓的交點。 (簡化版，省略內切/外切的特殊判斷，只處理兩交點或無交點)"""
    ensure_2d(c1, c2)
    R1, R2 = c1.radius, c2.radius
    P1, P2 = c1.center, c2.center
    d = distance(P1, P2)
    
    if np.isclose(d, 0): return "Coincident" if np.isclose(R1, R2) else None
    
    if d > R1 + R2 or d < abs(R1 - R2):
        if np.isclose(d, R1 + R2) or np.isclose(d, abs(R1 - R2)):
            # 恰好相切 (只返回一個點)
            t = (R1 / d) if d > R1 + R2 else (R1 / d if R1 > R2 else 1 + R2/d)
            if np.isclose(d, R1 + R2):
                 t = R1 / d
                 return P1 + P1.to_vector(P2) * t
            
            # 由於此函數的複雜性，我們只處理最常見的兩種情況
            return None # 為了簡潔，不處理切點
        
        return None
    
    # 兩個交點
    a = (R1**2 - R2**2 + d**2) / (2 * d)
    h_sq = R1**2 - a**2
    if h_sq < 0 and not np.isclose(h_sq, 0): return None
    h = np.sqrt(max(0, h_sq))

    P1_to_P2_unit_vec = P1.to_vector(P2).normalize
    P_a = P1 + (P1_to_P2_unit_vec * a)

    u_x, u_y = P1_to_P2_unit_vec.components
    u_perp = Vector([-u_y, u_x])

    p_int1 = P_a + (u_perp * h)
    p_int2 = P_a + (u_perp * -h)
    
    return (p_int1, p_int2)


def line_parallel_to(point: Point, line: Line) -> Line:
    """過一點對某線做平行線。"""
    ensure_2d(point, line)
    return Line(point, line.direction)

def line_perpendicular_to(point: Point, line: Line) -> Line:
    """過一點對某線做垂直線。"""
    ensure_2d(point, line)
    u_x, u_y = line.direction.components
    u_perp = Vector([-u_y, u_x])
    return Line(point, u_perp)

def pythagorean_theorem_verification(a_components: list, b_components: list):
    """驗證畢氏定理 (假設 a 和 b 垂直)。"""
    if len(a_components) != 2 or len(b_components) != 2: raise ValueError("Vectors must be 2D.")
        
    vec_a = Vector(a_components)
    vec_b = Vector(b_components)
    
    dot_product = vec_a.dot(vec_b)
    
    a_sq = vec_a.magnitude**2
    b_sq = vec_b.magnitude**2
    sum_of_squares = a_sq + b_sq
    
    vec_c = vec_a + vec_b
    c_sq = vec_c.magnitude**2
    
    print("\n\n--- [6] 畢氏定理驗證 ---")
    print(f"  * 兩邊向量點積 (驗證垂直): {dot_product:.4f}")
    print(f"  * 直角邊 |a|^2 = {a_sq:.4f}, |b|^2 = {b_sq:.4f}")
    print(f"  * a^2 + b^2 = {sum_of_squares:.4f}")
    print(f"  * 斜邊 |c|^2 = {c_sq:.4f}")
    
    if np.isclose(sum_of_squares, c_sq):
        print("  ✅ 驗證結果: |a|^2 + |b|^2 近似等於 |c|^2，定理成立。")
    else:
        print("  ❌ 驗證結果: 定理未成立。")

# --- 主程式展示 ---

def run_geometry_demo():
    """執行 2D 幾何套件的展示。"""
    print("=" * 50)
    print("      2D 歐氏幾何套件展示程式")
    print("=" * 50)
    
    # --- 1. 初始化基本物件 ---
    P_A = Point([1.0, 1.0])
    P_B = Point([4.0, 5.0])
    P_C = Point([0.0, 5.0])
    P_Out = Point([10.0, 10.0])
    
    V_dir_1 = Vector([3.0, 4.0]) # 單位向量 (0.6, 0.8)
    V_dir_2 = Vector([1.0, 0.0]) # 水平線
    V_dir_3 = Vector([0.0, 1.0]) # 垂直線

    L1 = Line(P_A, V_dir_1) # 經過 A(1, 1)，方向 (3, 4)
    L2 = Line(P_C, V_dir_2) # 經過 C(0, 5)，方向 (1, 0) -> 水平線 y=5
    
    C1 = Circle(P_A, 5.0) # 圓心 A(1, 1)，半徑 5
    C2 = Circle(P_C, 4.0) # 圓心 C(0, 5)，半徑 4
    
    print("\n--- [1] 基本物件 ---")
    print(f"  P_A: {P_A}")
    print(f"  L1: {L1}")
    print(f"  C1: {C1}")
    print(f"  距離 P_A 到 P_B: {distance(P_A, P_B):.4f}") # 距離 5

    # --- 2. 兩線交點 ---
    print("\n--- [2] 兩線交點 (L1 與 L2) ---")
    # L1: (1, 1) + t*(0.6, 0.8)
    # L2: y=5
    # 1 + 0.8t = 5 => 0.8t = 4 => t = 5
    # x = 1 + 0.6*5 = 4
    # 交點應為 (4, 5) 即 P_B
    intersection_LL = intersection_line_line(L1, L2)
    print(f"  L1 & L2 交點: {intersection_LL}")

    # --- 3. 線與圓交點 ---
    print("\n--- [3] 線與圓交點 (L2 與 C1) ---")
    # C1: (x-1)^2 + (y-1)^2 = 25
    # L2: y = 5
    # (x-1)^2 + (5-1)^2 = 25
    # (x-1)^2 + 16 = 25 => (x-1)^2 = 9
    # x-1 = +/- 3 => x = 4 或 x = -2
    # 交點應為 (4, 5) 和 (-2, 5)
    intersection_LC = intersection_line_circle(L2, C1)
    print(f"  L2 & C1 交點: {intersection_LC}")
    
    # --- 4. 兩圓交點 ---
    print("\n--- [4] 兩圓交點 (C1 與 C2) ---")
    # C1(1, 1), R1=5; C2(0, 5), R2=4
    # 圓心距 d = sqrt(1^2 + 4^2) = sqrt(17) ≈ 4.12
    # R1+R2=9, |R1-R2|=1. 1 < 4.12 < 9, 應有兩交點
    intersection_CC = intersection_circle_circle(C1, C2)
    print(f"  C1 & C2 交點: {intersection_CC}")

    # --- 5. 平行線與垂直線建構 ---
    print("\n--- [5] 歐氏建構 (過 P_Out) ---")
    # 過 P_Out(10, 10) 對 L1 平行
    L_parallel = line_parallel_to(P_Out, L1)
    print(f"  平行線 L_parallel: {L_parallel}")
    
    # 過 P_Out(10, 10) 對 L2 (y=5) 垂直
    L_perp = line_perpendicular_to(P_Out, L2)
    # L2 方向為 (1, 0)，垂直線方向應為 (0, 1)，即 x=10 的垂直線
    print(f"  垂直線 L_perp: {L_perp}")
    
    # 驗證垂直線與 L2 的交點，應為 (10, 5)
    L_perp_intersect_L2 = intersection_line_line(L_perp, L2)
    print(f"  垂直線與 L2 交點: {L_perp_intersect_L2}")
    
    # --- 6. 畢氏定理驗證 (3-4-5) ---
    pythagorean_theorem_verification([3, 0], [0, 4])

if __name__ == '__main__':
    # 為了美觀輸出，重新定義 Vector 和 Point 的 __repr__
    Vector.__repr__ = lambda self: f"V({self.components[0]:.4f}, {self.components[1]:.4f})"
    Point.__repr__ = lambda self: f"P({self.coordinates[0]:.4f}, {self.coordinates[1]:.4f})"
    Line.__repr__ = lambda self: f"Line(P: {self.point}, Dir: {self.direction})"
    Circle.__repr__ = lambda self: f"Circle(C: {self.center}, R: {self.radius:.4f})"

    run_geometry_demo()