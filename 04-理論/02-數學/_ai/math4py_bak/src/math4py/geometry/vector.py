"""Vector class for N-dimensional vectors."""

import numpy as np


class Vector:
    """An N-dimensional vector class supporting basic vector operations.

    Usage:
        Vector(1, 2, 3)       # 3D vector
        Vector([1, 2, 3])     # 3D vector from list/array
        Vector(1, 2)          # 2D vector
        Vector([1, 2])        # 2D vector from list/array
    """

    def __init__(self, *coords):
        """Initialize a vector.

        Args:
            *coords: Either individual components (Vector(1, 2, 3))
                     or a single list/array (Vector([1, 2, 3]))
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
        """Dimension of the vector."""
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
            return f"Vector({self.x}, {self.y})"
        return f"Vector({', '.join(str(c) for c in self._data)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return False
        return np.allclose(self._data, other._data)

    def __add__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self._data + other._data)

    def __sub__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self._data - other._data)

    def __mul__(self, scalar: float) -> "Vector":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(self._data * scalar)

    def __rmul__(self, scalar: float) -> "Vector":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vector":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        if scalar == 0:
            raise ValueError("Division by zero")
        return Vector(self._data / scalar)

    def __neg__(self) -> "Vector":
        return Vector(-self._data)

    def dot(self, other: "Vector") -> float:
        """Compute dot product with another vector."""
        if not isinstance(other, Vector):
            return NotImplemented
        return float(np.dot(self._data, other._data))

    def cross(self, other: "Vector") -> "Vector":
        """Compute cross product with another vector (3D only)."""
        if not isinstance(other, Vector):
            return NotImplemented
        if self.n != 3 or other.n != 3:
            raise ValueError("Cross product is only defined for 3D vectors")
        result = np.cross(self._data, other._data)
        return Vector(result)

    def norm(self) -> float:
        """Return the magnitude (length) of the vector."""
        return float(np.linalg.norm(self._data))

    def normalize(self) -> "Vector":
        """Return the unit vector (normalized)."""
        n = self.norm()
        if n == 0:
            raise ValueError("Cannot normalize zero vector")
        return self / n

    def angle_to(self, other: "Vector") -> float:
        """Return angle in radians to another vector."""
        if not isinstance(other, Vector):
            return NotImplemented
        dot_prod = self.dot(other)
        norms = self.norm() * other.norm()
        if norms == 0:
            raise ValueError("Cannot compute angle with zero vector")
        cos_angle = np.clip(dot_prod / norms, -1.0, 1.0)
        return float(np.arccos(cos_angle))

    def is_parallel(self, other: "Vector", tol: float = 1e-9) -> bool:
        """Check if vectors are parallel."""
        if not isinstance(other, Vector):
            return False
        if self.n != other.n:
            return False
        if self.norm() < tol or other.norm() < tol:
            return False
        cross_norm = self.cross(other).norm() if self.n == 3 else 0
        return cross_norm < tol or abs(self.dot(other)) / (self.norm() * other.norm()) > 1 - tol

    def is_perpendicular(self, other: "Vector", tol: float = 1e-9) -> bool:
        """Check if vectors are perpendicular."""
        if not isinstance(other, Vector):
            return False
        if self.n != other.n:
            return False
        return abs(self.dot(other)) < tol

    def to_array(self) -> np.ndarray:
        """Return as numpy array."""
        return self._data.copy()

    def __getitem__(self, i: int) -> float:
        """Access component by index."""
        return self._data[i]
