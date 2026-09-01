"""Plane3D class for 3D planes."""

from ..point import Point
from ..vector import Vector
from .line3d import Line3D


class Plane3D:
    """A 3D plane class defined by a point and normal vector."""

    def __init__(self, point: Point, normal: Vector):
        """Initialize a plane.

        Args:
            point: A point on the plane
            normal: Normal vector of the plane
        """
        if not isinstance(point, Point):
            raise TypeError("point must be a Point instance")
        if not isinstance(normal, Vector):
            raise TypeError("normal must be a Vector instance")
        if normal.norm() < 1e-9:
            raise ValueError("Normal vector cannot be zero")
        self._point = point
        self._normal = normal.normalize()

    @property
    def point(self) -> Point:
        """Return a point on the plane."""
        return self._point

    @property
    def normal(self) -> Vector:
        """Return the normal vector (unit)."""
        return self._normal

    def __repr__(self) -> str:
        return f"Plane({self._point}, {self._normal})"

    def contains_point(self, p: Point, tol: float = 1e-9) -> bool:
        """Check if point lies on the plane."""
        if not isinstance(p, Point):
            return False
        v = p - self._point
        return abs(v.dot(self._normal)) < tol

    def distance_to_point(self, p: Point) -> float:
        """Compute distance from point to plane."""
        if not isinstance(p, Point):
            return NotImplemented
        v = p - self._point
        return abs(v.dot(self._normal))

    def project_point(self, p: Point) -> Point:
        """Project point onto the plane."""
        if not isinstance(p, Point):
            return NotImplemented
        d = self.distance_to_point(p)
        sign = 1 if (p - self._point).dot(self._normal) > 0 else -1
        offset = self._normal * (sign * d)
        return p - offset

    def line_intersection(self, line: Line3D) -> Point | None:
        """Find intersection of plane with line. Returns None if parallel."""
        if not isinstance(line, Line3D):
            return NotImplemented
        denom = line.direction.dot(self._normal)
        if abs(denom) < 1e-9:
            return None
        v = self._point - line.point
        t = v.dot(self._normal) / denom
        return line.point_at(t)

    @classmethod
    def from_points(cls, p1: Point, p2: Point, p3: Point) -> "Plane3D":
        """Create plane passing through three points."""
        if not all(isinstance(p, Point) for p in [p1, p2, p3]):
            raise TypeError("All arguments must be Point instances")
        v1 = p2 - p1
        v2 = p3 - p1
        normal = v1.cross(v2)
        if normal.norm() < 1e-9:
            raise ValueError("Points are collinear, cannot form a plane")
        return cls(p1, normal)

    def is_parallel_to(self, other: "Plane3D", tol: float = 1e-9) -> bool:
        """Check if planes are parallel."""
        if not isinstance(other, Plane3D):
            return False
        return self._normal.is_parallel(other._normal, tol)

    def is_perpendicular_to(self, other: "Plane3D", tol: float = 1e-9) -> bool:
        """Check if planes are perpendicular."""
        if not isinstance(other, Plane3D):
            return False
        return self._normal.is_perpendicular(other._normal, tol)
