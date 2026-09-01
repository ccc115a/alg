# Statr - R-style Python Statistical Library

A Python statistical package inspired by R, providing probability distributions, descriptive statistics, and hypothesis tests with R-compatible API.

## Installation

```bash
pip install statr
```

## Quick Start

```python
import statr as R

# Probability distributions (R-style naming)
R.dnorm(0, 0, 1)        # density of N(0,1) at x=0
R.pnorm(1.96, 0, 1)     # P(X <= 1.96) for N(0,1)
R.qnorm(0.975, 0, 1)   # quantile for p=0.975
R.rnorm(100, 0, 1)     # 100 random samples from N(0,1)

# t, chi-square, F distributions
R.dt(2, 10)            # density of t(10) at x=2
R.pchisq(3.84, 1)      # P(X <= 3.84) for chi-square(1)
R.df(2.5, 3, 10)       # density of F(3,10) at x=2.5

# Descriptive statistics
x = [2, 4, 6, 8, 10]
R.mean(x)              # arithmetic mean
R.median(x)            # median
R.var(x)               # sample variance
R.sd(x)               # sample standard deviation
R.summary(x)          # comprehensive summary
```

## Hypothesis Tests

### One-sample t-test

```python
import statr as R

data = [101, 102, 100, 99, 101, 103, 100, 101]
result = R.t_test(data, mu=100)
print(result)
# {'statistic': 2.06, 'df': 7, 'p_value': 0.079, 
#  'estimate': 100.875, 'ci': (98.87, 102.88), 'ci_level': 0.95}
```

### Two-sample t-test

```python
group1 = [85, 90, 88, 92, 87]
group2 = [78, 82, 80, 76, 79]
result = R.t_test(group1, group2)
print(result)
```

### Z-test (known sigma)

```python
data = R.rnorm(50, 100, 15)
result = R.z_test(data, sigma=15, mu=100)
print(result)
```

### Chi-square test

```python
observed = [[10, 20], [15, 15], [5, 5]]
result = R.chisq_test(observed)
print(result)
```

### ANOVA

```python
group1 = [22, 25, 28, 24]
group2 = [30, 33, 28, 31]
group3 = [18, 20, 22, 19]
result = R.anova(group1, group2, group3)
print(result)
```

### Confidence Interval

```python
data = [10.2, 9.8, 10.1, 10.3, 9.9]
result = R.conf_interval(data)
print(result)  # {'estimate': 10.06, 'ci': (9.83, 10.29), ...}
```

## Visualization

```python
import statr as R

data = [101, 102, 100, 99, 101, 103, 100, 101]
result = R.t_test(data, mu=100)

# Plot confidence interval
R.plot_t_ci(data, result['ci'], result['estimate'])
```

## API Reference

### Distributions

| R Function | Description |
|------------|-------------|
| `dnorm(x, mean, sd)` | Normal density |
| `pnorm(q, mean, sd)` | Normal CDF |
| `qnorm(p, mean, sd)` | Normal quantile |
| `rnorm(n, mean, sd)` | Normal random numbers |
| `dt(x, df)` | t-distribution density |
| `pt(q, df)` | t-distribution CDF |
| `qt(p, df)` | t-distribution quantile |
| `rt(n, df)` | t-distribution random numbers |
| `dchisq(x, df)` | Chi-square density |
| `pchisq(q, df)` | Chi-square CDF |
| `qchisq(p, df)` | Chi-square quantile |
| `rchisq(n, df)` | Chi-square random numbers |
| `df(x, df1, df2)` | F-density |
| `pf(q, df1, df2)` | F-CDF |
| `qf(p, df1, df2)` | F-quantile |
| `rf(n, df1, df2)` | F-random numbers |
| `dbinom(x, size, prob)` | Binomial PMF |
| `pbinom(q, size, prob)` | Binomial CDF |
| `qbinom(p, size, prob)` | Binomial quantile |
| `rbinom(n, size, prob)` | Binomial random numbers |
| `dpois(x, lambda)` | Poisson PMF |
| `ppois(q, lambda)` | Poisson CDF |
| `qpois(p, lambda)` | Poisson quantile |
| `rpois(n, lambda)` | Poisson random numbers |

### Statistics

| Function | Description |
|----------|-------------|
| `mean(x)` | Arithmetic mean |
| `median(x)` | Median |
| `var(x)` | Sample variance |
| `sd(x)` | Standard deviation |
| `cov(x, y)` | Covariance |
| `cor(x, y)` | Pearson correlation |
| `quantile(x, p)` | Quantile (0<p<1) |
| `summary(x)` | Full summary |

### Tests

| Function | Description |
|----------|-------------|
| `t_test(x, y, mu, alpha, alternative, paired)` | t-test |
| `z_test(x, sigma, mu, alpha)` | Z-test |
| `chisq_test(observed, expected, alpha)` | Chi-square test |
| `anova(*groups)` | One-way ANOVA |
| `conf_interval(x, sigma, alpha)` | CI for mean |

## License

MIT License