"""Example: Visualization with Confidence Intervals

Usage: python plot_ci_example.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import statr as R

print("=" * 60)
print("Confidence Interval Visualization Examples")
print("=" * 60)

print("\n1. T-Test with CI Plot")
print("-" * 40)
data = [101, 102, 100, 99, 101, 103, 100, 101]
result = R.t_test(data, mu=100)
print(f"Data: {data}")
print(f"95% CI: {result['ci']}")
print("\nTo show plot, uncomment:")
print("  R.plot_t_ci(data, result['ci'], result['estimate'])")

print("\n2. Z-Test with CI Plot")
print("-" * 40)
mean_val = 100.5
se = 0.5
ci = (99.5, 101.5)
print(f"Mean: {mean_val}, SE: {se}")
print(f"95% CI: {ci}")
print("\nTo show plot, uncomment:")
print("  R.plot_z_ci(mean_val, se, ci)")

print("\n3. ANOVA Group Means with CI")
print("-" * 40)
groups = [[22, 25, 28, 24], [30, 33, 28, 31], [18, 20, 22, 19]]
labels = ["Group A", "Group B", "Group C"]
means = [R.mean(g) for g in groups]
ses = [R.sd(g)/len(g)**0.5 for g in groups]
print(f"Groups: {groups}")
print(f"Means: {means}")
print("\nTo show plot, uncomment:")
print("  R.plot_anova_ci(means, ses, labels)")