"""Plane Distance and Projection - Example for math4py.geometry."""

import math4py.geometry as geom
from math4py.geometry.threed import Plane, Line


def main():
    print("=== Plane Operations ===\n")

    plane = Plane(
        geom.Point(0, 0, 0),
        geom.Vector(0, 0, 1)
    )
    print(f"Plane: {plane}")
    print(f"Normal: {plane.normal}\n")

    print("--- Point on Plane ---")
    p1 = geom.Point(1, 1, 0)
    print(f"Point {p1} on plane? {plane.contains_point(p1)}")

    print("\n--- Point Above Plane ---")
    p2 = geom.Point(1, 1, 5)
    print(f"Point {p2}")
    print(f"Distance to plane: {plane.distance_to_point(p2)}")
    projected = plane.project_point(p2)
    print(f"Projected: {projected}")

    print("\n--- XY Plane (z=0) ---")
    xy_plane = Plane(
        geom.Point(0, 0, 0),
        geom.Vector(0, 0, 1)
    )
    p3 = geom.Point(3, 4, 7)
    print(f"Point: {p3}")
    print(f"Distance to XY plane: {xy_plane.distance_to_point(p3)}")
    print(f"Projected onto XY plane: {xy_plane.project_point(p3)}")

    print("\n--- Plane from Three Points ---")
    plane2 = Plane.from_points(
        geom.Point(0, 0, 0),
        geom.Point(1, 0, 0),
        geom.Point(0, 1, 0)
    )
    print(f"Plane through (0,0,0), (1,0,0), (0,1,0)")
    print(f"Normal: {plane2.normal}")

    print("\n--- Line Intersection with Plane ---")
    line = Line(
        geom.Point(0, 0, 1),
        geom.Vector(1, 0, -1)
    )
    print(f"Line: {line}")
    intersection = plane.line_intersection(line)
    print(f"Intersection with plane: {intersection}")


if __name__ == "__main__":
    main()