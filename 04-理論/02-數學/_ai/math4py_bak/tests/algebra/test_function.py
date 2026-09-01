"""Tests for algebra/function.py."""

import pytest
import math
from math4py.algebra.function import (
    det,
    inverse_2x2,
    matrix_multiply,
    matrix_add,
    matrix_scalar_mul,
    transpose,
    trace,
    norm_vector,
    dot_product,
    cross_product,
    polynomial_eval,
    polynomial_add,
    polynomial_multiply,
)


class TestMatrixFunctions:
    def test_det(self):
        m = [[1, 2], [3, 4]]
        assert det(m) == -2

    def test_inverse_2x2(self):
        m = [[4, 7], [2, 6]]
        inv = inverse_2x2(m)
        assert abs(inv[0][0] - 0.6) < 1e-9
        assert abs(inv[0][1] - (-0.7)) < 1e-9
        assert abs(inv[1][0] - (-0.2)) < 1e-9
        assert abs(inv[1][1] - 0.4) < 1e-9

    def test_matrix_multiply(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        result = matrix_multiply(A, B)
        assert result == [[19, 22], [43, 50]]

    def test_matrix_add(self):
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        result = matrix_add(A, B)
        assert result == [[6, 8], [10, 12]]

    def test_matrix_scalar_mul(self):
        A = [[1, 2], [3, 4]]
        result = matrix_scalar_mul(A, 2)
        assert result == [[2, 4], [6, 8]]

    def test_transpose(self):
        A = [[1, 2, 3], [4, 5, 6]]
        result = transpose(A)
        assert result == [[1, 4], [2, 5], [3, 6]]

    def test_trace(self):
        A = [[1, 2], [3, 4]]
        assert trace(A) == 5


class TestVectorFunctions:
    def test_norm_vector(self):
        v = [3, 4]
        assert norm_vector(v) == 5.0

    def test_dot_product(self):
        v1 = [1, 2, 3]
        v2 = [4, 5, 6]
        assert dot_product(v1, v2) == 32

    def test_cross_product(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        result = cross_product(v1, v2)
        assert result == [0, 0, 1]


class TestPolynomialFunctions:
    def test_polynomial_eval(self):
        coeffs = [2, 3, 1]  # 2x² + 3x + 1
        assert polynomial_eval(coeffs, 2) == 15

    def test_polynomial_add(self):
        p1 = [1, 2]  # x + 2
        p2 = [1, 1, 1]  # x² + x + 1
        result = polynomial_add(p1, p2)
        assert result == [1.0, 2.0, 3.0]

    def test_polynomial_multiply(self):
        p1 = [1, 1]  # x + 1
        p2 = [1, -1]  # x - 1
        result = polynomial_multiply(p1, p2)
        assert result == [1, 0, -1]