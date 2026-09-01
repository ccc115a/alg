"""Point class for N-dimensional points."""

import numpy as np

from .vector import Vector


class Point:
    """An N-dimensional point class supporting basic geometric operations.

    Usage:
        Point(1, 2, 3)       # 3D point
        Point([1, 2, 3])     # 3D point from list/array
        Point(1, 2)          # 2D point
        Point([1, 2])        # 2D point from list/array
    """

    def __init__(self, *coords):
        """Initialize a point.

        Args:
            *coords: Either individual coordinates (Point(1, 2, 3))
                     or a single list/array (Point([1, 2, 3]))
        """
        if (
            len(coords) == 1
            and hasattr(coords[0], "__iter__")
            and not isinstance(coords[0], (int, float, np.number))
        ):
            self._data = np.array(coords[0], dtype=float)
        else:
            self._data = np.array(coords, dtype=float)

    @property
    def n(self) -> int:
        """Dimension of the point."""
        return len(self._data)

    @property
    def x(self) -> float:
        return self._data[0] if self.n >= 1 else None

    @property
    def y(self) -> float:
        return self._data[1] if self.n >= 2 else None

    @property
    def z(self) -> float:
        return self._data[2] if self.n >= 3 else None

    def __repr__(self) -> str:
        if self.n == 2:
            return f"Point({self.x}, {self.y})"
        return f"Point({', '.join(str(c) for c in self._data)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return False
        return np.allclose(self._data, other._data)

    def __add__(self, other: Vector) -> "Point":
        if not isinstance(other, Vector):
            return NotImplemented
        return Point(self._data + other._data)

    def __sub__(self, other: "Point | Vector") -> "Point | Vector":
        if isinstance(other, Vector):
            return Point(self._data - other._data)
        if isinstance(other, Point):
            return Vector(self._data - other._data)
        return NotImplemented

    def distance_to(self, other: "Point") -> float:
        """Compute distance to another point."""
        if not isinstance(other, Point):
            return NotImplemented
        return float(np.linalg.norm(self._data - other._data))

    def to_vector(self) -> Vector:
        """Convert to vector from origin."""
        return Vector(self._data)

    def to_array(self) -> np.ndarray:
        """Return as numpy array."""
        return self._data.copy()

    def __getitem__(self, i: int) -> float:
        """Access coordinate by index."""
        return self._data[i]
