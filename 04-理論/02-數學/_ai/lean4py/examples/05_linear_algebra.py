#!/usr/bin/env python3
from lean4py.linear_algebra import (
    Vector, vector, zero_vector, dot_product, cross_product,
    angle_between, projection,
    Matrix, matrix, identity_matrix, zero_matrix,
    matrix_mul, matrix_vector_mul,
    det, matrix_inverse, trace,
    rank, nullity, eigenvalues, eigenvectors,
    is_linearly_independent, span, is_orthogonal, is_orthonormal,
    LinearMap, linear_map
)

print("=" * 60)
print("Linear Algebra Module Examples")
print("=" * 60)

print("\n1. Vectors:")
u = Vector(3, [1, 2, 3])
v = Vector(3, [4, 5, 6])
print(f"   u = {u}")
print(f"   v = {v}")
print(f"   u + v = {u + v}")
print(f"   u - v = {u - v}")
print(f"   2 * u = {2 * u}")
print(f"   ||u|| = {u.norm():.4f}")

print("\n2. Dot Product:")
print(f"   u · v = {dot_product(u, v)}")
print(f"   u · u = {dot_product(u, u)}")

print("\n3. Cross Product:")
i = Vector(3, [1, 0, 0])
j = Vector(3, [0, 1, 0])
k = cross_product(i, j)
print(f"   i × j = {k}")

print("\n4. Angle Between Vectors:")
u2 = Vector(3, [1, 0, 0])
v2 = Vector(3, [1, 1, 0])
angle = angle_between(u2, v2)
print(f"   angle between [1,0,0] and [1,1,0] = {angle:.4f} rad ({angle * 180 / 3.14159:.2f}°)")

print("\n5. Projection:")
proj = projection(u, v)
print(f"   proj_u(v) = {proj}")

print("\n6. Matrices:")
A = Matrix(2, 2, [[1, 2], [3, 4]])
B = Matrix(2, 2, [[5, 6], [7, 8]])
print(f"   A = {A}")
print(f"   B = {B}")
print(f"   A + B = {A + B}")
print(f"   A - B = {A - B}")
print(f"   2 * A = {A * 2}")
print(f"   A^T = {A.transpose()}")

print("\n7. Matrix Multiplication:")
C = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
D = Matrix(3, 2, [[1, 2], [3, 4], [5, 6]])
E = matrix_mul(C, D)
print(f"   C (2x3) = {C.data}")
print(f"   D (3x2) = {D.data}")
print(f"   C @ D = {E.data}")

print("\n8. Matrix-Vector Multiplication:")
A2 = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
v3 = Vector(3, [1, 1, 1])
result = matrix_vector_mul(A2, v3)
print(f"   A @ v = {result}")

print("\n9. Determinant:")
A_det = Matrix(2, 2, [[1, 2], [3, 4]])
print(f"   det([[1,2],[3,4]]) = {det(A_det)}")
A3 = Matrix(3, 3, [[1, 2, 3], [0, 4, 5], [0, 0, 6]])
print(f"   det([[1,2,3],[0,4,5],[0,0,6]]) = {det(A3)}")

print("\n10. Matrix Inverse:")
A_inv = Matrix(2, 2, [[4, 7], [2, 6]])
A_inv_result = matrix_inverse(A_inv)
if A_inv_result:
    I = matrix_mul(A_inv, A_inv_result)
    print(f"   A^(-1) = {A_inv_result.data}")
    print(f"   A @ A^(-1) = {I.data}")
    print(f"   (verification: should be identity)")

print("\n11. Trace:")
A_trace = Matrix(3, 3, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"   trace(A) = {trace(A_trace)}")

print("\n12. Rank and Nullity:")
A_rank = Matrix(3, 3, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"   rank(A) = {rank(A_rank)}")
print(f"   nullity(A) = {nullity(A_rank)}")
print(f"   rank + nullity = {rank(A_rank) + nullity(A_rank)} (should be 3)")

print("\n13. Eigenvalues:")
I2 = identity_matrix(2)
print(f"   eigenvalues(I) = {eigenvalues(I2)}")
A_eigen = Matrix(2, 2, [[4, -2], [1, 1]])
eigenvals = eigenvalues(A_eigen)
print(f"   eigenvalues([[4,-2],[1,1]]) = {[round(e, 4) for e in eigenvals]}")

print("\n14. Linear Independence:")
v1 = Vector(2, [1, 0])
v2 = Vector(2, [0, 1])
v3 = Vector(2, [1, 1])
print(f"   {[v1, v2]} linearly independent? {is_linearly_independent([v1, v2])}")
print(f"   {[v1, v3]} linearly independent? {is_linearly_independent([v1, v3])}")

print("\n15. Orthogonality:")
e1 = Vector(3, [1, 0, 0])
e2 = Vector(3, [0, 1, 0])
e3 = Vector(3, [0, 0, 1])
print(f"   e1, e2 orthogonal? {is_orthogonal(e1, e2)}")
print(f"   e1, e2, e3 orthonormal? {is_orthonormal([e1, e2, e3])}")

print("\n16. Identity and Zero Matrices:")
I3 = identity_matrix(3)
Z = zero_matrix(2, 2)
print(f"   I_3 = {I3.data}")
print(f"   Z_2x2 = {Z.data}")

print("\n17. Linear Maps:")
A_map = Matrix(2, 2, [[1, 2], [0, 1]])
T = linear_map(A_map)
v_map = Vector(2, [3, 4])
print(f"   T(v) where A={A_map.data}, v={v_map.elements} = {T(v_map)}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)