"""幾何函數：基本的幾何計算函數。

幾何計算的輔助函數（不是 class，是 functions）。
"""

import math
from .point import Point
from .vector import Vector


def distance(p1: Point, p2: Point) -> float:
    """兩點 Euclidean 距離。

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        距離
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    dz = (p2.z - p1.z) if hasattr(p1, "z") and hasattr(p2, "z") else 0
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def midpoint(p1: Point, p2: Point) -> Point:
    """兩點中點。

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        中點
    """
    return Point(
        (p1.x + p2.x) / 2,
        (p1.y + p2.y) / 2,
        (p1.z + p2.z) / 2 if hasattr(p1, "z") and hasattr(p2, "z") else 0
    )


def slope(p1: Point, p2: Point) -> float:
    """直線斜率 (2D)。

    Args:
        p1: 點 1
        p2: 點 2

    Returns:
        斜率
    """
    if p2.x == p1.x:
        raise ValueError("Vertical line (undefined slope)")
    return (p2.y - p1.y) / (p2.x - p1.x)


def area_triangle(p1: Point, p2: Point, p3: Point) -> float:
    """三角形面積。

    Args:
        p1, p2, p3: 三個頂點

    Returns:
        面積
    """
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    x3, y3 = p3.x, p3.y
    return abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2


def perimeter_triangle(p1: Point, p2: Point, p3: Point) -> float:
    """三角形周長。

    Args:
        p1, p2, p3: 三個頂點

    Returns:
        周長
    """
    return distance(p1, p2) + distance(p2, p3) + distance(p3, p1)


def area_circle(radius: float) -> float:
    """圓面積 = πr²。

    Args:
        radius: 半徑

    Returns:
        面積
    """
    return math.pi * radius * radius


def circumference(radius: float) -> float:
    """圓周長 = 2πr。

    Args:
        radius: 半徑

    Returns:
        周長
    """
    return 2 * math.pi * radius


def volume_sphere(radius: float) -> float:
    """球體積 = (4/3)πr³。

    Args:
        radius: 半徑

    Returns:
        體積
    """
    return (4/3) * math.pi * radius**3


def surface_area_sphere(radius: float) -> float:
    """球表面積 = 4πr²。

    Args:
        radius: 半徑

    Returns:
        表面積
    """
    return 4 * math.pi * radius * radius


def volume_cylinder(radius: float, height: float) -> float:
    """圓柱體積 = πr²h。

    Args:
        radius: 半徑
        height: 高

    Returns:
        體積
    """
    return math.pi * radius**2 * height


def volume_cone(radius: float, height: float) -> float:
    """圓錐體積 = (1/3)πr²h。

    Args:
        radius: 半徑
        height: 高

    Returns:
        體積
    """
    return (1/3) * math.pi * radius**2 * height


__all__ = [
    "distance",
    "midpoint",
    "slope",
    "area_triangle",
    "perimeter_triangle",
    "area_circle",
    "circumference",
    "volume_sphere",
    "surface_area_sphere",
    "volume_cylinder",
    "volume_cone",
]