import numpy as np
import math

# 為了方便，我們將 2D 點和向量都表示為 numpy 陣列
Vector2D = np.ndarray 
Point = Vector2D

# --- 1. 定義幾何物件 ---

class Line:
    """直線：以向量參數式 r(t) = p + t*d 定義"""
    def __init__(self, p: Point, direction: Vector2D):
        self.p = p                   # 直線上的已知點 (起點)
        self.direction = direction   # 方向向量

class Circle:
    """圓：以圓心和半徑定義"""
    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius

class Triangle:
    """三角形：以三個頂點定義"""
    def __init__(self, A: Point, B: Point, C: Point):
        self.A = A
        self.B = B
        self.C = C

# 輔助函式：計算 2D 向量的叉積 (結果是 Z 軸分量，一個純量)
def cross_product_2d(v1: Vector2D, v2: Vector2D) -> float:
    """計算 2D 向量的叉積（返回 Z 分量）"""
    return v1[0] * v2[1] - v1[1] * v2[0]

def intersect_line_line(L1: Line, L2: Line) -> Point | None:
    """計算兩直線交點 (L1: p1 + t*d1, L2: p2 + s*d2)"""
    d1, d2 = L1.direction, L2.direction
    p1, p2 = L1.p, L2.p
    
    # 判斷是否平行 (叉積接近 0)
    denominator = cross_product_2d(d1, d2)
    if np.isclose(denominator, 0):
        return None  # 平行或重合

    # 計算參數 t
    p2_minus_p1 = p2 - p1
    t = cross_product_2d(p2_minus_p1, d2) / denominator
    
    # 計算交點
    intersection_point = p1 + t * d1
    return intersection_point

def get_perpendicular_foot(Q: Point, L: Line) -> Point:
    """計算點 Q 到直線 L 上的垂足 (Pr)"""
    d = L.direction
    p0 = L.p
    
    # 向量 p0Q
    p0Q = Q - p0
    
    # 點積計算參數 t：t = (p0Q . d) / (d . d)
    d_sq = np.dot(d, d)
    if np.isclose(d_sq, 0):
        # 方向向量為零，視為無窮多垂線，返回 p0
        return p0

    t = np.dot(p0Q, d) / d_sq
    
    # 垂足 Pr = p0 + t * d
    foot = p0 + t * d
    return foot

def intersect_line_circle(L: Line, C: Circle) -> list[Point]:
    """計算直線 L 與圓 C 的交點"""
    # 1. 計算圓心 C 到直線 L 的垂足 (Pr)
    Pr = get_perpendicular_foot(C.center, L)
    
    # 2. 計算距離 h (圓心到直線的距離)
    h_sq = np.linalg.norm(Pr - C.center)**2
    R_sq = C.radius**2
    
    if h_sq > R_sq + 1e-9: # 考慮浮點數誤差
        return [] # 無交點
    
    # 3. 計算交點到垂足的距離 (L_side)
    L_side = math.sqrt(max(0, R_sq - h_sq))
    
    # 4. 獲取直線的方向單位向量 e
    e = L.direction / np.linalg.norm(L.direction)
    
    if np.isclose(L_side, 0):
        # 剛好相切
        return [Pr]
    else:
        # 兩個交點
        I1 = Pr + L_side * e
        I2 = Pr - L_side * e
        return [I1, I2]

def intersect_circle_circle(C1: Circle, C2: Circle) -> list[Point]:
    """計算兩個圓 C1 和 C2 的交點"""
    d = np.linalg.norm(C2.center - C1.center) # 圓心距
    r1, r2 = C1.radius, C2.radius
    
    # 判斷關係
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return [] # 外離、內含、或同心

    # 餘弦定理：計算 C1C2I 形成的三角形中，以 r1 為邊所對應的夾角 alpha
    # r2^2 = r1^2 + d^2 - 2*r1*d*cos(alpha)
    # cos(alpha) = (r1^2 + d^2 - r2^2) / (2 * r1 * d)
    
    cos_alpha = (r1**2 + d**2 - r2**2) / (2 * r1 * d)
    
    # 限制 cos_alpha 在 [-1, 1] 以避免浮點誤差導致的 math domain error
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    alpha = math.acos(cos_alpha)

    # 向量 v12 (從 C1 到 C2)
    v12 = C2.center - C1.center
    
    # 向量 v1I (從 C1 到交點 I) 是 v12 旋轉 +/- alpha 角度後，縮放到 r1 長度
    
    # 1. 計算 v12 相對於 X 軸的角度 theta
    theta = math.atan2(v12[1], v12[0]) 

    # 2. 交點角度
    angle1 = theta + alpha
    angle2 = theta - alpha
    
    # 3. 計算交點座標
    I1 = C1.center + r1 * np.array([math.cos(angle1), math.sin(angle1)])
    I2 = C1.center + r1 * np.array([math.cos(angle2), math.sin(angle2)])
    
    if np.isclose(alpha, 0) or np.isclose(alpha, math.pi):
        # 相切 (alpha=0 或 pi)，只有一個交點
        return [I1]
    
    return [I1, I2]

