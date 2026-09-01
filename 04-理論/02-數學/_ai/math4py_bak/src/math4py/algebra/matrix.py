"""Matrix - 矩陣運算，包裝 numpy.ndarray 提供一致 API."""

import numpy as np


class Matrix:
    """矩陣類別，包裝 numpy.ndarray。

    提供統一的矩陣運算接口，專注數值計算。
    符號運算請直接使用 sympy.Matrix。
    """

    def __init__(self, data, dtype=None):
        if isinstance(data, np.ndarray):
            self._np_mat = data.astype(dtype) if dtype else data
        else:
            self._np_mat = np.array(data, dtype=dtype)

    @property
    def shape(self):
        return self._np_mat.shape

    @property
    def T(self):
        return Matrix(self._np_mat.T)

    def __add__(self, other):
        if isinstance(other, Matrix):
            return Matrix(self._np_mat + other._np_mat)
        return Matrix(self._np_mat + other)

    def __sub__(self, other):
        if isinstance(other, Matrix):
            return Matrix(self._np_mat - other._np_mat)
        return Matrix(self._np_mat - other)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            return Matrix(self._np_mat @ other._np_mat)
        return Matrix(self._np_mat * other)

    def __matmul__(self, other):
        if isinstance(other, Matrix):
            return Matrix(self._np_mat @ other._np_mat)
        return Matrix(self._np_mat @ other)

    def dot(self, other):
        """矩陣乘法。"""
        return self @ other

    def inv(self):
        """反矩陣。"""
        return Matrix(np.linalg.inv(self._np_mat))

    def det(self):
        """行列式。"""
        return float(np.linalg.det(self._np_mat))

    def eigvals(self):
        """特徵值。"""
        vals, _ = np.linalg.eig(self._np_mat)
        return vals

    def eig(self):
        """特徵值與特徵向量。"""
        vals, vecs = np.linalg.eig(self._np_mat)
        return vals, Matrix(vecs)

    def svd(self, full_matrices=True):
        """奇異值分解 SVD。"""
        U, S, Vh = np.linalg.svd(self._np_mat, full_matrices=full_matrices)
        return Matrix(U), S, Matrix(Vh)

    def rank(self):
        """矩陣秩。"""
        return np.linalg.matrix_rank(self._np_mat)

    def norm(self, ord=None):
        """矩陣範數。"""
        return np.linalg.norm(self._np_mat, ord=ord)

    def solve(self, b):
        """解線性方程組 Ax = b。"""
        if isinstance(b, Matrix):
            b = b._np_mat
        x = np.linalg.solve(self._np_mat, b)
        return Matrix(x)

    def qr(self):
        """QR 分解。"""
        Q, R = np.linalg.qr(self._np_mat)
        return Matrix(Q), Matrix(R)

    def lu(self):
        """LU 分解 (使用 scipy)。"""
        import scipy.linalg
        P, L, U = scipy.linalg.lu(self._np_mat)
        return Matrix(P), Matrix(L), Matrix(U)

    def __repr__(self):
        return f"Matrix(shape={self.shape})"

    def __str__(self):
        return str(self._np_mat)

    @classmethod
    def eye(cls, n):
        """單位矩陣。"""
        return cls(np.eye(n))

    @classmethod
    def zeros(cls, shape):
        """零矩陣。"""
        return cls(np.zeros(shape))

    @classmethod
    def ones(cls, shape):
        """全一矩陣。"""
        return cls(np.ones(shape))

    @classmethod
    def random(cls, shape, low=-1, high=1):
        """隨機矩陣。"""
        return cls(np.random.uniform(low, high, shape))
