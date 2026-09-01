"""geometry - N-dimensional geometry module for math4py.

Modules:
- Point, Vector: N-dimensional (generic)
- _2d: 2D-specific (Line2D, Transform2D)
- _3d: 3D-specific (Line3D, Plane3D)
"""

from ._2d import Line2D, Transform2D
from ._3d import Line3D, Plane3D
from .point import Point
from .vector import Vector

__all__ = ["Point", "Vector", "Line2D", "Line3D", "Plane3D", "Transform2D"]
