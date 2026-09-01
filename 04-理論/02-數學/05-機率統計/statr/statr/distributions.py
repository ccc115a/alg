"""Probability distributions and statistical functions"""

from typing import Optional
import math
from scipy import special
from scipy.stats import norm, t, chi2, f, binom, poisson

def dnorm(x: float, mean: float = 0, sd: float = 1) -> float:
    """Probability density function of normal distribution
    
    Args:
        x: Value at which to evaluate
        mean: Mean of the distribution (default 0)
        sd: Standard deviation (default 1)
    """
    return norm.pdf(x, loc=mean, scale=sd)

def pnorm(q: float, mean: float = 0, sd: float = 1, lower_tail: bool = True) -> float:
    """Cumulative distribution function of normal distribution
    
    Args:
        q: Quantile
        mean: Mean (default 0)
        sd: Standard deviation (default 1)
        lower_tail: If True (default), probability P(X <= q)
    """
    p = norm.cdf(q, loc=mean, scale=sd)
    return p if lower_tail else 1 - p

def qnorm(p: float, mean: float = 0, sd: float = 1, lower_tail: bool = True) -> float:
    """Quantile function (inverse CDF) of normal distribution
    
    Args:
        p: Probability
        mean: Mean (default 0)
        sd: Standard deviation (default 1)
        lower_tail: If True (default), use lower tail
    """
    if not lower_tail:
        p = 1 - p
    return norm.ppf(p, loc=mean, scale=sd)

def rnorm(n: int, mean: float = 0, sd: float = 1) -> list:
    """Generate random numbers from normal distribution
    
    Args:
        n: Number of samples
        mean: Mean (default 0)
        sd: Standard deviation (default 1)
    """
    return list(norm.rvs(loc=mean, scale=sd, size=n))

def dt(x: float, df: int) -> float:
    """Probability density function of Student's t distribution"""
    return t.pdf(x, df)

def pt(q: float, df: int, lower_tail: bool = True) -> float:
    """Cumulative distribution function of t distribution"""
    p = t.cdf(q, df)
    return p if lower_tail else 1 - p

def qt(p: float, df: int, lower_tail: bool = True) -> float:
    """Quantile function of t distribution"""
    if not lower_tail:
        p = 1 - p
    return t.ppf(p, df)

def rt(n: int, df: int) -> list:
    """Generate random numbers from t distribution"""
    return list(t.rvs(df, size=n))

def dchisq(x: float, df: int) -> float:
    """Probability density function of chi-square distribution"""
    return chi2.pdf(x, df)

def pchisq(q: float, df: int, lower_tail: bool = True) -> float:
    """Cumulative distribution function of chi-square distribution"""
    p = chi2.cdf(q, df)
    return p if lower_tail else 1 - p

def qchisq(p: float, df: int, lower_tail: bool = True) -> float:
    """Quantile function of chi-square distribution"""
    if not lower_tail:
        p = 1 - p
    return chi2.ppf(p, df)

def rchisq(n: int, df: int) -> list:
    """Generate random numbers from chi-square distribution"""
    return list(chi2.rvs(df, size=n))

def df(x: float, df1: int, df2: int) -> float:
    """Probability density function of F distribution"""
    return f.pdf(x, df1, df2)

def pf(q: float, df1: int, df2: int, lower_tail: bool = True) -> float:
    """Cumulative distribution function of F distribution"""
    p = f.cdf(q, df1, df2)
    return p if lower_tail else 1 - p

def qf(p: float, df1: int, df2: int, lower_tail: bool = True) -> float:
    """Quantile function of F distribution"""
    if not lower_tail:
        p = 1 - p
    return f.ppf(p, df1, df2)

def rf(n: int, df1: int, df2: int) -> list:
    """Generate random numbers from F distribution"""
    return list(f.rvs(df1, df2, size=n))

def dbinom(x: int, size: int, prob: float) -> float:
    """Probability mass function of binomial distribution"""
    return binom.pmf(x, size, prob)

def pbinom(q: int, size: int, prob: float, lower_tail: bool = True) -> float:
    """Cumulative distribution function of binomial distribution"""
    p = binom.cdf(q, size, prob)
    return p if lower_tail else 1 - p

def qbinom(p: float, size: int, prob: float, lower_tail: bool = True) -> float:
    """Quantile function of binomial distribution"""
    if not lower_tail:
        p = 1 - p
    return binom.ppf(p, size, prob)

def rbinom(n: int, size: int, prob: float) -> list:
    """Generate random numbers from binomial distribution"""
    return list(binom.rvs(size, prob, size=n))

def dpois(x: int, lambda_: float) -> float:
    """Probability mass function of Poisson distribution"""
    return poisson.pmf(x, lambda_)

def ppois(q: int, lambda_: float, lower_tail: bool = True) -> float:
    """Cumulative distribution function of Poisson distribution"""
    p = poisson.cdf(q, lambda_)
    return p if lower_tail else 1 - p

def qpois(p: float, lambda_: float, lower_tail: bool = True) -> float:
    """Quantile function of Poisson distribution"""
    if not lower_tail:
        p = 1 - p
    return poisson.ppf(p, lambda_)

def rpois(n: int, lambda_: float) -> list:
    """Generate random numbers from Poisson distribution"""
    return list(poisson.rvs(lambda_, size=n))