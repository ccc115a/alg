import numpy as np
from typing import List, Tuple, Union, Optional
from geometry_nd import Point, Vector, Line

# --- 3D 輔助函數 ---

def ensure_3d(*objects):
    """檢查所有輸入物件是否都是 3D 的。"""
    for obj in objects:
        if hasattr(obj, 'ndim') and obj.ndim != 3:
            raise ValueError(f"{type(obj).__name__} must be 3-dimensional for this operation.")

def cross_product(vec1: Vector, vec2: Vector) -> Vector:
    """計算兩個 3D 向量的外積 (Cross Product)。"""
    ensure_3d(vec1, vec2)
    cross_comp = np.cross(vec1.components, vec2.components)
    return Vector(cross_comp)

def distance(obj1: Point, obj2: Point) -> float:
    """計算兩點之間的距離。"""
    ensure_3d(obj1, obj2)
    return obj1.to_vector(obj2).magnitude

# --- 3D 擴展類 ---

class Plane:
    """表示 3D 空間中的平面"""
    def __init__(self, point: Point, normal_vector: Vector):
        ensure_3d(point, normal_vector)
        if normal_vector.magnitude == 0:
            raise ValueError("Normal vector cannot be a zero vector.")
            
        self.point = point
        self.normal = normal_vector.normalize
        self.ndim = 3
        
        # d = n . P0 (這裡的 P0 是 self.point)
        self.d = self.normal.dot(self.point.to_vector(Point([0, 0, 0])) * -1)

    def __repr__(self):
        n_comp = self.normal.components
        return (f"Plane(Eq: {n_comp[0]:.4f}x + {n_comp[1]:.4f}y + {n_comp[2]:.4f}z = {self.d:.4f})")

    def is_on_plane(self, p: Point, tol: float = 1e-9) -> bool:
        """檢查一個點是否在平面上。"""
        ensure_3d(p)
        vector_P0P = self.point.to_vector(p)
        return np.isclose(self.normal.dot(vector_P0P), 0.0, atol=tol)


class Sphere:
    """表示 3D 空間中的球體"""
    def __init__(self, center: Point, radius: float):
        ensure_3d(center)
        if radius <= 0:
            raise ValueError("Radius must be positive.")
            
        self.center = center
        self.radius = radius
        self.ndim = 3

    def __repr__(self):
        return f"Sphere(C: {self.center}, R: {self.radius:.4f})"

# --- 3D 核心幾何函數 ---

def intersection_plane_plane(plane1: Plane, plane2: Plane) -> Union[Line, str, None]:
    """計算兩平面的交線。"""
    ensure_3d(plane1, plane2)
    n1, n2 = plane1.normal.components, plane2.normal.components
    d1, d2 = plane1.d, plane2.d
    
    # 1. 交線方向向量 (垂直於兩法向量)
    v_dir = Vector(np.cross(n1, n2))
    
    if np.isclose(v_dir.magnitude, 0):
        if plane2.is_on_plane(plane1.point):
            return "Coincident"
        else:
            return None # 平行不重合
            
    # 2. 找到交線上的一個點 P (解 2x3 線性系統)
    A = np.array([n1, n2])
    b = np.array([d1, d2])
    
    # 嘗試將 z=0 帶入
    M_xy = A[:, :2]
    b_xy = b - A[:, 2] * 0
    
    if not np.isclose(np.linalg.det(M_xy), 0):
        xy = np.linalg.solve(M_xy, b_xy)
        point_on_line = Point([xy[0], xy[1], 0.0])
    else:
        # 嘗試將 y=0 帶入
        M_xz = A[:, [0, 2]]
        b_xz = b - A[:, 1] * 0
        if not np.isclose(np.linalg.det(M_xz), 0):
            xz = np.linalg.solve(M_xz, b_xz)
            point_on_line = Point([xz[0], 0.0, xz[1]])
        else:
            # 必須可以解出 (x=0)
            M_yz = A[:, [1, 2]]
            b_yz = b - A[:, 0] * 0
            yz = np.linalg.solve(M_yz, b_yz)
            point_on_line = Point([0.0, yz[0], yz[1]])
            
    return Line(point_on_line, v_dir)

def intersection_line_plane(line: Line, plane: Plane) -> Union[Point, str, None]:
    """計算直線與平面的交點。"""
    ensure_3d(line, plane)
    
    n = plane.normal.components
    u = line.direction.components
    A = line.point.coordinates
    
    # n . u
    n_dot_u = np.dot(n, u)
    
    # n . P0 - n . A
    n_dot_P0_minus_A = plane.d - np.dot(n, A)
    
    if np.isclose(n_dot_u, 0):
        # 平行，檢查是否在平面上
        if np.isclose(n_dot_P0_minus_A, 0):
            return "Line on Plane"
        else:
            return None # 平行不相交
            
    # 存在唯一交點
    t = n_dot_P0_minus_A / n_dot_u
    intersection_coords = A + t * u
    return Point(intersection_coords)

def distance_point_to_plane(point: Point, plane: Plane) -> float:
    """計算點到平面的最短距離。"""
    ensure_3d(point, plane)
    # 距離 = |n . P - d| / |n|。由於 |n|=1，簡化為 |n . P - d|
    n_dot_P = np.dot(plane.normal.components, point.coordinates)
    distance_val = abs(n_dot_P - plane.d)
    return distance_val

