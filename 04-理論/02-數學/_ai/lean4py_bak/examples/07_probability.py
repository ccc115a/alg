#!/usr/bin/env python3
from lean4py.probability import (
    ProbabilitySpace, Event, RandomVariable,
    ExpectedValue, Variance, StandardDeviation, Covariance, Correlation,
    NormalDistribution, BinomialDistribution, PoissonDistribution, UniformDistribution,
    bayes_theorem, law_of_total_probability, hypothesis_test, confidence_interval
)

print("=" * 60)
print("Probability Module Examples")
print("=" * 60)

print("\n1. Probability Space (Dice):")
ps = ProbabilitySpace.dice(6)
print(f"   Sample space: {ps.sample_space}")
print(f"   P(rolling 3) = {ps.probability(3)}")

print("\n2. Uniform Space:")
colors = {'red', 'green', 'blue'}
ps = ProbabilitySpace.uniform(colors)
print(f"   Sample space: {colors}")
print(f"   P(red) = {ps.probability('red')}")

print("\n3. Events:")
e1 = Event({1, 2, 3}, "Even or <=3")
e2 = Event({2, 4, 6}, "Even")
print(f"   Event 1: {e1}")
print(f"   Event 2: {e2}")
print(f"   Intersection: {e1 & e2}")
print(f"   Union: {e1 | e2}")

print("\n4. Random Variable:")
X = RandomVariable('X', {1: 1/6, 2: 1/6, 3: 1/6, 4: 1/6, 5: 1/6, 6: 1/6})
print(f"   X = outcome of fair die")
print(f"   E[X] = {ExpectedValue(X)}")
print(f"   Var(X) = {Variance(X)}")
print(f"   σ(X) = {StandardDeviation(X)}")

print("\n5. Biased Coin:")
X = RandomVariable('X', {1: 0.7, 0: 0.3})  # 1=heads, 0=tails
print(f"   P(heads) = 0.7, P(tails) = 0.3")
print(f"   E[X] = {ExpectedValue(X)} (expected heads value)")
print(f"   Var(X) = {Variance(X)}")

print("\n6. Normal Distribution:")
N = NormalDistribution(100, 225)  # μ=100, σ²=225 (σ=15)
print(f"   N(μ=100, σ²=225)")
print(f"   PDF at x=100: {N.pdf(100):.6f}")
print(f"   CDF at x=100: {N.cdf(100):.6f}")
print(f"   P(85 ≤ X ≤ 115) = {N.cdf(115) - N.cdf(85):.4f}")

print("\n7. Binomial Distribution:")
B = BinomialDistribution(10, 0.5)  # 10 trials, p=0.5
print(f"   Binomial(n=10, p=0.5)")
print(f"   P(X=5) = {B.pdf(5):.4f}")
print(f"   P(X≤5) = {B.cdf(5):.4f}")
print(f"   E[X] = {B.mean()}")
print(f"   Var(X) = {B.variance()}")

print("\n8. Poisson Distribution:")
P = PoissonDistribution(3)  # λ=3
print(f"   Poisson(λ=3)")
print(f"   P(X=0) = {P.pdf(0):.4f}")
print(f"   P(X=2) = {P.pdf(2):.4f}")
print(f"   P(X=3) = {P.pdf(3):.4f}")
print(f"   E[X] = {P.mean()}")
print(f"   Var(X) = {P.variance()}")

print("\n9. Uniform Distribution:")
U = UniformDistribution(0, 10)
print(f"   Uniform(0, 10)")
print(f"   PDF at x=5: {U.pdf(5)}")
print(f"   CDF at x=5: {U.cdf(5)}")
print(f"   E[X] = {U.mean()}")

print("\n10. Bayes' Theorem:")
p_b_given_a = 0.9
p_a = 0.3
p_b = 0.5
p_a_given_b = bayes_theorem(0.8, p_b_given_a, p_a, p_b)
print(f"   P(A) = {p_a}")
print(f"   P(B|A) = {p_b_given_a}")
print(f"   P(B) = {p_b}")
print(f"   P(A|B) = {p_a_given_b:.4f}")

print("\n11. Law of Total Probability:")
p_b_givens = [0.1, 0.2, 0.3]
p_as = [0.3, 0.4, 0.3]
p_b = law_of_total_probability(p_b_givens, p_as)
print(f"   P(B) = Σ P(B|A_i)P(A_i) = {p_b:.4f}")

print("\n12. Hypothesis Testing (Z-test):")
sample = [10.2, 9.8, 10.1, 10.3, 9.9, 10.0, 9.7, 10.2, 10.1, 9.9]
result = hypothesis_test('z', sample, mu=10.0)
print(f"   Sample: {sample}")
print(f"   H₀: μ = 10.0")
print(f"   z-statistic = {result['z']:.4f}")
print(f"   p-value = {result['p_value']:.4f}")
print(f"   Reject H₀: {result['reject']}")

print("\n13. Hypothesis Testing (T-test):")
result = hypothesis_test('t', sample, mu=10.0)
print(f"   Sample: {sample}")
print(f"   H₀: μ = 10.0")
print(f"   t-statistic = {result['t']:.4f}")
print(f"   p-value = {result['p_value']:.4f}")
print(f"   Reject H₀: {result['reject']}")

print("\n14. Confidence Interval:")
lower, upper = confidence_interval(sample, 0.95)
print(f"   95% CI for sample mean: ({lower:.4f}, {upper:.4f})")

print("\n15. Covariance and Correlation:")
X = RandomVariable('X', {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25})
Y = RandomVariable('Y', {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25})
print(f"   X and Y independent uniform on {{1,2,3,4}}")
print(f"   Cov(X,Y) = {Covariance(X, Y):.4f}")
print(f"   Corr(X,Y) = {Correlation(X, Y):.4f}")

print("\n" + "=" * 60)
print("All examples completed!")
print("=" * 60)