# 垂直線是 Q 和 Pr 之間的線段，其方向向量為 Q - Pr
def create_perpendicular_line(Q: Point, L: Line) -> Line:
    """給定線外一點 Q，返回 Q 到 L 的垂線 (Line 物件)"""
    Pr = get_perpendicular_foot(Q, L)
    # 垂線的方向向量
    perp_direction = Q - Pr
    
    # 垂直線 L_perp: Pr + t * (Q - Pr)
    return Line(p=Pr, direction=perp_direction)

def verify_pythagorean_theorem(Q: Point, L: Line) -> tuple[bool, float]:
    """
    驗證由線外點 Q、垂足 Pr、以及直線上任一點 p0 形成的直角三角形。
    """
    p0 = L.p # 直線 L 上的已知點
    Pr = get_perpendicular_foot(Q, L) # 垂足
    
    # 1. 定義三角形的三個向量/邊
    vec_a = Q - Pr # 直角邊 A (垂線段)
    vec_b = Pr - p0 # 直角邊 B (直線段)
    vec_c = Q - p0 # 斜邊 C (線外點到 p0 的連線)

    # 2. 驗證直角 (vec_a 和 vec_b 應垂直，點積應為 0)
    dot_product = np.dot(vec_a, vec_b)
    is_right_angle = np.isclose(dot_product, 0)

    # 3. 驗證畢氏定理： A^2 + B^2 = C^2
    A_sq = np.dot(vec_a, vec_a)
    B_sq = np.dot(vec_b, vec_b)
    C_sq = np.dot(vec_c, vec_c)
    
    # 檢查 A^2 + B^2 是否等於 C^2
    is_pythagorean = np.isclose(A_sq + B_sq, C_sq)
    
    # 打印結果
    print("\n--- 畢氏定理驗證 ---")
    print(f"直角點積 (a . b): {dot_product} (接近 0: {is_right_angle})")
    print(f"直角邊平方和 (A^2 + B^2): {A_sq + B_sq}")
    print(f"斜邊平方 (C^2): {C_sq}")
    print(f"驗證結果: {is_pythagorean}")
    
    return is_pythagorean, abs(A_sq + B_sq - C_sq)

