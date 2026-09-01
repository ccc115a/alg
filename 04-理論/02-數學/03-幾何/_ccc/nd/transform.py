import numpy as np
from typing import List, Tuple, Union, Optional
from geometry_nd import Point, Vector, Line

# --- 幾何變換函數 ---

# --------------------------
# 1. 平移 (Translation)
# --------------------------

def translate_point(point: Point, vector: Vector) -> Point:
    """將點 P 沿著向量 V 平移。"""
    if point.ndim != vector.ndim:
        raise ValueError("Point and Vector must have the same dimension for translation.")
        
    return point + vector

def translate_line(line: Line, vector: Vector) -> Line:
    """將直線 L 沿著向量 V 平移。"""
    if line.ndim != vector.ndim:
        raise ValueError("Line and Vector must have the same dimension for translation.")
        
    new_point = translate_point(line.point, vector)
    # 使用原始方向向量，因為平移不改變線的方向
    original_dir_vec = line.direction * line.direction.magnitude # 由於 Line 內部存儲單位向量，這裡必須重建原始長度
    return Line(new_point, original_dir_vec)

# --------------------------
# 2. 縮放 (Scaling)
# --------------------------

def scale_point(point: Point, factor: float) -> Point:
    """將點 P 相對於原點進行縮放。"""
    scaled_coords = point.coordinates * factor
    return Point(scaled_coords)

def scale_vector(vector: Vector, factor: float) -> Vector:
    """將向量 V 進行縮放。"""
    return vector * factor

def scale_line(line: Line, factor: float) -> Line:
    """將直線 L 相對於原點進行縮放。"""
    new_point = scale_point(line.point, factor)
    
    # 方向向量也必須被縮放
    original_dir_vec = line.direction * line.direction.magnitude 
    new_direction = scale_vector(original_dir_vec, factor)
    
    if new_direction.magnitude == 0:
         raise ValueError("Scaling factor results in a zero direction vector, line definition failed.")
         
    return Line(new_point, new_direction)

# --------------------------
# 3. 旋轉 (Rotation) - 僅限 2D
# --------------------------

def rotate_2d(obj: Union[Point, Vector], angle_rad: float) -> Union[Point, Vector]:
    """將 2D 點或向量相對於原點進行旋轉。"""
    if obj.ndim != 2:
        raise ValueError("Rotation operation is only supported for 2D objects in this function.")
        
    coords = obj.components if isinstance(obj, Vector) else obj.coordinates
    x, y = coords[0], coords[1]
    
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # 旋轉矩陣應用
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    new_coords = [new_x, new_y]
    
    if isinstance(obj, Point):
        return Point(new_coords)
    else:
        return Vector(new_coords)

def rotate_2d_around_point(point: Point, center: Point, angle_rad: float) -> Point:
    """將 2D 點 P 相對於另一個中心點 C 進行旋轉。"""
    if point.ndim != 2 or center.ndim != 2:
        raise ValueError("Objects must be 2D for this rotation function.")
        
    # 1. 平移到原點 (P - C)
    vec_t = center.to_vector(point)
    
    # 2. 在原點旋轉
    vec_rotated = rotate_2d(vec_t, angle_rad)
    
    # 3. 平移回中心 (C + P_t')
    point_rotated = center + vec_rotated
    
    return point_rotated


# 假設 Vector 和 Point 類已定義

def _apply_rotation_matrix(obj: Union[Point, Vector], matrix: np.ndarray) -> Union[Point, Vector]:
    """
    私有輔助函數：將 3x3 旋轉矩陣應用於 3D 點或向量。
    """
    if obj.ndim != 3:
        raise ValueError("Rotation functions are for 3D objects (ndim=3) only.")
        
    coords = obj.components if isinstance(obj, Vector) else obj.coordinates
    
    # 矩陣乘法：[x' y' z'] = [x y z] @ M
    # 或 M @ [x y z]^T (我們使用 NumPy 的標準矩陣乘法 M @ v)
    
    # 將座標向量轉置為列向量 (3x1)
    coords_col = coords.reshape((3, 1))
    
    # 進行矩陣乘法
    new_coords_col = matrix @ coords_col
    
    # 變換回行向量
    new_coords = new_coords_col.flatten()
    
    if isinstance(obj, Point):
        return Point(new_coords)
    else:
        return Vector(new_coords)

