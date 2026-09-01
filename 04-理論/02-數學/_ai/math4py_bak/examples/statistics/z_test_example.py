"""Example: Z-Test

Usage: python z_test_example.py
"""

import math4py.statistics as R

print("=" * 60)
print("Z-Test Examples (Known Population Sigma)")
print("=" * 60)

print("\n1. One-Sample Z-Test")
print("-" * 40)
data = [101, 102, 100, 99, 101, 103, 100, 101]
result = R.z_test(data, sigma=2, mu=100)
print(f"Data: {data}")
print(f"Known sigma = 2")
print(f"H0: mu = 100")
print(f"Result: {result}")
print(f"95% CI: ({result['ci'][0]:.2f}, {result['ci'][1]:.2f})")

print("\n2. Z-Test with Different Alpha")
print("-" * 40)
data = R.rnorm(50, 100, 15)
result = R.z_test(data, sigma=15, mu=100, alpha=0.01)
print(f"Sample size: 50")
print(f"H0: mu = 100, alpha = 0.01")
print(f"Result: {result}")