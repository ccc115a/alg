"""幾何定理。

幾何學的重要定理。
"""

import math
from .point import Point
from .vector import Vector


def pythagorean_theorem(a: float, b: float) -> float:
    """畢氏定理。

    c² = a² + b²

    Args:
        a: 股
        b: 勾

    Returns:
        弦
    """
    return math.sqrt(a * a + b * b)


def distance_formula(p1: Point, p2: Point) -> float:
    """距離公式。

    d = √((x2-x1)² + (y2-y1)²)

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        距離
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)


def midpoint_formula(p1: Point, p2: Point) -> Point:
    """中點公式。

    M = ((x1+x2)/2, (y1+y2)/2)

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        中點
    """
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


def slope_formula(p1: Point, p2: Point) -> float:
    """斜率公式。

    m = (y2-y1) / (x2-x1)

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        斜率
    """
    if p2.x == p1.x:
        raise ValueError("Vertical line")
    return (p2.y - p1.y) / (p2.x - p1.x)


def area_triangle_heron(a: float, b: float, c: float) -> float:
    """海龍公式 (三角形面積)。

    s = (a+b+c)/2
    A = √(s(s-a)(s-b)(s-c))

    Args:
        a, b, c: 邊長

    Returns:
        面積
    """
    s = (a + b + c) / 2
    area_sq = s * (s - a) * (s - b) * (s - c)
    if area_sq <= 0:
        return 0.0
    return math.sqrt(area_sq)


def law_of_cosine(a: float, b: float, angle_c: float) -> float:
    """餘弦定理。

    c² = a² + b² - 2ab cos(C)

    Args:
        a: 邊 a
        b: 邊 b
        angle_c: 夾角 C (弧度)

    Returns:
        邊 c
    """
    return math.sqrt(a * a + b * b - 2 * a * b * math.cos(angle_c))


def law_of_sine(a: float, angle_a: float, angle_b: float) -> float:
    """正弦定理。

    a/sin(A) = b/sin(B) = c/sin(C)

    Args:
        a: 邊 a
        angle_a: 角 A (弧度)
        angle_b: 角 B (弧度)

    Returns:
        邊 b
    """
    return a * math.sin(angle_b) / math.sin(angle_a)


def euler_theorem(poly_order: int, poly_edges: int, poly_faces: int) -> int:
    """Euler 多面體定理。

    V - E + F = 2

    Args:
        poly_order: 頂點數 V
        poly_edges: 邊數 E
        poly_faces: 面數 F

    Returns:
        V - E + F
    """
    return poly_order - poly_edges + poly_faces


def heron_maximizer(triangles: list) -> tuple:
    """Heron 最優三角形 (最大面積)。

    等腰三角形面積最大

    Args:
        triangles: 三角形列表

    Returns:
        最大面積三角形
    """
    max_area = 0
    max_tri = None
    for tri in triangles:
        a, b, c = tri
        s = (a + b + c) / 2
        area_sq = s * (s - a) * (s - b) * (s - c)
        if area_sq > max_area:
            max_area = area_sq
            max_tri = tri
    return max_tri


def angle_sum_triangle() -> float:
    """三角形內角和 = π。

    Returns:
        內角和 (弧度)
    """
    return math.pi


def angle_sum_polygon(n: int) -> float:
    """n 邊形內角和。

    (n-2) * π

    Args:
        n: 邊數

    Returns:
        內角和 (弧度)
    """
    return (n - 2) * math.pi


def interior_angle(n: int) -> float:
    """正 n 邊形內角。

    (n-2) * π / n

    Args:
        n: 邊數

    Returns:
        內角 (弧度)
    """
    return (n - 2) * math.pi / n


__all__ = [
    "pythagorean_theorem",
    "distance_formula",
    "midpoint_formula",
    "slope_formula",
    "area_triangle_heron",
    "law_of_cosine",
    "law_of_sine",
    "euler_theorem",
    "heron_maximizer",
    "angle_sum_triangle",
    "angle_sum_polygon",
    "interior_angle",
]