def rotate_3d_x(obj: Union[Point, Vector], angle_rad: float) -> Union[Point, Vector]:
    """
    繞 X 軸旋轉 3D 點或向量。
    
    :param obj: 3D Point 或 Vector。
    :param angle_rad: 旋轉角度（弧度）。
    :return: 旋轉後的物件。
    """
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # X 軸旋轉矩陣 M_x
    M_x = np.array([
        [1, 0, 0],
        [0, cos_a, -sin_a],
        [0, sin_a, cos_a]
    ])
    return _apply_rotation_matrix(obj, M_x)

def rotate_3d_y(obj: Union[Point, Vector], angle_rad: float) -> Union[Point, Vector]:
    """
    繞 Y 軸旋轉 3D 點或向量。
    """
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # Y 軸旋轉矩陣 M_y
    M_y = np.array([
        [cos_a, 0, sin_a],
        [0, 1, 0],
        [-sin_a, 0, cos_a]
    ])
    return _apply_rotation_matrix(obj, M_y)

def rotate_3d_z(obj: Union[Point, Vector], angle_rad: float) -> Union[Point, Vector]:
    """
    繞 Z 軸旋轉 3D 點或向量。
    """
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    
    # Z 軸旋轉矩陣 M_z
    M_z = np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])
    return _apply_rotation_matrix(obj, M_z)

def rotate_3d_around_point_x(point: Point, center: Point, angle_rad: float) -> Point:
    """
    將 3D 點 P 繞著中心點 C，並繞 X 軸旋轉。
    """
    # 1. 平移到原點: P_t = P - C
    vec_t = center.to_vector(point)
    P_t = Point(vec_t.components) # 將向量視為相對於原點的點
    
    # 2. 繞 X 軸旋轉
    P_rotated_t = rotate_3d_x(P_t, angle_rad)
    
    # 3. 平移回中心: P' = C + P_rotated_t
    P_rotated_vec = Vector(P_rotated_t.coordinates) # 將旋轉後的點視為向量
    point_rotated = center + P_rotated_vec
    
    return point_rotated

# --------------------------
# 測試程式
# --------------------------

def run_transformation_test():
    print("=" * 60)
    print("      ND 幾何變換功能測試")
    print("=" * 60)

    # --- 1. 平移測試 (3D) ---
    print("\n--- [1] 平移測試 (3D) ---")
    P_start_3d = Point([1.0, 2.0, 3.0])
    V_shift_3d = Vector([10.0, -5.0, 2.0])
    L_start_3d = Line(P_start_3d, Vector([1, 0, 0]))

    P_trans_3d = translate_point(P_start_3d, V_shift_3d)
    L_trans_3d = translate_line(L_start_3d, V_shift_3d)

    print(f"  起始點 P: {P_start_3d}")
    print(f"  平移向量 V: {V_shift_3d}")
    print(f"  平移後 P': {P_trans_3d} (應為 P(11.0, -3.0, 5.0))")
    print(f"  起始線 L: {L_start_3d}")
    print(f"  平移後 L': {L_trans_3d} (方向應不變, P 變為 P')")

    # --- 2. 縮放測試 (3D) ---
    print("\n--- [2] 縮放測試 (3D, 相對於原點) ---")
    P_start_scale = Point([2.0, 4.0, -1.0])
    V_start_scale = Vector([1.0, 1.0, 1.0])
    factor = 2.5

    P_scaled = scale_point(P_start_scale, factor)
    V_scaled = scale_vector(V_start_scale, factor)

    print(f"  起始點 P: {P_start_scale}")
    print(f"  縮放因子: {factor}")
    print(f"  縮放後 P': {P_scaled} (應為 P(5.0, 10.0, -2.5))")
    print(f"  縮放後 V': {V_scaled}")

    # --- 3. 旋轉測試 (2D) ---
    print("\n--- [3] 旋轉測試 (2D) ---")
    P_start_2d = Point([1.0, 0.0]) # 位於 X 軸上
    V_start_2d = Vector([1.0, 0.0])
    
    angle_90_rad = np.pi / 2 # 90 度
    angle_180_rad = np.pi   # 180 度

    # 相對於原點旋轉
    P_rot_90 = rotate_2d(P_start_2d, angle_90_rad)
    V_rot_180 = rotate_2d(V_start_2d, angle_180_rad)

    print(f"  起始 P: {P_start_2d}")
    print(f"  旋轉 90° 後 P': {P_rot_90} (應為 P(0.0, 1.0))")
    print(f"  旋轉 180° 後 V': {V_rot_180} (應為 V(-1.0, 0.0))")

    # 繞非原點中心旋轉
    P_center = Point([5.0, 5.0])
    P_to_rotate = Point([6.0, 5.0]) # 位於中心右邊 1 單位

    P_rot_center = rotate_2d_around_point(P_to_rotate, P_center, angle_90_rad)

    print(f"\n  中心點 C: {P_center}")
    print(f"  待旋轉點 P_rot: {P_to_rotate}")
    print(f"  繞 C 旋轉 90° 後 P': {P_rot_center} (應為 P(5.0, 6.0))")
    

