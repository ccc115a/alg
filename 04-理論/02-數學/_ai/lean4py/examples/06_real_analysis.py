#!/usr/bin/env python3
from lean4py.real_analysis import (
    Real, real, limit, limit_left, limit_right,
    derivative, partial_derivative, integral, riemann_sum,
    series_sum, infinite_series_sum, converges,
    is_continuous, is_differentiable, taylor_series, Sequence
)

print("=" * 60)
print("Real Analysis Module Examples")
print("=" * 60)

print("\n1. Real Numbers:")
x = Real(3.14159)
y = Real(2.71828)
print(f"   x = {x}, y = {y}")
print(f"   x + y = {x + y}")
print(f"   x - y = {x - y}")
print(f"   x * y = {x * y}")
print(f"   x / y = {x / y}")

print("\n2. Limits:")
f = lambda t: (t**2 - 1) / (t - 1)
result = limit(f, 1)
print(f"   lim_{{t→1}} (t²-1)/(t-1) = {result}")

g = lambda s: (s**3 - 8) / (s - 2)
result = limit(g, 2)
print(f"   lim_{{s→2}} (s³-8)/(s-2) = {result}")

h = lambda z: (z**2 - 4) / (z - 2)
left = limit_left(h, 2)
right = limit_right(h, 2)
print(f"   Left limit at 2: {left}, Right limit at 2: {right}")

print("\n3. Derivatives:")
def f(x): return x**2
def df(x): return 2*x

x = 3.0
approx_deriv = derivative(f, x)
exact_deriv = df(x)
print(f"   f(x) = x²")
print(f"   f'({x}) ≈ {approx_deriv} (exact: {exact_deriv})")

import math
sin_deriv = derivative(math.sin, 0)
print(f"   sin'(0) ≈ {sin_deriv} (exact: 1)")

cos_deriv = derivative(math.cos, math.pi/4)
print(f"   cos'(π/4) ≈ {cos_deriv} (exact: -√2/2 ≈ {-math.sqrt(2)/2})")

print("\n4. Partial Derivatives:")
def f(xy): return xy[0]**2 + xy[1]**2
partial_x = partial_derivative(f, [1.0, 1.0], 0)
partial_y = partial_derivative(f, [1.0, 1.0], 1)
print(f"   f(x,y) = x² + y² at (1,1)")
print(f"   ∂f/∂x = {partial_x}, ∂f/∂y = {partial_y}")

print("\n5. Integrals:")
def f(t): return t**2
result = integral(f, 0, 1)
print(f"   ∫₀¹ t² dt = {result} (exact: 1/3 ≈ {1/3})")

def g(x): return math.sin(x)
result = integral(g, 0, math.pi)
print(f"   ∫₀^π sin(x) dx = {result} (exact: 2)")

def h(x): return x**3
result = integral(h, 0, 2)
print(f"   ∫₀² x³ dx = {result} (exact: 4)")

print("\n6. Riemann Sums:")
f = lambda x: x**2
left_sum = riemann_sum(f, 0, 1, n=100, method='left')
right_sum = riemann_sum(f, 0, 1, n=100, method='right')
mid_sum = riemann_sum(f, 0, 1, n=100, method='midpoint')
print(f"   ∫₀¹ x² dx ≈ {left_sum.value:.6f} (left Riemann)")
print(f"   ∫₀¹ x² dx ≈ {right_sum.value:.6f} (right Riemann)")
print(f"   ∫₀¹ x² dx ≈ {mid_sum.value:.6f} (midpoint Riemann)")
print(f"   Exact value: {1/3}")

print("\n7. Series Sum:")
series = lambda n: 1 / (n * (n + 1))
result = series_sum(series, 1, 100)
print(f"   Σ₁¹⁰⁰ 1/(n(n+1)) = {result}")

print("\n8. Infinite Series:")
geom_series = lambda n: (1/2) ** n
result, conv = infinite_series_sum(geom_series)
print(f"   Σ₀^∞ (1/2)^n = {result} (converges: {conv})")

harm_series = lambda n: 1 / n
result, conv = infinite_series_sum(harm_series, max_terms=1000)
print(f"   Σ₁^∞ 1/n diverges (converges: {conv})")

print("\n9. Convergence Test:")
p_series = lambda n: 1 / (n ** 2)
print(f"   Σ 1/n² converges: {converges(p_series)}")

exp_series = lambda n: 1 / (2 ** n)
print(f"   Σ 1/2^n converges: {converges(exp_series)}")

print("\n10. Continuity:")
poly = lambda x: x**3 - 2*x + 1
print(f"   f(x) = x³ - 2x + 1")
print(f"   Is continuous at x=1: {is_continuous(poly, 1.0)}")
print(f"   Is continuous at x=2: {is_continuous(poly, 2.0)}")

print("\n11. Differentiability:")
print(f"   f(x) = |x|")
abs_func = lambda x: abs(x)
print(f"   Is differentiable at x=1: {is_differentiable(abs_func, 1.0)}")
print(f"   Is differentiable at x=0: {is_differentiable(abs_func, 0.0)}")

print("\n12. Taylor Series:")
f = lambda x: math.sin(x)
taylor_fn = taylor_series(f, 0, 5)
for x_val in [0, math.pi/6, math.pi/4, math.pi/3]:
    approx = taylor_fn(x_val)
    exact = math.sin(x_val)
    print(f"   sin({x_val:.2f}) ≈ {approx:.6f} (exact: {exact:.6f})")

print("\n13. Sequence Limit:")
a_n = lambda n: (2*n + 1) / (3*n + 5)
result, conv = Sequence(a_n).limit()
print(f"   a_n = (2n+1)/(3n+5)")
print(f"   limit = {result} (converged: {conv})")

print("\n14. Sequence Monotonicity:")
inc_seq = lambda n: n / (n + 1)
dec_seq = lambda n: 1 + 1/n
print(f"   a_n = n/(n+1) is {Sequence(inc_seq).is_monotonic()}")
print(f"   a_n = 1 + 1/n is {Sequence(dec_seq).is_monotonic()}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)