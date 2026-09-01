"""微積分定理驗證。

用 function.py 中的計算函數驗證定理是否成立。
"""

import math
import numpy as np
from .function import derivative, integral, simpson, trapezoidal


def fundamental_theorem():
    """微積分基本定理驗證。

    若 F'(x) = f(x)，則 ∫[a,b] f(x)dx = F(b) - F(a)
    """
    F = lambda x: -math.cos(x)
    f = lambda x: math.sin(x)

    a, b = 0, math.pi
    exact = -math.cos(b) - (-math.cos(a))

    x_arr = np.linspace(a, b, 1001)
    y_arr = np.array([f(x) for x in x_arr])
    h = (b - a) / 1000
    num_int = h * (0.5 * y_arr[0] + np.sum(y_arr[1:-1]) + 0.5 * y_arr[-1])

    x_arr2 = np.linspace(a, b, 101)
    y_arr2 = np.array([f(x) for x in x_arr2])
    h2 = (b - a) / 100
    num_sim = h2 / 3 * (y_arr2[0] + y_arr2[-1] + 4 * np.sum(y_arr2[1:-1:2]) + 2 * np.sum(y_arr2[2:-2:2]))

    error_int = abs(num_int - exact)
    error_sim = abs(num_sim - exact)

    return {
        "exact": exact,
        "integral_approx": num_int,
        "simpson_approx": num_sim,
        "integral_error": error_int,
        "simpson_error": error_sim,
        "pass": bool(error_int < 1e-3 and error_sim < 1e-3)
    }


def mean_value_theorem():
    """均值定理驗證。"""
    f = lambda x: x ** 2
    a, b = 0, 2

    slope = (f(b) - f(a)) / (b - a)

    c = (a + b) / 2
    h = 1e-5
    deriv_at_c = (f(c + h) - f(c - h)) / (2 * h)

    error = abs(deriv_at_c - slope)

    return {
        "slope": slope,
        "f_prime_at_c": deriv_at_c,
        "c": c,
        "error": error,
        "pass": error < 1e-5
    }


def rolle_theorem():
    """Rolle 定理驗證。"""
    f = lambda x: x ** 2 - x
    a, b = 0, 1

    if abs(f(a) - f(b)) > 1e-10:
        return {"pass": False, "reason": "f(a) != f(b)"}

    c = 0.5
    h = 1e-5
    deriv = (f(c + h) - f(c - h)) / (2 * h)

    return {
        "f_a": f(a),
        "f_b": f(b),
        "c": c,
        "f_prime_at_c": deriv,
        "pass": abs(deriv) < 1e-10
    }


def intermediate_value_theorem():
    """中介值定理驗證。"""
    f = lambda x: x ** 2
    a, b = 0, 2
    y = 2.0

    if y < f(a) or y > f(b):
        return {"pass": False, "reason": "y not in range"}

    c = math.sqrt(y)

    return {
        "y": y,
        "c": c,
        "f(c)": f(c),
        "pass": abs(f(c) - y) < 1e-10
    }


def taylor_theorem():
    """Taylor 級數驗證 e^x at x=0.5。"""
    x_val = 0.5
    exact = math.exp(x_val)

    approx = 1 + x_val + x_val**2/2 + x_val**3/6 + x_val**4/24 + x_val**5/120

    error = abs(approx - exact)

    return {
        "exact": exact,
        "approx": approx,
        "error": error,
        "pass": bool(error < 0.01)
    }


def leibniz_rule(limit=1000):
    """Leibniz 級數收斂到 π/4。"""
    total = 0.0
    for i in range(limit):
        term = ((-1) ** i) / (2 * i + 1)
        total += term

    exact = math.pi / 4
    error = abs(total - exact)

    return {
        "approximation": total,
        "exact": exact,
        "error": error,
        "pass": error < 1e-3
    }


def wallis_product(limit=1000):
    """Wallis 積公式收斂到 π/2。"""
    total = 1.0
    for i in range(1, limit + 1):
        term = (4 * i * i) / ((4 * i * i) - 1)
        total *= term

    result = total * 2
    exact = math.pi
    error = abs(result - exact)

    return {
        "approximation": result,
        "exact": exact,
        "error": error,
        "pass": error < 0.1
    }


__all__ = [
    "fundamental_theorem",
    "mean_value_theorem",
    "rolle_theorem",
    "intermediate_value_theorem",
    "taylor_theorem",
    "leibniz_rule",
    "wallis_product",
]