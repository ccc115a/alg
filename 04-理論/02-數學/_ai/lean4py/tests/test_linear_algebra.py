import pytest
import math
from lean4py.linear_algebra import (
    Vector, vector, zero_vector, dot_product, cross_product,
    angle_between, projection,
    Matrix, matrix, identity_matrix, zero_matrix,
    matrix_mul, matrix_vector_mul,
    det, matrix_minor, matrix_inverse, trace,
    rank, nullity, eigenvalues, eigenvectors,
    is_linearly_independent, span, is_orthogonal, is_orthonormal,
    LinearMap, linear_map
)

class TestVector:
    def test_vector_init(self):
        v = Vector(3, [1, 2, 3])
        assert v.dim == 3
        assert v.elements == [1, 2, 3]

    def test_vector_init_error(self):
        with pytest.raises(ValueError):
            Vector(3, [1, 2])

    def test_vector_equality(self):
        assert Vector(3, [1, 2, 3]) == Vector(3, [1, 2, 3])
        assert Vector(3, [1, 2, 3]) != Vector(3, [1, 2, 4])

    def test_vector_add(self):
        u = Vector(3, [1, 2, 3])
        v = Vector(3, [4, 5, 6])
        result = u + v
        assert result.elements == [5, 7, 9]

    def test_vector_sub(self):
        u = Vector(3, [4, 5, 6])
        v = Vector(3, [1, 2, 3])
        result = u - v
        assert result.elements == [3, 3, 3]

    def test_vector_mul(self):
        v = Vector(3, [1, 2, 3])
        result = v * 2
        assert result.elements == [2, 4, 6]

    def test_vector_rmul(self):
        v = Vector(3, [1, 2, 3])
        result = 2 * v
        assert result.elements == [2, 4, 6]

    def test_vector_neg(self):
        v = Vector(3, [1, 2, 3])
        result = -v
        assert result.elements == [-1, -2, -3]

    def test_vector_norm(self):
        v = Vector(3, [3, 4, 0])
        assert abs(v.norm() - 5.0) < 1e-10

    def test_vector_normalize(self):
        v = Vector(3, [3, 4, 0])
        n = v.normalize()
        assert abs(n.norm() - 1.0) < 1e-10

class TestDotProduct:
    def test_dot_product(self):
        u = Vector(3, [1, 2, 3])
        v = Vector(3, [4, 5, 6])
        assert dot_product(u, v) == 32

    def test_dot_product_orthogonal(self):
        u = Vector(3, [1, 0, 0])
        v = Vector(3, [0, 1, 0])
        assert dot_product(u, v) == 0

class TestCrossProduct:
    def test_cross_product(self):
        u = Vector(3, [1, 0, 0])
        v = Vector(3, [0, 1, 0])
        result = cross_product(u, v)
        assert result.elements == [0, 0, 1]

class TestMatrix:
    def test_matrix_init(self):
        M = Matrix(2, 2, [[1, 2], [3, 4]])
        assert M.rows == 2
        assert M.cols == 2

    def test_matrix_init_error(self):
        with pytest.raises(ValueError):
            Matrix(2, 2, [[1, 2, 3], [4, 5, 6]])

    def test_matrix_equality(self):
        A = Matrix(2, 2, [[1, 2], [3, 4]])
        B = Matrix(2, 2, [[1, 2], [3, 4]])
        assert A == B

    def test_matrix_add(self):
        A = Matrix(2, 2, [[1, 2], [3, 4]])
        B = Matrix(2, 2, [[5, 6], [7, 8]])
        C = A + B
        assert C.data == [[6, 8], [10, 12]]

    def test_matrix_sub(self):
        A = Matrix(2, 2, [[5, 6], [7, 8]])
        B = Matrix(2, 2, [[1, 2], [3, 4]])
        C = A - B
        assert C.data == [[4, 4], [4, 4]]

    def test_matrix_mul(self):
        A = Matrix(2, 2, [[1, 2], [3, 4]])
        B = A * 2
        assert B.data == [[2, 4], [6, 8]]

    def test_matrix_transpose(self):
        A = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        AT = A.transpose()
        assert AT.rows == 3
        assert AT.cols == 2
        assert AT.data == [[1, 4], [2, 5], [3, 6]]

