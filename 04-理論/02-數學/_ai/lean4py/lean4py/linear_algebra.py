from typing import List, Tuple, Optional

class Vector:
    def __init__(self, dim: int, elements: List[float]):
        if len(elements) != dim:
            raise ValueError(f"Expected {dim} elements, got {len(elements)}")
        self.dim = dim
        self.elements = elements

    def __repr__(self):
        return f"Vector({self.elements})"

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.elements == other.elements

    def __hash__(self):
        return hash(tuple(self.elements))

    def __add__(self, other):
        if not isinstance(other, Vector) or self.dim != other.dim:
            raise ValueError("Vectors must have same dimension")
        return Vector(self.dim, [a + b for a, b in zip(self.elements, other.elements)])

    def __sub__(self, other):
        if not isinstance(other, Vector) or self.dim != other.dim:
            raise ValueError("Vectors must have same dimension")
        return Vector(self.dim, [a - b for a, b in zip(self.elements, other.elements)])

    def __mul__(self, scalar):
        return Vector(self.dim, [x * scalar for x in self.elements])

    def __rmul__(self, scalar):
        return Vector(self.dim, [x * scalar for x in self.elements])

    def __neg__(self):
        return Vector(self.dim, [-x for x in self.elements])

    def __getitem__(self, i):
        return self.elements[i]

    def __iter__(self):
        return iter(self.elements)

    def norm(self) -> float:
        import math
        return math.sqrt(sum(x * x for x in self.elements))

    def normalize(self):
        n = self.norm()
        if n == 0:
            raise ValueError("Cannot normalize zero vector")
        return Vector(self.dim, [x / n for x in self.elements])

def vector(dim: int, elements: List[float]) -> Vector:
    return Vector(dim, elements)

def zero_vector(dim: int) -> Vector:
    return Vector(dim, [0.0] * dim)

def dot_product(u: Vector, v: Vector) -> float:
    if u.dim != v.dim:
        raise ValueError("Vectors must have same dimension")
    return sum(a * b for a, b in zip(u.elements, v.elements))

def cross_product(u: Vector, v: Vector) -> Vector:
    if u.dim != 3 or v.dim != 3:
        raise ValueError("Cross product is only defined for 3D vectors")
    a, b, c = u.elements
    d, e, f = v.elements
    return Vector(3, [
        b * f - c * e,
        c * d - a * f,
        a * e - b * d
    ])

def angle_between(u: Vector, v: Vector) -> float:
    import math
    cos_angle = dot_product(u, v) / (u.norm() * v.norm())
    return math.acos(max(-1, min(1, cos_angle)))

def projection(u: Vector, v: Vector) -> Vector:
    scale = dot_product(u, v) / dot_product(v, v)
    return v * scale

class Matrix:
    def __init__(self, rows: int, cols: int, data: List[List[float]]):
        if rows <= 0 or cols <= 0:
            raise ValueError("Matrix dimensions must be positive")
        if len(data) != rows:
            raise ValueError(f"Expected {rows} rows, got {len(data)}")
        for row in data:
            if len(row) != cols:
                raise ValueError(f"Expected {cols} columns")
        self.rows = rows
        self.cols = cols
        self.data = data

    def __repr__(self):
        return f"Matrix({self.rows}x{self.cols})"

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        return self.data == other.data

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.data))

    def __add__(self, other):
        if not isinstance(other, Matrix) or self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")
        return Matrix(self.rows, self.cols, [
            [a + b for a, b in zip(self.data[i], other.data[i])]
            for i in range(self.rows)
        ])

    def __sub__(self, other):
        if not isinstance(other, Matrix) or self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")
        return Matrix(self.rows, self.cols, [
            [a - b for a, b in zip(self.data[i], other.data[i])]
            for i in range(self.rows)
        ])

    def __mul__(self, scalar):
        return Matrix(self.rows, self.cols, [
            [x * scalar for x in row]
            for row in self.data
        ])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __matmul__(self, other):
        return matrix_mul(self, other)

    def __getitem__(self, i):
        return self.data[i]

    def __iter__(self):
        return iter(self.data)

    def transpose(self):
        return Matrix(self.cols, self.rows, [
            [self.data[j][i] for j in range(self.rows)]
            for i in range(self.cols)
        ])

    def row(self, i: int) -> List[float]:
        return self.data[i]

    def col(self, j: int) -> List[float]:
        return [self.data[i][j] for i in range(self.rows)]

def matrix(rows: int, cols: int, data: List[List[float]]) -> Matrix:
    return Matrix(rows, cols, data)

def identity_matrix(n: int) -> Matrix:
    return Matrix(n, n, [
        [1 if i == j else 0 for j in range(n)]
        for i in range(n)
    ])

def zero_matrix(rows: int, cols: int) -> Matrix:
    return Matrix(rows, cols, [[0.0] * cols for _ in range(rows)])

def matrix_mul(A: Matrix, B: Matrix) -> Matrix:
    if A.cols != B.rows:
        raise ValueError(f"Cannot multiply {A.rows}x{A.cols} by {B.rows}x{B.cols}")
    result = zero_matrix(A.rows, B.cols)
    for i in range(A.rows):
        for j in range(B.cols):
            total = 0
            for k in range(A.cols):
                total += A.data[i][k] * B.data[k][j]
            result.data[i][j] = total
    return result

