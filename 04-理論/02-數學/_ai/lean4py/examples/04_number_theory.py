#!/usr/bin/env python3
from lean4py.number_theory import (
    Integer, int_, zero, one, gcd, lcm, bezout_identity,
    is_prime, prime_factors, phi, mod_exp, mod_inverse,
    divides, coprime, fundamental_theorem_of_arithmetic
)

print("=" * 60)
print("Number Theory Module Examples")
print("=" * 60)

print("\n1. Integer Operations:")
a = Integer(12)
b = Integer(18)
print(f"   a = {a}, b = {b}")
print(f"   a + b = {a + b}")
print(f"   a - b = {a - b}")
print(f"   a * b = {a * b}")
print(f"   -a = {-a}")
print(f"   abs(-a) = {abs(-a)}")

print("\n2. GCD and LCM:")
print(f"   gcd({a}, {b}) = {gcd(a, b)}")
print(f"   lcm({a}, {b}) = {lcm(a, b)}")
print(f"   gcd({a}, {a}) * lcm({a}, {a}) = {gcd(a, a) * lcm(a, a)} (should be |a*a| = {abs(a.n * a.n)})")

print("\n3. Bezout Identity:")
x, y, d = bezout_identity(Integer(35), Integer(15))
print(f"   35 * {x.n} + 15 * {y.n} = {35 * x.n + 15 * y.n} = d = {d}")

print("\n4. Prime Numbers:")
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
for p in primes:
    print(f"   is_prime({p}) = {is_prime(Integer(p))}")
non_primes = [1, 4, 6, 8, 9, 10, 12, 15]
print("   Non-primes: 1, 4, 6, 8, 9, 10, 12, 15")
for np in non_primes:
    print(f"   is_prime({np}) = {is_prime(Integer(np))}")

print("\n5. Prime Factorization:")
for n in [12, 60, 100, 17]:
    factors = prime_factors(Integer(n))
    print(f"   prime_factors({n}) = {[f.n for f in factors]}")

print("\n6. Euler's Totient Function (phi):")
for n in [1, 2, 5, 10, 12, 17]:
    print(f"   phi({n}) = {phi(Integer(n))}")

print("\n7. Modular Exponentiation:")
print(f"   2^10 mod 1024 = {mod_exp(Integer(2), Integer(10), Integer(1024))}")
print(f"   3^4 mod 10 = {mod_exp(Integer(3), Integer(4), Integer(10))}")
print(f"   7^234 mod 100 = {mod_exp(Integer(7), Integer(234), Integer(100))}")

print("\n8. Modular Inverse:")
inv3 = mod_inverse(Integer(3), Integer(11))
if inv3:
    print(f"   3^(-1) mod 11 = {inv3}")
    print(f"   Verification: 3 * {inv3.n} mod 11 = {(3 * inv3.n) % 11}")
inv2 = mod_inverse(Integer(2), Integer(4))
print(f"   2^(-1) mod 4 = {inv2} (no inverse exists)")

print("\n9. Coprime Check:")
pairs = [(7, 11), (12, 18), (8, 15)]
for a, b in pairs:
    print(f"   coprime({a}, {b}) = {coprime(Integer(a), Integer(b))}")

print("\n10. Divisibility:")
tests = [(3, 12), (5, 12), (7, 0)]
for d, n in tests:
    print(f"   {d} divides {n} = {divides(Integer(d), Integer(n))}")

print("\n11. Fundamental Theorem of Arithmetic:")
for n in [1, 7, 12, 60, 100]:
    result = fundamental_theorem_of_arithmetic(Integer(n))
    print(f"   fundamental_theorem_of_arithmetic({n}) = {result}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)