class Transformations:
    """提供平移、縮放、旋轉的幾何操作"""

    @staticmethod
    def _rotate_point(P: Point, angle_rad: float) -> Point:
        """對點 P 進行旋轉 (相對於原點)"""
        # 2D 旋轉矩陣: [[cos(a), -sin(a)], [sin(a), cos(a)]]
        R = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])
        return R @ P

    @staticmethod
    def translate(obj, T: Vector2D):
        """對幾何物件進行平移"""
        if isinstance(obj, (Line, Circle, Triangle)):
            # 點/圓心/頂點平移，方向向量不變
            if isinstance(obj, Line):
                return Line(obj.p + T, obj.direction)
            elif isinstance(obj, Circle):
                return Circle(obj.center + T, obj.radius)
            elif isinstance(obj, Triangle):
                return Triangle(obj.A + T, obj.B + T, obj.C + T)
        # 處理單點平移
        elif isinstance(obj, np.ndarray):
            return obj + T
        return obj

    @staticmethod
    def scale(obj, S: tuple[float, float]):
        """對幾何物件進行縮放 (相對於原點)"""
        sx, sy = S
        
        if isinstance(obj, (Line, Circle, Triangle)):
            # 縮放所有頂點/中心點/方向向量
            if isinstance(obj, Line):
                return Line(obj.p * [sx, sy], obj.direction * [sx, sy])
            elif isinstance(obj, Circle):
                # 簡單起見，假設是等比例縮放 (sx=sy)
                s = sx 
                return Circle(obj.center * [sx, sy], obj.radius * s)
            elif isinstance(obj, Triangle):
                A_scaled = obj.A * [sx, sy]
                B_scaled = obj.B * [sx, sy]
                C_scaled = obj.C * [sx, sy]
                return Triangle(A_scaled, B_scaled, C_scaled)
        
        # 處理單點縮放
        elif isinstance(obj, np.ndarray):
            return obj * [sx, sy]
        return obj

    @staticmethod
    def rotate(obj, angle_deg: float):
        """對幾何物件進行旋轉 (角度，逆時針)"""
        angle_rad = math.radians(angle_deg)
        
        if isinstance(obj, (Line, Circle, Triangle)):
            # 旋轉所有頂點/中心點/方向向量
            if isinstance(obj, Line):
                return Line(
                    Transformations._rotate_point(obj.p, angle_rad), 
                    Transformations._rotate_point(obj.direction, angle_rad)
                )
            elif isinstance(obj, Circle):
                return Circle(
                    Transformations._rotate_point(obj.center, angle_rad), 
                    obj.radius # 半徑不變
                )
            elif isinstance(obj, Triangle):
                return Triangle(
                    Transformations._rotate_point(obj.A, angle_rad),
                    Transformations._rotate_point(obj.B, angle_rad),
                    Transformations._rotate_point(obj.C, angle_rad)
                )
        
        # 處理單點旋轉
        elif isinstance(obj, np.ndarray):
            return Transformations._rotate_point(obj, angle_rad)
        return obj

# --- 範例執行 ---
if __name__ == "__main__":
    # 範例點
    P_A = np.array([1.0, 1.0])
    P_B = np.array([5.0, 5.0])
    Q_out = np.array([1.0, 7.0])
    
    # 範例直線 (L: 通過 (1, 1) 且方向為 (1, 1)，即 y=x)
    Line1 = Line(p=P_A, direction=P_B - P_A)
    
    # 範例圓
    Circle1 = Circle(center=np.array([4.0, 1.0]), radius=3.0)
    Circle2 = Circle(center=np.array([8.0, 1.0]), radius=5.0)

    # 1. 兩直線交點 (與 L1 垂直的直線 L2: 通過 (1, 7) 且方向為 (-1, 1))
    Line2 = Line(p=Q_out, direction=np.array([-1.0, 1.0]))
    intersection_LL = intersect_line_line(Line1, Line2)
    print(f"1. 兩直線交點 (L1, L2): {intersection_LL}") # 應為 (4, 4)

    # 2. 直線與圓交點
    Line_H = Line(p=np.array([0.0, 1.0]), direction=np.array([1.0, 0.0])) # 水平線 y=1
    intersection_LC = intersect_line_circle(Line_H, Circle1)
    print(f"2. 直線與圓交點 (y=1, C1): {intersection_LC}") # 應為 (1, 1) 和 (7, 1)

    # 3. 兩圓交點
    intersection_CC = intersect_circle_circle(Circle1, Circle2)
    print(f"3. 兩圓交點 (C1, C2): {intersection_CC}") # 應為 (4, 4) 和 (4, -2)

    # 4. 垂足與畢氏定理驗證
    foot = get_perpendicular_foot(Q_out, Line1) # 應為 (4, 4)
    print(f"\n4. 點 {Q_out} 到直線 L1 的垂足: {foot}") 
    
    verify_pythagorean_theorem(Q_out, Line1)
    
    # 5. 變換操作範例
    print("\n--- 幾何物件變換 (Transformations) ---")
    tri = Triangle(np.array([0, 0]), np.array([2, 0]), np.array([1, 3]))
    
    # 平移
    tri_T = Transformations.translate(tri, np.array([10, -5]))
    print(f"5. 平移後的三角形頂點 A': {tri_T.A}") # 應為 (10, -5)
    
    # 旋轉
    point_rotated = Transformations.rotate(P_A, 90) # 旋轉 90 度
    print(f"6. 點 {P_A} 旋轉 90 度: {point_rotated.round(4)}") # 應為 (-1, 1)
