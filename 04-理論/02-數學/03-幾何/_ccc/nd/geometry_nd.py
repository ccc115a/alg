import numpy as np

# --- 向量和點的基礎類 ---

class Vector:
    """表示 N 維空間中的向量"""
    def __init__(self, components):
        """
        初始化一個向量。
        :param components: 向量的分量，可以是列表、元組或 numpy 陣列。
        """
        self.components = np.array(components, dtype=float)
        self.ndim = len(self.components)

    # 運算子重載：加法
    def __add__(self, other):
        if not isinstance(other, Vector) or self.ndim != other.ndim:
            raise ValueError("Addition must be between two vectors of the same dimension.")
        return Vector(self.components + other.components)

    # 運算子重載：減法
    def __sub__(self, other):
        if not isinstance(other, Vector) or self.ndim != other.ndim:
            raise ValueError("Subtraction must be between two vectors of the same dimension.")
        return Vector(self.components - other.components)

    # 運算子重載：數乘 (左乘)
    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Multiplication must be with a scalar.")
        return Vector(self.components * scalar)

    # 運算子重載：數乘 (右乘)
    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # 運算子重載：除法 (數除)
    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)) or scalar == 0:
            raise ValueError("Division must be by a non-zero scalar.")
        return Vector(self.components / scalar)

    # 運算子重載：負號
    def __neg__(self):
        return Vector(-self.components)

    # 運算子重載：字串表示
    def __repr__(self):
        return f"Vector({list(self.components)}) in {self.ndim}D"

    # 點積 (內積)
    def dot(self, other):
        """計算與另一個向量的點積。"""
        if not isinstance(other, Vector) or self.ndim != other.ndim:
            raise ValueError("Dot product must be between two vectors of the same dimension.")
        return np.dot(self.components, other.components)

    # 範數 (長度)
    @property
    def magnitude(self):
        """計算向量的 L2 範數（長度）。"""
        return np.linalg.norm(self.components)

    # 單位向量
    @property
    def normalize(self):
        """計算與其方向相同的單位向量。"""
        mag = self.magnitude
        if mag == 0:
            raise ValueError("Cannot normalize a zero vector.")
        return Vector(self.components / mag)

class Point:
    """表示 N 維空間中的點"""
    def __init__(self, coordinates):
        """
        初始化一個點。
        :param coordinates: 點的坐標，可以是列表、元組或 numpy 陣列。
        """
        self.coordinates = np.array(coordinates, dtype=float)
        self.ndim = len(self.coordinates)

    def __repr__(self):
        return f"Point({list(self.coordinates)}) in {self.ndim}D"

    # 點到點的向量
    def to_vector(self, other):
        """
        計算從此點到另一個點的向量 (other - self)。
        :param other: 另一個 Point 物件。
        :return: Vector 物件。
        """
        if not isinstance(other, Point) or self.ndim != other.ndim:
            raise ValueError("Target must be a Point of the same dimension.")
        return Vector(other.coordinates - self.coordinates)

    # 點加上向量
    def __add__(self, vector):
        """點 + 向量 = 點"""
        if not isinstance(vector, Vector) or self.ndim != vector.ndim:
            raise ValueError("Addition must be with a Vector of the same dimension.")
        return Point(self.coordinates + vector.components)

    # 點減去向量
    def __sub__(self, vector):
        """點 - 向量 = 點"""
        if not isinstance(vector, Vector) or self.ndim != vector.ndim:
            raise ValueError("Subtraction must be with a Vector of the same dimension.")
        return Point(self.coordinates - vector.components)


# --- 幾何形狀類 ---

class Line:
    """表示 N 維空間中的直線 (參數式)"""
    def __init__(self, point, direction_vector):
        """
        初始化一條直線。
        :param point: 直線上的任意一個 Point 物件。
        :param direction_vector: 直線的方向 Vector 物件。
        """
        if point.ndim != direction_vector.ndim:
            raise ValueError("Point and direction vector must have the same dimension.")
        if direction_vector.magnitude == 0:
             raise ValueError("Direction vector cannot be a zero vector.")
             
        self.point = point
        self.direction = direction_vector.normalize # 使用單位向量來規範化
        self.ndim = point.ndim

    def __repr__(self):
        return f"Line in {self.ndim}D (Point: {self.point}, Direction: {self.direction})"

    def get_point_at(self, t):
        """
        根據參數 t 取得直線上的點。
        :param t: 實數參數。
        :return: Point 物件。
        """
        return self.point + (self.direction * t)

# --- 幾何計算函數 ---

