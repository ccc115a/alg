"""Example: Central Limit Theorem - math4py.statistics"""

import math4py.statistics as R
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
os.makedirs("./out", exist_ok=True)

def sample_sum(distribution, n):
    """Draw n samples and return their sum."""
    total = 0
    for _ in range(n):
        total += distribution()
    return total

def coin_flip():
    return np.random.choice([0, 1])

def dice_roll():
    return np.random.choice([1, 2, 3, 4, 5, 6])

def uniform():
    return np.random.uniform(0, 1)

def normal():
    return np.random.normal(0, 1)

def plot_clt(distribution, name, n_values, n_trials=10000, filename=None):
    """Plot CLT demonstration for given distribution."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Central Limit Theorem: {name}", fontsize=14, fontweight="bold")

    colors = ['#2196F3', '#F44336', '#4CAF50', '#FF9800']

    for idx, n in enumerate(n_values):
        ax = axes[idx // 2, idx % 2]

        # Generate sample sums
        sums = [sample_sum(distribution, n) for _ in range(n_trials)]

        # Plot histogram
        ax.hist(sums, bins=50, density=True, alpha=0.7, color=colors[idx], edgecolor='white')

        # Overlay normal distribution fit
        mean = np.mean(sums)
        std = np.std(sums)
        x = np.linspace(min(sums), max(sums), 200)
        y = R.dnorm(x, mean, std)
        ax.plot(x, y, 'r-', lw=2, label=f'N({mean:.2f}, {std:.2f})')

        ax.set_title(f"n = {n} samples (trials = {n_trials})")
        ax.set_xlabel("Sum")
        ax.set_ylabel("Density")
        ax.legend(fontsize=8)

    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved to {filename}")
    return fig

print("=" * 60)
print("Central Limit Theorem Demonstration")
print("=" * 60)

n_values = [1, 2, 10, 20]

print("\n--- Coin Flip (Bernoulli) ---")
print("Distribution: P(X=0) = P(X=1) = 0.5")
print("Mean = 0.5, Variance = 0.25")
plot_clt(coin_flip, "Coin Flip (Bernoulli)", n_values, filename="./out/clt_coin.png")

print("\n--- Dice Roll (1-6) ---")
print("Distribution: P(X=k) = 1/6 for k=1,2,3,4,5,6")
print("Mean = 3.5, Variance = 35/12 ≈ 2.92")
plot_clt(dice_roll, "Dice Roll (Uniform 1-6)", n_values, filename="./out/clt_dice.png")

print("\n--- Uniform (0, 1) ---")
print("Distribution: Uniform(0, 1)")
print("Mean = 0.5, Variance = 1/12 ≈ 0.083")
plot_clt(uniform, "Uniform(0, 1)", n_values, filename="./out/clt_uniform.png")

print("\n--- Normal (0, 1) ---")
print("Distribution: N(0, 1)")
print("Mean = 0, Variance = 1")
plot_clt(normal, "Normal(0, 1)", n_values, filename="./out/clt_normal.png")

print("\n" + "=" * 60)
print("CLT: Sum of n samples from ANY distribution")
print("      → approaches N(n*μ, n*σ²) as n → ∞")
print("=" * 60)
print("\nAll CLT plots saved to ./out/")