"""Example: Chi-Square Test

Usage: python chisq_test_example.py
"""

import math4py.statistics as R

print("=" * 60)
print("Chi-Square Test Examples")
print("=" * 60)

print("\n1. Goodness of Fit Test")
print("-" * 40)
observed = [[10, 20], [15, 15], [5, 5]]
result = R.chisq_test(observed)
print(f"Observed frequencies: {observed}")
print(f"Chi-square statistic: {result['statistic']:.4f}")
print(f"df: {result['df']}")
print(f"p-value: {result['p_value']:.6f}")

print("\n2. Independence Test")
print("-" * 40)
observed = [[30, 10], [15, 25]]
result = R.chisq_test(observed)
print(f"Contingency table: {observed}")
print(f"Chi-square statistic: {result['statistic']:.4f}")
print(f"df: {result['df']}")
print(f"p-value: {result['p_value']:.6f}")
print(f"Expected frequencies: {result['expected']}")