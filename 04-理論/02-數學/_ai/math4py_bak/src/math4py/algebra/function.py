"""代數函數：矩陣運算、多項式運算輔助函數。"""

import numpy as np


def det(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def inverse_2x2(matrix):
    d = det(matrix)
    if abs(d) < 1e-10:
        raise ValueError("Singular matrix")
    a = matrix[0][0]
    b = matrix[0][1]
    c = matrix[1][0]
    d_val = matrix[1][1]
    inv_det = 1 / d
    return [[d_val * inv_det, -b * inv_det], [-c * inv_det, a * inv_det]]


def matrix_multiply(A, B):
    m, n = len(A), len(A[0])
    p = len(B[0])
    result = [[0] * p for _ in range(m)]
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result


def matrix_add(A, B):
    nrows = len(A)
    ncols = len(A[0])
    result = []
    for i in range(nrows):
        row = []
        for j in range(ncols):
            row.append(A[i][j] + B[i][j])
        result.append(row)
    return result


def matrix_scalar_mul(A, scalar):
    result = []
    for row in A:
        result.append([scalar * a for a in row])
    return result


def transpose(A):
    nrows = len(A)
    ncols = len(A[0])
    result = []
    for j in range(ncols):
        row = []
        for i in range(nrows):
            row.append(A[i][j])
        result.append(row)
    return result


def trace(A):
    n = min(len(A), len(A[0]))
    return sum(A[i][i] for i in range(n))


def norm_vector(v):
    return np.sqrt(sum(x * x for x in v))


def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def polynomial_eval(coeffs, x):
    result = 0
    for c in coeffs:
        result = result * x + c
    return result


def polynomial_add(coeffs1, coeffs2):
    len1 = len(coeffs1)
    len2 = len(coeffs2)
    n = max(len1, len2)
    result = [0.0] * n
    for i in range(len1):
        result[n - len1 + i] += coeffs1[i]
    for i in range(len2):
        result[n - len2 + i] += coeffs2[i]
    return result


def polynomial_multiply(coeffs1, coeffs2):
    n = len(coeffs1) + len(coeffs2) - 1
    result = [0] * n
    for i in range(len(coeffs1)):
        for j in range(len(coeffs2)):
            result[i + j] += coeffs1[i] * coeffs2[j]
    return result


__all__ = [
    "det",
    "inverse_2x2",
    "matrix_multiply",
    "matrix_add",
    "matrix_scalar_mul",
    "transpose",
    "trace",
    "norm_vector",
    "dot_product",
    "cross_product",
    "polynomial_eval",
    "polynomial_add",
    "polynomial_multiply",
]