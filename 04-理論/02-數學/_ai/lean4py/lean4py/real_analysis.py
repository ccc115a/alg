from typing import Callable, Optional, List, Tuple, Dict
import math

class Real:
    def __init__(self, value: float):
        self.value = float(value)

    def __repr__(self):
        return f"Real({self.value})"

    def __eq__(self, other):
        if isinstance(other, Real):
            return abs(self.value - other.value) < 1e-10
        return False

    def __hash__(self):
        return hash(self.value)

    def __add__(self, other):
        if isinstance(other, Real):
            return Real(self.value + other.value)
        return Real(self.value + other)

    def __radd__(self, other):
        return Real(other + self.value)

    def __sub__(self, other):
        if isinstance(other, Real):
            return Real(self.value - other.value)
        return Real(self.value - other)

    def __rsub__(self, other):
        return Real(other - self.value)

    def __mul__(self, other):
        if isinstance(other, Real):
            return Real(self.value * other.value)
        return Real(self.value * other)

    def __rmul__(self, other):
        return Real(other * self.value)

    def __truediv__(self, other):
        if isinstance(other, Real):
            return Real(self.value / other.value)
        return Real(self.value / other)

    def __neg__(self):
        return Real(-self.value)

    def __abs__(self):
        return Real(abs(self.value))

    def __le__(self, other):
        if isinstance(other, Real):
            return self.value <= other.value
        return self.value <= other

    def __lt__(self, other):
        if isinstance(other, Real):
            return self.value < other.value
        return self.value < other

    def __ge__(self, other):
        if isinstance(other, Real):
            return self.value >= other.value
        return self.value >= other

    def __gt__(self, other):
        if isinstance(other, Real):
            return self.value > other.value
        return self.value > other

    @property
    def is_integer(self) -> bool:
        return abs(self.value - round(self.value)) < 1e-10

def real(x: float) -> Real:
    return Real(x)

def limit(f: Callable[[float], float], x0: float, h: float = 1e-8) -> Real:
    left_limit = f(x0 - h)
    right_limit = f(x0 + h)
    if abs(left_limit - right_limit) < 1e-6:
        return Real((left_limit + right_limit) / 2)
    return Real((left_limit + right_limit) / 2)

def limit_left(f: Callable[[float], float], x0: float, h: float = 1e-8) -> Real:
    return Real(f(x0 - h))

def limit_right(f: Callable[[float], float], x0: float, h: float = 1e-8) -> Real:
    return Real(f(x0 + h))

def derivative(f: Callable[[float], float], x: float, h: float = 1e-8) -> Real:
    left_deriv = (f(x) - f(x - h)) / h
    right_deriv = (f(x + h) - f(x)) / h
    if abs(left_deriv - right_deriv) > 1e-6:
        return Real(float('nan'))
    df = (f(x + h) - f(x - h)) / (2 * h)
    return Real(df)

def partial_derivative(f: Callable[[List[float]], float], x: List[float], var_idx: int, h: float = 1e-8) -> Real:
    def single_var(t):
        vals = x[:]
        vals[var_idx] = t
        return f(vals)
    return derivative(single_var, x[var_idx], h)

