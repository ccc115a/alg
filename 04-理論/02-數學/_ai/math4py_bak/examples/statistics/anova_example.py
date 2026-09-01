"""Example: ANOVA

Usage: python anova_example.py
"""

import math4py.statistics as R

print("=" * 60)
print("One-Way ANOVA Examples")
print("=" * 60)

print("\n1. Basic ANOVA")
print("-" * 40)
g1 = [22, 25, 28, 24]
g2 = [30, 33, 28, 31]
g3 = [18, 20, 22, 19]
print(f"Group 1: {g1}, mean = {R.mean(g1):.2f}")
print(f"Group 2: {g2}, mean = {R.mean(g2):.2f}")
print(f"Group 3: {g3}, mean = {R.mean(g3):.2f}")

result = R.anova(g1, g2, g3)
print(f"\nANOVA Result:")
print(f"  F-statistic: {result['statistic']:.4f}")
print(f"  df1 (between): {result['df1']}")
print(f"  df2 (within): {result['df2']}")
print(f"  p-value: {result['p_value']:.6f}")
print(f"  SS between: {result['ss_between']:.4f}")
print(f"  SS within: {result['ss_within']:.4f}")

if result['p_value'] < 0.05:
    print("\n  => Reject H0: At least one group mean differs")
else:
    print("\n  => Fail to reject H0: No significant difference")