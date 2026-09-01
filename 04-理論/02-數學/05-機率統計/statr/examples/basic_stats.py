"""Example: Basic Statistics with Statr

Usage: python basic_stats.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import statr as R
import os

print("=" * 60)
print("Statr - R-style Python Statistical Library")
print("=" * 60)

print("\n1. Distribution Functions (R-style naming)")
print("-" * 40)
print(f"R.dnorm(0, 0, 1) = {R.dnorm(0, 0, 1):.6f}")
print(f"R.pnorm(1.96, 0, 1) = {R.pnorm(1.96, 0, 1):.6f}")
print(f"R.qnorm(0.975, 0, 1) = {R.qnorm(0.975, 0, 1):.6f}")
print(f"R.dt(2, 10) = {R.dt(2, 10):.6f}")
print(f"R.pchisq(3.84, 1) = {R.pchisq(3.84, 1):.6f}")

print("\n2. Descriptive Statistics")
print("-" * 40)
data = [2, 4, 6, 8, 10]
print(f"Data: {data}")
print(f"R.mean(data) = {R.mean(data)}")
print(f"R.median(data) = {R.median(data)}")
print(f"R.var(data) = {R.var(data)}")
print(f"R.sd(data) = {R.sd(data)}")

print("\n3. Full Summary")
print("-" * 40)
print(R.summary(data))

print("\n4. Random Number Generation")
print("-" * 40)
samples = R.rnorm(10, 0, 1)
print(f"R.rnorm(10, 0, 1) = {samples}")
print(f"Sample mean: {R.mean(samples):.4f}")
print(f"Sample sd: {R.sd(samples):.4f}")