def matrix_vector_mul(A: Matrix, v: Vector) -> Vector:
    if A.cols != v.dim:
        raise ValueError(f"Cannot multiply {A.cols}x{v.dim}")
    result = []
    for i in range(A.rows):
        total = sum(A.data[i][j] * v.elements[j] for j in range(A.cols))
        result.append(total)
    return Vector(A.rows, result)

def det(A: Matrix) -> float:
    if A.rows != A.cols:
        raise ValueError("Determinant only defined for square matrices")
    n = A.rows
    if n == 1:
        return A.data[0][0]
    if n == 2:
        return A.data[0][0] * A.data[1][1] - A.data[0][1] * A.data[1][0]
    result = 0
    for j in range(n):
        minor = matrix_minor(A, 0, j)
        cofactor = ((-1) ** j) * det(minor)
        result += A.data[0][j] * cofactor
    return result

def matrix_minor(A: Matrix, i: int, j: int) -> Matrix:
    n = A.rows
    data = [
        [A.data[r][c] for c in range(n) if c != j]
        for r in range(n) if r != i
    ]
    return Matrix(n - 1, n - 1, data)

def matrix_inverse(A: Matrix) -> Optional[Matrix]:
    if A.rows != A.cols:
        return None
    n = A.rows
    d = det(A)
    if abs(d) < 1e-10:
        return None
    if n == 1:
        return Matrix(1, 1, [[1.0 / A.data[0][0]]])
    adj = matrix_adjoint(A)
    return adj * (1.0 / d)

def matrix_adjoint(A: Matrix) -> Matrix:
    n = A.rows
    cofactors = []
    for i in range(n):
        row = []
        for j in range(n):
            minor = matrix_minor(A, i, j)
            cofactor = ((-1) ** (i + j)) * det(minor)
            row.append(cofactor)
        cofactors.append(row)
    return Matrix(n, n, cofactors).transpose()

def rank(A: Matrix) -> int:
    m, n = A.rows, A.cols
    data = [row[:] for row in A.data]
    r = 0
    for c in range(n):
        if r >= m:
            break
        pivot_row = r
        for i in range(r, m):
            if abs(data[i][c]) > abs(data[pivot_row][c]):
                pivot_row = i
        if abs(data[pivot_row][c]) < 1e-10:
            continue
        data[r], data[pivot_row] = data[pivot_row], data[r]
        pivot = data[r][c]
        for j in range(c, n):
            data[r][j] /= pivot
        for i in range(m):
            if i != r:
                factor = data[i][c]
                for j in range(c, n):
                    data[i][j] -= factor * data[r][j]
        r += 1
    return r

def nullity(A: Matrix) -> int:
    return A.cols - rank(A)

def trace(A: Matrix) -> float:
    if A.rows != A.cols:
        raise ValueError("Trace only defined for square matrices")
    return sum(A.data[i][i] for i in range(A.rows))

def is_linearly_independent(vectors: List[Vector]) -> bool:
    if not vectors:
        return True
    n = vectors[0].dim
    for v in vectors:
        if v.dim != n:
            raise ValueError("All vectors must have same dimension")
    if len(vectors) > n:
        return False
    A = Matrix(len(vectors), n, [v.elements for v in vectors]).transpose()
    return rank(A) == len(vectors)

def span(vectors: List[Vector]) -> int:
    if not vectors:
        return 0
    n = vectors[0].dim
    A = Matrix(len(vectors), n, [v.elements for v in vectors]).transpose()
    return rank(A)

def eigenvalues(M: Matrix) -> List[float]:
    if M.rows != M.cols:
        raise ValueError("Eigenvalues only for square matrices")
    n = M.rows
    if n == 1:
        return [M.data[0][0]]
    if n == 2:
        a, b = M.data[0][0], M.data[0][1]
        c, d = M.data[1][0], M.data[1][1]
        trace = a + d
        det_val = a * d - b * c
        disc = trace * trace - 4 * det_val
        if disc < 0:
            return []
        return [(trace + disc ** 0.5) / 2, (trace - disc ** 0.5) / 2]
    return []

def eigenvectors(M: Matrix, eigenvalue: float) -> List[Vector]:
    if M.rows != M.cols:
        raise ValueError("Eigenvectors only for square matrices")
    n = M.rows
    shifted = M + Matrix(n, n, [[-eigenvalue if i == j else 0 for j in range(n)] for i in range(n)])
    r = rank(shifted)
    null_dim = n - r
    if null_dim == 0:
        return []
    basis_vectors = []
    for i in range(n):
        for j in range(n):
            if abs(shifted.data[i][j]) > 1e-10:
                v = [0.0] * n
                v[j] = 1.0
                basis_vectors.append(Vector(n, v))
                break
        if len(basis_vectors) >= null_dim:
            break
    return basis_vectors[:null_dim]

def is_orthogonal(u: Vector, v: Vector) -> bool:
    return abs(dot_product(u, v)) < 1e-10

def is_orthonormal(vectors: List[Vector]) -> bool:
    for v in vectors:
        if abs(v.norm() - 1.0) > 1e-10:
            return False
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            if not is_orthogonal(vectors[i], vectors[j]):
                return False
    return True

class LinearMap:
    def __init__(self, A: Matrix):
        self.A = A

    def __call__(self, v: Vector) -> Vector:
        return matrix_vector_mul(self.A, v)

    @property
    def domain_dim(self) -> int:
        return self.A.cols

    @property
    def codomain_dim(self) -> int:
        return self.A.rows

    def matrix(self) -> Matrix:
        return self.A

def linear_map(A: Matrix) -> LinearMap:
    return LinearMap(A)