def distance(obj1, obj2):
    """
    計算兩個幾何物件之間的距離。
    :param obj1: 第一個物件 (Point, Vector)。
    :param obj2: 第二個物件 (Point, Vector)。
    """
    if isinstance(obj1, Point) and isinstance(obj2, Point):
        if obj1.ndim != obj2.ndim:
            raise ValueError("Points must have the same dimension.")
        # 兩點距離 = 連接向量的長度
        return obj1.to_vector(obj2).magnitude
    
    elif isinstance(obj1, Vector) and isinstance(obj2, Vector):
        if obj1.ndim != obj2.ndim:
            raise ValueError("Vectors must have the same dimension.")
        # 兩向量距離 (差的長度)
        return (obj1 - obj2).magnitude
    
    else:
        raise TypeError("Unsupported object types for distance calculation.")

def angle_between_vectors(vec1, vec2, degrees=False):
    """
    計算兩個向量之間的夾角。
    :param vec1: 第一個 Vector 物件。
    :param vec2: 第二個 Vector 物件。
    :param degrees: 如果為 True，返回角度（度），否則返回弧度。
    :return: 夾角（弧度或度）。
    """
    if vec1.ndim != vec2.ndim:
        raise ValueError("Vectors must have the same dimension.")
    
    # cos(theta) = (v1 . v2) / (|v1| * |v2|)
    dot_product = vec1.dot(vec2)
    mag_product = vec1.magnitude * vec2.magnitude

    if mag_product == 0:
        return 0.0 # 至少有一個零向量，角度沒有意義，返回 0

    cos_theta = dot_product / mag_product
    # 由於浮點數精度，cos_theta 可能略微超出 [-1, 1]，需要進行限制
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    angle_rad = np.arccos(cos_theta)
    
    if degrees:
        return np.degrees(angle_rad)
    return angle_rad

# --- 測試範例 ---

if __name__ == '__main__':
    print("--- N 維歐氏空間幾何套件測試 (3D 範例) ---")

    # 1. Vector 測試
    v1 = Vector([1, 2, 3])
    v2 = Vector([4, -1, 0])
    v3 = Vector([0, 0, 0])

    print(f"v1: {v1}")
    print(f"v2: {v2}")
    
    print(f"v1 + v2: {v1 + v2}")
    print(f"v1 - v2: {v1 - v2}")
    print(f"2 * v1: {2 * v1}")
    print(f"v1 / 2: {v1 / 2}")

    print(f"v1 點積 v2: {v1.dot(v2)}") # 1*4 + 2*(-1) + 3*0 = 2
    print(f"v1 長度: {v1.magnitude:.4f}") # sqrt(1^2 + 2^2 + 3^2) = sqrt(14)
    print(f"v1 單位向量: {v1.normalize}")
    
    # 2. Point 測試
    p1 = Point([10, 20, 30])
    p2 = Point([11, 22, 33])
    
    print(f"\np1: {p1}")
    print(f"p2: {p2}")

    vec_p1_to_p2 = p1.to_vector(p2)
    print(f"p1 到 p2 的向量: {vec_p1_to_p2}")
    
    p3 = p1 + v1
    print(f"p1 + v1: {p3}") # [11, 22, 33]
    
    # 3. 距離函數測試
    dist_p1_p2 = distance(p1, p2)
    print(f"\np1 到 p2 的距離: {dist_p1_p2:.4f}") # 3.7417
    
    # 4. 角度函數測試
    v_i = Vector([1, 0, 0])
    v_j = Vector([0, 1, 0])
    v_diag = Vector([1, 1, 0])
    
    angle_90 = angle_between_vectors(v_i, v_j, degrees=True)
    angle_45 = angle_between_vectors(v_i, v_diag, degrees=True)
    
    print(f"\nv_i 與 v_j 的夾角: {angle_90:.2f}°")
    print(f"v_i 與 v_diag 的夾角: {angle_45:.2f}°")

    # 5. Line 測試
    p_on_line = Point([5, 5, 5])
    v_dir = Vector([1, 1, 1])
    line1 = Line(p_on_line, v_dir)
    
    print(f"\nline1: {line1}")
    print(f"t=0 時的點: {line1.get_point_at(0)}") # 應該是 P
    print(f"t=sqrt(3) 時的點: {line1.get_point_at(np.sqrt(3))}") # 應該是 [6, 6, 6]
    
    # 6. 錯誤處理測試 (解除註釋會引發錯誤)
    # try:
    #     v4 = Vector([1, 2])
    #     v1 + v4 # 緯度不同
    # except ValueError as e:
    #     print(f"\n錯誤測試: {e}")