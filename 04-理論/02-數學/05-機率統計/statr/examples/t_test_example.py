"""Example: T-Test with Confidence Interval Visualization

Usage: python t_test_example.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import statr as R

print("=" * 60)
print("T-Test Examples")
print("=" * 60)

print("\n1. One-Sample T-Test")
print("-" * 40)
data = [101, 102, 100, 99, 101, 103, 100, 101]
result = R.t_test(data, mu=100)
print(f"Data: {data}")
print(f"H0: mu = 100")
print(f"Result: {result}")
print(f"Interpretation: p-value = {result['p_value']:.4f}")
if result['p_value'] < 0.05:
    print("  => Reject H0 at alpha=0.05")
else:
    print("  => Fail to reject H0 at alpha=0.05")

print("\n2. Two-Sample T-Test (Independent)")
print("-" * 40)
group1 = [85, 90, 88, 92, 87]
group2 = [78, 82, 80, 76, 79]
result = R.t_test(group1, group2)
print(f"Group 1: {group1}, mean = {R.mean(group1):.2f}")
print(f"Group 2: {group2}, mean = {R.mean(group2):.2f}")
print(f"Result: {result}")
print(f"Difference: {result['estimate']:.2f}")

print("\n3. Paired T-Test")
print("-" * 40)
before = [100, 102, 98, 105, 101]
after = [95, 99, 96, 100, 98]
result = R.t_test(before, after, paired=True)
print(f"Before: {before}, mean = {R.mean(before):.2f}")
print(f"After:  {after}, mean = {R.mean(after):.2f}")
print(f"Result: {result}")

print("\n4. Visualization")
print("-" * 40)
print("To visualize the CI, uncomment the following line:")
print("  R.plot_t_ci(data, result['ci'], result['estimate'])")