"""Line3D class for 3D lines."""

from ..point import Point
from ..vector import Vector


class Line3D:
    """A 3D line class defined by a point and direction vector."""

    def __init__(self, point: Point, direction: Vector):
        """Initialize a line.

        Args:
            point: A point on the line
            direction: Direction vector of the line
        """
        if not isinstance(point, Point):
            raise TypeError("point must be a Point instance")
        if not isinstance(direction, Vector):
            raise TypeError("direction must be a Vector instance")
        if direction.norm() < 1e-9:
            raise ValueError("Direction vector cannot be zero")
        self._point = point
        self._direction = direction.normalize()

    @property
    def point(self) -> Point:
        """Return a point on the line."""
        return self._point

    @property
    def direction(self) -> Vector:
        """Return the direction vector (unit)."""
        return self._direction

    def __repr__(self) -> str:
        return f"Line3D({self._point}, {self._direction})"

    def point_at(self, t: float) -> Point:
        """Get point at parameter t: P = P0 + t*d."""
        if not isinstance(t, (int, float)):
            return NotImplemented
        result = self._point.to_array() + t * self._direction.to_array()
        return Point(result[0], result[1], result[2])

    def distance_to_point(self, p: Point) -> float:
        """Compute distance from point to line."""
        if not isinstance(p, Point):
            return NotImplemented
        v = p - self._point
        cross = v.cross(self._direction)
        return cross.norm()

    def closest_point(self, p: Point) -> Point:
        """Find the closest point on line to given point."""
        if not isinstance(p, Point):
            return NotImplemented
        v = p - self._point
        t = v.dot(self._direction)
        return self.point_at(t)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> "Line3D":
        """Create line passing through two points."""
        if not isinstance(p1, Point) or not isinstance(p2, Point):
            raise TypeError("Both arguments must be Point instances")
        direction = p2 - p1
        return cls(p1, direction)

    def is_parallel_to(self, other: "Line3D", tol: float = 1e-9) -> bool:
        """Check if lines are parallel."""
        if not isinstance(other, Line3D):
            return False
        return self._direction.is_parallel(other._direction, tol)

    def is_perpendicular_to(self, other: "Line3D", tol: float = 1e-9) -> bool:
        """Check if lines are perpendicular."""
        if not isinstance(other, Line3D):
            return False
        return self._direction.is_perpendicular(other._direction, tol)
