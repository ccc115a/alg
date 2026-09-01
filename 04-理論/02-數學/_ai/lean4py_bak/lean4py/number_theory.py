from typing import Tuple, List, Optional

class Integer:
    def __init__(self, n: int):
        self.n = n

    def __repr__(self):
        return f"Integer({self.n})"

    def __eq__(self, other):
        if isinstance(other, Integer):
            return self.n == other.n
        return False

    def __hash__(self):
        return hash(self.n)

    def __add__(self, other):
        if isinstance(other, Integer):
            return Integer(self.n + other.n)
        return Integer(self.n + other)

    def __radd__(self, other):
        return Integer(other + self.n)

    def __sub__(self, other):
        if isinstance(other, Integer):
            return Integer(self.n - other.n)
        return Integer(self.n - other)

    def __rsub__(self, other):
        return Integer(other - self.n)

    def __mul__(self, other):
        if isinstance(other, Integer):
            return Integer(self.n * other.n)
        return Integer(self.n * other)

    def __rmul__(self, other):
        return Integer(other * self.n)

    def __truediv__(self, other):
        if isinstance(other, Integer):
            if other.n == 0:
                raise ZeroDivisionError("division by zero")
            return Integer(self.n // other.n)
        if other == 0:
            raise ZeroDivisionError("division by zero")
        return Integer(self.n // other)

    def __neg__(self):
        return Integer(-self.n)

    def __abs__(self):
        return Integer(abs(self.n))

    def __le__(self, other):
        if isinstance(other, Integer):
            return self.n <= other.n
        return self.n <= other

    def __lt__(self, other):
        if isinstance(other, Integer):
            return self.n < other.n
        return self.n < other

    def __ge__(self, other):
        if isinstance(other, Integer):
            return self.n >= other.n
        return self.n >= other

    def __gt__(self, other):
        if isinstance(other, Integer):
            return self.n > other.n
        return self.n > other

    @property
    def is_zero(self) -> bool:
        return self.n == 0

    @property
    def is_positive(self) -> bool:
        return self.n > 0

    @property
    def is_negative(self) -> bool:
        return self.n < 0

def int_(n: int) -> Integer:
    return Integer(n)

def zero() -> Integer:
    return Integer(0)

def one() -> Integer:
    return Integer(1)

def gcd(a: Integer, b: Integer) -> Integer:
    a_abs, b_abs = abs(a.n), abs(b.n)
    while b_abs != 0:
        a_abs, b_abs = b_abs, a_abs % b_abs
    return Integer(a_abs)

def lcm(a: Integer, b: Integer) -> Optional[Integer]:
    if a.n == 0 or b.n == 0:
        return Integer(0)
    return Integer(abs(a.n * b.n) // gcd(a, b).n)

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (1, 0, a)
    x1, y1, g = extended_gcd(b, a % b)
    return (y1, x1 - (a // b) * y1, g)

def bezout_identity(a: Integer, b: Integer) -> Tuple[Integer, Integer, Integer]:
    x, y, d = extended_gcd(a.n, b.n)
    return (Integer(x), Integer(y), Integer(d))

def is_prime(n: Integer) -> bool:
    v = n.n
    if v < 2:
        return False
    if v == 2:
        return True
    if v % 2 == 0:
        return False
    for i in range(3, int(v ** 0.5) + 1, 2):
        if v % i == 0:
            return False
    return True

def prime_factors(n: Integer) -> List[Integer]:
    v = n.n
    if v == 0:
        return []
    if v == 1:
        return []
    factors = []
    d = 2
    temp = abs(v)
    while d * d <= temp:
        while temp % d == 0:
            factors.append(Integer(d))
            temp //= d
        d += 1
    if temp > 1:
        factors.append(Integer(temp))
    return factors

def phi(n: Integer) -> Integer:
    v = n.n
    if v <= 0:
        return Integer(0)
    if v == 1:
        return Integer(1)
    factors = prime_factors(n)
    result = v
    seen = set()
    for p in factors:
        if p.n not in seen:
            seen.add(p.n)
            result -= result // p.n
    return Integer(result)

def mod_exp(base: Integer, exp: Integer, mod: Integer) -> Integer:
    if mod.n == 0:
        raise ValueError("modulus cannot be zero")
    result = 1
    b = base.n % mod.n
    e = exp.n
    if e < 0:
        raise ValueError("exponent must be non-negative")
    while e > 0:
        if e % 2 == 1:
            result = (result * b) % mod.n
        e //= 2
        b = (b * b) % mod.n
    return Integer(result)

def mod_inverse(a: Integer, m: Integer) -> Optional[Integer]:
    if m.n <= 0:
        return None
    x, y, g = extended_gcd(a.n, m.n)
    if g != 1:
        return None
    return Integer((x % m.n + m.n) % m.n)

def divides(d: Integer, n: Integer) -> bool:
    if n.n == 0:
        return True
    if d.n == 0:
        return False
    return n.n % d.n == 0

def divides_rel(d: Integer, n: Integer):
    from lean4py.logic import Prop, implies, and_
    return Prop(f"{d} | {n}")

def divides_theorem(a: Integer, b: Integer):
    from lean4py.logic import Theorem, Prop
    if divides(a, b) and divides(b, a):
        return abs(a.n) == abs(b.n)
    return False

def coprime(a: Integer, b: Integer) -> bool:
    return gcd(a, b).n == 1

def chinese_remainder(r1: Integer, m1: Integer, r2: Integer, m2: Integer) -> Optional[Integer]:
    s, t, g = extended_gcd(m1.n, m2.n)
    if g != 1:
        return None
    n = r1.n + m1.n * ((r2.n - r1.n) * s % m2.n)
    return Integer(n % (m1.n * m2.n))

class Divisibility:
    def __init__(self, a: Integer, b: Integer):
        self.a = a
        self.b = b

    def holds(self) -> bool:
        return divides(self.a, self.b)

    def __repr__(self):
        return f"{self.a} | {self.b}"

def divides_stmt(a: Integer, b: Integer) -> Divisibility:
    return Divisibility(a, b)

class NumberTheoryTheorem:
    def __init__(self, name: str, statement: str, proof: list = None):
        self.name = name
        self.statement = statement
        self.proof = proof or []

    def __repr__(self):
        return f"Theorem({self.name}: {self.statement})"

def fundamental_theorem_of_arithmetic(n: Integer) -> bool:
    if n.n <= 1:
        return True
    factors = prime_factors(n)
    product = Integer(1)
    for f in factors:
        product = product * f
    for f in factors:
        count_n = factors.count(f)
        count_product = prime_factors(product).count(f)
        product = product / f
    return abs(product.n) == 1

class IntegerInduction:
    @staticmethod
    def prove(P: callable, n: Integer) -> bool:
        if n.n == 0:
            return P(Integer(0))
        k = 1
        while k <= n.n:
            if not P(Integer(k)):
                return False
            k += 1
        return True

    @staticmethod
    def prove_by_strong(P: callable, n: Integer) -> bool:
        if n.n == 0:
            return P(Integer(0))
        results = {}
        for i in range(n.n + 1):
            if i == 0:
                results[0] = P(Integer(0))
            else:
                results[i] = P(Integer(i)) and all(results[j] for j in range(i))
            if not results[i]:
                return False
        return True