def integral(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> Real:
    if a >= b:
        return Real(0)
    dx = (b - a) / n
    result = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        result += f(a + i * dx)
    return Real(result * dx)

def riemann_sum(f: Callable[[float], float], a: float, b: float, n: int = 100, method: str = 'left') -> Real:
    dx = (b - a) / n
    result = 0.0
    for i in range(n):
        if method == 'left':
            x = a + i * dx
        elif method == 'right':
            x = a + (i + 1) * dx
        elif method == 'midpoint':
            x = a + (i + 0.5) * dx
        else:
            x = a + i * dx
        result += f(x)
    return Real(result * dx)

def series_sum(a_n: Callable[[int], float], n_start: int = 1, n_end: Optional[int] = None) -> Real:
    if n_end is None:
        result = 0.0
        i = n_start
        while i < 10000:
            term = a_n(i)
            result += term
            if abs(term) < 1e-12:
                break
            i += 1
        return Real(result)
    else:
        result = 0.0
        for i in range(n_start, n_end + 1):
            result += a_n(i)
        return Real(result)

def infinite_series_sum(a_n: Callable[[int], float], max_terms: int = 10000, tolerance: float = 1e-10) -> Tuple[Real, bool]:
    result = 0.0
    for i in range(1, max_terms + 1):
        term = a_n(i)
        result += term
        if abs(term) < tolerance:
            return (Real(result), True)
    return (Real(result), False)

def converges(series: Callable[[int], float], test: str = 'default', max_terms: int = 1000) -> bool:
    if test == 'default':
        _, converged = infinite_series_sum(series, max_terms, tolerance=1e-8)
        return converged
    elif test == 'comparison':
        for n in range(1, max_terms):
            term = abs(series(n))
            if term >= 1:
                return False
        return True
    else:
        _, converged = infinite_series_sum(series, max_terms, tolerance=1e-8)
        return converged

def is_continuous(f: Callable[[float], float], x0: float, delta: float = 1e-6) -> bool:
    limit_val = limit(f, x0, delta)
    f_val = f(x0)
    return abs(limit_val.value - f_val) < 1e-6

def is_differentiable(f: Callable[[float], float], x: float, h: float = 1e-8) -> bool:
    try:
        df = derivative(f, x, h)
        return not math.isnan(df.value) and not math.isinf(df.value)
    except:
        return False

def nth_derivative(f: Callable[[float], float], x0: float, n: int, h: float = 0.001) -> float:
    if n == 0:
        return f(x0)
    result = 0.0
    for k in range(n + 1):
        result += (-1) ** (n - k) * math.comb(n, k) * f(x0 + k * h)
    return result / (h ** n)

def taylor_series(f: Callable[[float], float], x0: float, n: int, h: float = 0.001) -> Callable[[float], float]:
    coeffs = []
    for i in range(n + 1):
        coeffs.append(nth_derivative(f, x0, i, h))
    def taylor(x):
        result = 0.0
        for i, c in enumerate(coeffs):
            result += c * ((x - x0) ** i) / math.factorial(i)
        return result
    return taylor

def lhopital_limit(f: Callable[[float], float], g: Callable[[float], float], x0: float, n: int = 10) -> Optional[Real]:
    for _ in range(n):
        f0, g0 = f(x0), g(x0)
        if abs(g0) > 1e-10:
            break
        f = derivative(f, x0)
        g = derivative(g, x0)
    try:
        return limit(lambda x: f(x) / g(x), x0)
    except:
        return None

def sequence_limit(a_n: Callable[[int], float], n0: int = 1, tolerance: float = 1e-6, max_iter: int = 100000) -> Tuple[Real, bool]:
    prev = a_n(n0)
    for n in range(n0 + 1, n0 + max_iter):
        curr = a_n(n)
        if abs(curr - prev) < tolerance:
            return (Real(curr), True)
        prev = curr
    return (Real(prev), False)

def is_monotonic(a_n: Callable[[int], float], n_start: int = 1, n_end: int = 100) -> str:
    increasing = decreasing = True
    for n in range(n_start, n_end):
        diff = a_n(n + 1) - a_n(n)
        if diff <= 0:
            increasing = False
        if diff >= 0:
            decreasing = False
    if increasing:
        return "increasing"
    elif decreasing:
        return "decreasing"
    else:
        return "non-monotonic"

def is_bounded(a_n: Callable[[int], float], n_start: int = 1, n_end: int = 1000) -> Tuple[bool, bool]:
    values = [a_n(n) for n in range(n_start, n_end)]
    lower_bound = min(values)
    upper_bound = max(values)
    return (lower_bound > -float('inf'), upper_bound < float('inf'))

class Sequence:
    def __init__(self, a_n: Callable[[int], float]):
        self.a_n = a_n

    def __getitem__(self, n: int) -> float:
        return self.a_n(n)

    def limit(self, n0: int = 1, tolerance: float = 1e-8) -> Tuple[Real, bool]:
        return sequence_limit(self.a_n, n0, tolerance)

    def is_monotonic(self, n_start: int = 1, n_end: int = 100) -> str:
        return is_monotonic(self.a_n, n_start, n_end)

    def is_bounded(self, n_start: int = 1, n_end: int = 1000) -> Tuple[bool, bool]:
        return is_bounded(self.a_n, n_start, n_end)

    def converges(self, n_start: int = 1) -> bool:
        limit_val, converged = self.limit(n_start)
        if not converged:
            return False
        m = is_monotonic(self.a_n, n_start, n_start + 100)
        lower, upper = is_bounded(self.a_n, n_start, n_start + 100)
        return (m != "non-monotonic") and lower and upper

def mclaurin_series(f: Callable[[float], float], n: int, h: float = 1e-8) -> Callable[[float], float]:
    return taylor_series(f, 0.0, n, h)

class Function:
    def __init__(self, f: Callable[[float], float], domain: Optional[Tuple[float, float]] = None):
        self.f = f
        self.domain = domain or (float('-inf'), float('inf'))

    def __call__(self, x: float) -> float:
        if self.domain[0] <= x <= self.domain[1]:
            return self.f(x)
        raise ValueError(f"x = {x} is outside domain {self.domain}")

    def limit(self, x0: float) -> Real:
        return limit(self.f, x0)

    def derivative(self, x: float) -> Real:
        return derivative(self.f, x)

    def integral(self, a: float, b: float) -> Real:
        return integral(self.f, a, b)

    def is_continuous(self, x0: float) -> bool:
        return is_continuous(self.f, x0)

    def is_differentiable(self, x: float) -> bool:
        return is_differentiable(self.f, x)

def compose(f: Function, g: Function) -> Function:
    return Function(lambda x: f.f(g.f(x)))

def sum_func(f: Function, g: Function) -> Function:
    return Function(lambda x: f.f(x) + g.f(x))

def product_func(f: Function, g: Function) -> Function:
    return Function(lambda x: f.f(x) * g.f(x))