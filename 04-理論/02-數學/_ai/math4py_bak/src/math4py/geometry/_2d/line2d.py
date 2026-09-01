"""2D Line class."""

from ..point import Point
from ..vector import Vector


class Line2D:
    """A 2D line class defined by a point and direction vector."""

    def __init__(self, point: Point, direction: Vector):
        """Initialize a 2D line.

        Args:
            point: A 2D point on the line
            direction: 2D direction vector
        """
        if not isinstance(point, Point):
            raise TypeError("point must be a Point instance")
        if not isinstance(direction, Vector):
            raise TypeError("direction must be a Vector instance")
        if direction.n != 2:
            raise ValueError("Direction must be 2D vector")
        if direction.norm() < 1e-9:
            raise ValueError("Direction vector cannot be zero")
        self._point = point
        self._direction = direction.normalize()

    @property
    def point(self) -> Point:
        return self._point

    @property
    def direction(self) -> Vector:
        return self._direction

    def __repr__(self) -> str:
        return f"Line2D({self._point}, {self._direction})"

    def point_at(self, t: float) -> Point:
        """Get point at parameter t: P = P0 + t*d."""
        return Point(self._point.to_array() + t * self._direction.to_array())

    def distance_to_point(self, p: Point) -> float:
        """Compute distance from point to line."""
        if p.n != 2:
            raise ValueError("Point must be 2D")
        v = p - self._point
        return abs(v.x * self._direction.y - v.y * self._direction.x)

    def closest_point(self, p: Point) -> Point:
        """Find the closest point on line to given point."""
        v = p - self._point
        t = v.dot(self._direction)
        return self.point_at(t)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Line2D":
        """Create line passing through two points."""
        if p1.n != 2 or p2.n != 2:
            raise ValueError("Both points must be 2D")
        direction = p2 - p1
        return cls(p1, direction)

    def is_parallel_to(self, other: "Line2D", tol: float = 1e-9) -> bool:
        """Check if lines are parallel."""
        if not isinstance(other, Line2D):
            return False
        return self._direction.is_parallel(other._direction, tol)

    def is_perpendicular_to(self, other: "Line2D", tol: float = 1e-9) -> bool:
        """Check if lines are perpendicular."""
        if not isinstance(other, Line2D):
            return False
        return self._direction.is_perpendicular(other._direction, tol)

    @staticmethod
    def intersection(l1: "Line2D", l2: "Line2D") -> Point | None:
        """Find intersection point of two lines. Returns None if parallel."""
        x1, y1 = l1.point.x, l1.point.y
        dx1, dy1 = l1.direction.x, l1.direction.y
        x2, y2 = l2.point.x, l2.point.y
        dx2, dy2 = l2.direction.x, l2.direction.y

        det = dx1 * dy2 - dy1 * dx2
        if abs(det) < 1e-9:
            return None

        t = ((x2 - x1) * dy2 - (y2 - y1) * dx2) / det
        return l1.point_at(t)