class TestMatrixMul:
    def test_matrix_mul(self):
        A = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        B = Matrix(3, 2, [[1, 2], [3, 4], [5, 6]])
        C = matrix_mul(A, B)
        assert C.rows == 2
        assert C.cols == 2
        assert C.data == [[22, 28], [49, 64]]

    def test_matrix_vector_mul(self):
        A = Matrix(2, 3, [[1, 2, 3], [4, 5, 6]])
        v = Vector(3, [1, 1, 1])
        result = matrix_vector_mul(A, v)
        assert result.elements == [6, 15]

class TestDeterminant:
    def test_det_1x1(self):
        A = Matrix(1, 1, [[5]])
        assert det(A) == 5

    def test_det_2x2(self):
        A = Matrix(2, 2, [[1, 2], [3, 4]])
        assert det(A) == -2

    def test_det_3x3(self):
        A = Matrix(3, 3, [[1, 2, 3], [0, 4, 5], [0, 0, 6]])
        assert det(A) == 24

class TestMatrixInverse:
    def test_inverse_2x2(self):
        A = Matrix(2, 2, [[4, 7], [2, 6]])
        A_inv = matrix_inverse(A)
        assert A_inv is not None
        I = matrix_mul(A, A_inv)
        assert abs(I.data[0][0] - 1) < 1e-10
        assert abs(I.data[1][1] - 1) < 1e-10

    def test_inverse_singular(self):
        A = Matrix(2, 2, [[1, 2], [2, 4]])
        A_inv = matrix_inverse(A)
        assert A_inv is None

class TestRankNullity:
    def test_rank_full(self):
        A = Matrix(3, 3, [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        assert rank(A) == 3

    def test_rank_deficient(self):
        A = Matrix(3, 3, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert rank(A) == 2

    def test_nullity(self):
        A = Matrix(3, 3, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert nullity(A) == 1

class TestEigenvalues:
    def test_eigenvalues_2x2(self):
        A = Matrix(2, 2, [[4, -2], [1, 1]])
        eigenvals = eigenvalues(A)
        assert len(eigenvals) == 2

    def test_eigenvalues_identity(self):
        I = identity_matrix(3)
        eigenvals = eigenvalues(I)
        assert all(abs(ev - 1) < 1e-10 for ev in eigenvals)

class TestLinearIndependence:
    def test_independent_vectors(self):
        v1 = Vector(3, [1, 0, 0])
        v2 = Vector(3, [0, 1, 0])
        assert is_linearly_independent([v1, v2]) == True

    def test_dependent_vectors(self):
        v1 = Vector(3, [1, 0, 0])
        v2 = Vector(3, [2, 0, 0])
        assert is_linearly_independent([v1, v2]) == False

    def test_too_many_vectors(self):
        v1 = Vector(2, [1, 0])
        v2 = Vector(2, [0, 1])
        v3 = Vector(2, [1, 1])
        assert is_linearly_independent([v1, v2, v3]) == False

class TestSpan:
    def test_span_basis(self):
        v1 = Vector(3, [1, 0, 0])
        v2 = Vector(3, [0, 1, 0])
        assert span([v1, v2]) == 2

class TestOrthogonal:
    def test_is_orthogonal(self):
        u = Vector(3, [1, 0, 0])
        v = Vector(3, [0, 1, 0])
        assert is_orthogonal(u, v) == True

    def test_is_orthonormal(self):
        e1 = Vector(3, [1, 0, 0])
        e2 = Vector(3, [0, 1, 0])
        e3 = Vector(3, [0, 0, 1])
        assert is_orthonormal([e1, e2, e3]) == True

class TestLinearMap:
    def test_linear_map(self):
        A = Matrix(2, 2, [[1, 0], [0, 1]])
        T = linear_map(A)
        v = Vector(2, [3, 4])
        result = T(v)
        assert result.elements == [3, 4]

class TestIdentityMatrix:
    def test_identity(self):
        I = identity_matrix(3)
        for i in range(3):
            for j in range(3):
                if i == j:
                    assert I.data[i][j] == 1
                else:
                    assert I.data[i][j] == 0