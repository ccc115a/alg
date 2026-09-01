"""Tests for algebra/matrix.py."""

import pytest
import numpy as np
from math4py.algebra import Matrix


class TestMatrixCreation:
    def test_from_list(self):
        m = Matrix([[1, 2], [3, 4]])
        assert m.shape == (2, 2)

    def test_from_numpy(self):
        arr = np.array([[1, 2], [3, 4]])
        m = Matrix(arr)
        assert m.shape == (2, 2)

    def test_eye(self):
        m = Matrix.eye(3)
        assert m.shape == (3, 3)
        assert np.allclose(m._np_mat, np.eye(3))

    def test_zeros(self):
        m = Matrix.zeros((2, 3))
        assert m.shape == (2, 3)
        assert np.allclose(m._np_mat, np.zeros((2, 3)))

    def test_ones(self):
        m = Matrix.ones((2, 2))
        assert m.shape == (2, 2)
        assert np.allclose(m._np_mat, np.ones((2, 2)))


class TestMatrixOperations:
    def test_add(self):
        a = Matrix([[1, 2], [3, 4]])
        b = Matrix([[5, 6], [7, 8]])
        c = a + b
        assert np.allclose(c._np_mat, np.array([[6, 8], [10, 12]]))

    def test_sub(self):
        a = Matrix([[5, 6], [7, 8]])
        b = Matrix([[1, 2], [3, 4]])
        c = a - b
        assert np.allclose(c._np_mat, np.array([[4, 4], [4, 4]]))

    def test_matmul(self):
        a = Matrix([[1, 2], [3, 4]])
        b = Matrix([[5, 6], [7, 8]])
        c = a @ b
        expected = np.array([[19, 22], [43, 50]])
        assert np.allclose(c._np_mat, expected)

    def test_mul_scalar(self):
        a = Matrix([[1, 2], [3, 4]])
        c = a * 2
        assert np.allclose(c._np_mat, np.array([[2, 4], [6, 8]]))


class TestMatrixMethods:
    def test_transpose(self):
        m = Matrix([[1, 2, 3], [4, 5, 6]])
        t = m.T
        assert t.shape == (3, 2)
        assert np.allclose(t._np_mat, np.array([[1, 4], [2, 5], [3, 6]]))

    def test_det(self):
        m = Matrix([[1, 2], [3, 4]])
        assert abs(m.det() - (-2.0)) < 1e-9

    def test_inv(self):
        m = Matrix([[1, 2], [3, 4]])
        inv = m.inv()
        expected = np.linalg.inv(np.array([[1, 2], [3, 4]]))
        assert np.allclose(inv._np_mat, expected)

    def test_eig(self):
        m = Matrix([[1, 2], [2, 1]])
        vals, vecs = m.eig()
        assert len(vals) == 2
        assert np.allclose(sorted(vals), sorted([3, -1]))

    def test_svd(self):
        m = Matrix([[1, 2], [3, 4]])
        U, S, Vh = m.svd()
        assert U.shape == (2, 2)
        assert len(S) == 2
        assert Vh.shape == (2, 2)

    def test_rank(self):
        m = Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        assert m.rank() == 2

    def test_solve(self):
        A = Matrix([[2, 1], [1, 3]])
        b = np.array([5, 6])
        x = A.solve(b)
        assert np.allclose(x._np_mat, np.array([1.8, 1.4]))

    def test_qr(self):
        m = Matrix([[1, 2], [3, 4], [5, 6]])
        Q, R = m.qr()
        assert Q.shape == (3, 2)
        assert R.shape == (2, 2)


class TestMatrixClassMethods:
    def test_random(self):
        m = Matrix.random((3, 4), low=0, high=1)
        assert m.shape == (3, 4)