def point_projection_on_line(point: Point, line: Line) -> Point:
    """計算點在直線上的投影點 (垂足)。"""
    ensure_3d(point, line)
    A = line.point
    AP = A.to_vector(point)
    u = line.direction # 單位向量
    
    # 投影長度 t = AP . u
    t = AP.dot(u)
    
    # 投影點 Q = A + t*u
    projection_point = A + (u * t)
    
    return projection_point

# --- 測試主程式 ---

def run_3d_geometry_demo():
    """執行 3D 幾何套件的展示。"""
    print("=" * 60)
    print("           3D 歐氏幾何套件展示程式")
    print("=" * 60)
    
    # --- 1. 初始化基本物件 ---
    P_A = Point([1.0, 2.0, 3.0])
    P_B = Point([5.0, 5.0, 5.0])
    P_C = Point([2.0, 2.0, 2.0]) # 在平面 P1 上的一點
    
    V_dir_L = Vector([1.0, 1.0, 0.0]) # 直線方向
    V_norm_P1 = Vector([1.0, 0.0, 0.0]) # 平面 P1 法向量 (垂直於 X 軸)
    V_norm_P2 = Vector([0.0, 1.0, 0.0]) # 平面 P2 法向量 (垂直於 Y 軸)
    
    L1 = Line(P_A, V_dir_L) # 經過 A(1, 2, 3)，方向 (1, 1, 0)
    P1 = Plane(P_C, V_norm_P1) # 經過 C(2, 2, 2)，法向量 (1, 0, 0) => 平面 x = 2
    P2 = Plane(P_A, V_norm_P2) # 經過 A(1, 2, 3)，法向量 (0, 1, 0) => 平面 y = 2
    S1 = Sphere(P_C, 3.0) # 圓心 (2, 2, 2)，半徑 3
    
    print("\n--- [1] 基本物件與屬性 ---")
    print(f"  P_A: {P_A}")
    print(f"  L1: {L1}")
    print(f"  P1: {P1} (x = 2)")
    print(f"  P2: {P2} (y = 2)")
    print(f"  S1: {S1}")
    print(f"  P_A 到 P_B 距離: {distance(P_A, P_B):.4f}")

    # --- 2. 兩平面交線 ---
    print("\n--- [2] 兩平面交線 (P1 與 P2) ---")
    # P1: x=2, P2: y=2 => 交線為 x=2, y=2, z=t (垂直線)
    # 方向應為 (0, 0, 1)，線上任一點 (2, 2, 0)
    intersection_PP = intersection_plane_plane(P1, P2)
    print(f"  P1 & P2 交線: {intersection_PP}")
    
    # --- 3. 線與平面交點 ---
    print("\n--- [3] 線與平面交點 (L1 與 P1) ---")
    # L1: x = 1+t, y = 2+t, z = 3
    # P1: x = 2
    # 1+t = 2 => t = 1
    # 交點應為 (2, 3, 3)
    intersection_LP = intersection_line_plane(L1, P1)
    print(f"  L1 & P1 交點: {intersection_LP}")

    # 4. 點到平面的距離
    print("\n--- [4] 點到平面的距離 (P_B 到 P1) ---")
    # P_B(5, 5, 5), P1(x=2)
    # 距離應為 |5 - 2| = 3
    dist_PB_P1 = distance_point_to_plane(P_B, P1)
    print(f"  P_B 到 P1 的距離: {dist_PB_P1:.4f}")
    
    # 5. 點到線的投影
    print("\n--- [5] 點到線的投影 (P_B 到 L1) ---")
    # L1 方向 (1, 1, 0)
    # 投影計算
    P_proj = point_projection_on_line(P_B, L1)
    print(f"  P_B 在 L1 上的投影點: {P_proj}")
    
    # 驗證：P_proj 到 P_B 的向量 (P_B - P_proj) 應垂直於 L1 的方向 (1, 1, 0)
    vec_proj_to_B = P_proj.to_vector(P_B)
    dot_check = vec_proj_to_B.dot(L1.direction)
    print(f"  投影點與 P_B 的連線向量: {vec_proj_to_B}")
    print(f"  垂直性檢查 (點積): {dot_check:.4e} (應接近 0)")

    # 6. 外積測試
    print("\n--- [6] 外積測試 (Cross Product) ---")
    V_i = Vector([1, 0, 0])
    V_j = Vector([0, 1, 0])
    V_cross = cross_product(V_i, V_j)
    print(f"  V_i x V_j: {V_i} x {V_j} = {V_cross} (應為 (0, 0, 1))")

    # --- 7. 邊界案例測試 ---
    print("\n--- [7] 邊界案例測試 ---")
    P_A_prime = Point([3.0, 3.0, 3.0])
    L_parallel_P1 = Line(P_A_prime, Vector([0, 1, 1])) # 方向垂直 P1 法向量 (1, 0, 0)
    
    # L_parallel_P1 (平行線) 與 P1 (x=2)
    intersection_parallel = intersection_line_plane(L_parallel_P1, P1)
    print(f"  L_parallel_P1 (x=3) 與 P1 (x=2): {intersection_parallel} (應為 None)")
    
    L_on_P1 = Line(P_C, Vector([0, 1, 1])) # 點 P_C(2, 2, 2) 在 P1 上，方向平行 P1
    intersection_on_plane = intersection_line_plane(L_on_P1, P1)
    print(f"  L_on_P1 與 P1: {intersection_on_plane} (應為 'Line on Plane')")


if __name__ == '__main__':
    run_3d_geometry_demo()