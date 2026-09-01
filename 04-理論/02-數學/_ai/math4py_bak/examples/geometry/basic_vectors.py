"""Basic Vector Operations - Example for math4py.geometry."""

import math4py.geometry as geom


def main():
    print("=== Basic Vector Operations ===\n")

    v1 = geom.Vector(1, 0, 0)
    v2 = geom.Vector(0, 1, 0)
    v3 = geom.Vector(0, 0, 1)

    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v3 = {v3}\n")

    print("--- Addition ---")
    result = v1 + v2
    print(f"v1 + v2 = {result}")

    print("\n--- Subtraction ---")
    result = v1 - v2
    print(f"v1 - v2 = {result}")

    print("\n--- Scalar Multiplication ---")
    result = v1 * 3
    print(f"v1 * 3 = {result}")

    print("\n--- Dot Product ---")
    dot = v1.dot(v2)
    print(f"v1 · v2 = {dot}")

    dot = v1.dot(v1)
    print(f"v1 · v1 = {dot}")

    print("\n--- Cross Product ---")
    result = v1.cross(v2)
    print(f"v1 × v2 = {result}")

    result = v2.cross(v3)
    print(f"v2 × v3 = {result}")

    print("\n--- Norm (Length) ---")
    v = geom.Vector(3, 4, 0)
    print(f"||{v}|| = {v.norm()}")

    print("\n--- Normalize ---")
    u = v.normalize()
    print(f"normalize({v}) = {u} (length = {u.norm()})")

    print("\n--- Angle Between Vectors ---")
    angle = v1.angle_to(v2)
    print(f"Angle between v1 and v2: {angle:.4f} rad ({angle/np.pi*180:.2f}°)")
    angle = v1.angle_to(v3)
    print(f"Angle between v1 and v3: {angle:.4f} rad ({angle/np.pi*180:.2f}°)")

    print("\n--- Parallel & Perpendicular Check ---")
    v4 = geom.Vector(2, 0, 0)
    v5 = geom.Vector(0, 1, 0)
    print(f"Is v1 parallel to v4? {v1.is_parallel(v4)}")
    print(f"Is v1 parallel to v5? {v1.is_parallel(v5)}")
    print(f"Is v1 perpendicular to v5? {v1.is_perpendicular(v5)}")


if __name__ == "__main__":
    import numpy as np
    main()