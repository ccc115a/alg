"""2D transformation module."""

import numpy as np

from ..point import Point
from ..vector import Vector


class Transform2D:
    """2D affine transformation: translation, rotation, scaling."""

    def __init__(self, matrix: np.ndarray = None):
        """Initialize transformation.

        Args:
            matrix: 3x3 homogeneous transformation matrix.
                    If None, creates identity transform.
        """
        if matrix is None:
            self._matrix = np.eye(3)
        else:
            self._matrix = np.array(matrix, dtype=float)
            if self._matrix.shape != (3, 3):
                raise ValueError("Transformation matrix must be 3x3")

    @classmethod
    def translation(cls, tx: float, ty: float) -> "Transform2D":
        """Create translation transform."""
        m = np.eye(3)
        m[0, 2] = tx
        m[1, 2] = ty
        return cls(m)

    @classmethod
    def rotation(cls, angle: float) -> "Transform2D":
        """Create rotation transform (radians)."""
        c, s = np.cos(angle), np.sin(angle)
        m = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)
        return cls(m)

    @classmethod
    def scaling(cls, sx: float, sy: float) -> "Transform2D":
        """Create scaling transform."""
        m = np.diag([sx, sy, 1])
        return cls(m)

    @classmethod
    def scaling_uniform(cls, s: float) -> "Transform2D":
        """Create uniform scaling transform."""
        return cls.scaling(s, s)

    def apply_point(self, p: Point) -> Point:
        """Apply transform to a point."""
        if p.n != 2:
            raise ValueError("Point must be 2D")
        h = np.array([p.x, p.y, 1])
        h2 = self._matrix @ h
        return Point(h2[0], h2[1])

    def apply_vector(self, v: Vector) -> Vector:
        """Apply transform to a vector (no translation)."""
        if v.n != 2:
            raise ValueError("Vector must be 2D")
        h = np.array([v.x, v.y, 0])
        h2 = self._matrix @ h
        return Vector(h2[0], h2[1])

    def inverse(self) -> "Transform2D":
        """Return inverse transformation."""
        return Transform2D(np.linalg.inv(self._matrix))

    def __matmul__(self, other: "Transform2D") -> "Transform2D":
        """Compose transformations: self then other."""
        return Transform2D(other._matrix @ self._matrix)

    def __repr__(self) -> str:
        return f"Transform2D(\n{self._matrix})"