def run_3d_rotation_test():
    print("=" * 60)
    print("      3D 空間旋轉測試 (使用矩陣)")
    print("=" * 60)
    
    P_start = Point([1.0, 0.0, 0.0]) # 位於 X 軸上的點
    V_start = Vector([1.0, 1.0, 0.0]) # 位於 XY 平面上的向量
    angle_90_rad = np.pi / 2 # 90 度
    
    print(f"起始點 P: {P_start}")
    print(f"起始向量 V: {V_start}")
    print(f"旋轉角度: 90° ({angle_90_rad:.4f} 弧度)")
    
    # --- 1. 繞 X 軸旋轉 ---
    P_rot_x = rotate_3d_x(P_start, angle_90_rad)
    V_rot_x = rotate_3d_x(V_start, angle_90_rad)
    
    print("\n--- 繞 X 軸旋轉 (90°) ---")
    print(f"  P' (P 仍在 X 軸上): {P_rot_x} (應為 P(1.0, 0.0, 0.0))")
    print(f"  V' (從 (1, 1, 0) 轉): {V_rot_x} (應為 V(1.0, 0.0, 1.0))")
    
    # --- 2. 繞 Y 軸旋轉 ---
    P_rot_y = rotate_3d_y(P_start, angle_90_rad)
    V_rot_y = rotate_3d_y(V_start, angle_90_rad)
    
    print("\n--- 繞 Y 軸旋轉 (90°) ---")
    print(f"  P' (從 (1, 0, 0) 轉): {P_rot_y} (應為 P(0.0, 0.0, 1.0))")
    print(f"  V' (從 (1, 1, 0) 轉): {V_rot_y} (應為 V(0.0, 1.0, 1.0))")
    
    # --- 3. 繞 Z 軸旋轉 ---
    P_rot_z = rotate_3d_z(P_start, angle_90_rad)
    V_rot_z = rotate_3d_z(V_start, angle_90_rad)
    
    print("\n--- 繞 Z 軸旋轉 (90°) ---")
    print(f"  P' (從 (1, 0, 0) 轉): {P_rot_z} (應為 P(0.0, 1.0, 0.0))")
    print(f"  V' (從 (1, 1, 0) 轉): {V_rot_z} (應為 V(-1.0, 1.0, 0.0))")

    # --- 4. 繞任意點旋轉 (繞 X 軸) ---
    P_center = Point([5.0, 5.0, 5.0])
    P_to_rotate = Point([5.0, 6.0, 5.0]) # 位於中心上方 1 單位
    
    P_rot_center = rotate_3d_around_point_x(P_to_rotate, P_center, angle_90_rad)
    
    print("\n--- 繞中心點 C 旋轉 (繞 X 軸 90°) ---")
    print(f"  中心點 C: {P_center}")
    print(f"  待旋轉點 P_rot: {P_to_rotate}")
    # P_t = (0, 1, 0)。旋轉後 P_t' = (0, 0, 1)。 P' = C + P_t' = (5, 5, 5) + (0, 0, 1) = (5, 5, 6)
    print(f"  旋轉後 P': {P_rot_center} (應為 P(5.0, 5.0, 6.0))")

if __name__ == '__main__':
    run_transformation_test()
    run_3d_rotation_test()
