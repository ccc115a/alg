"""Descriptive statistics"""

from typing import List, Optional
import math

def mean(x: List[float]) -> float:
    """Calculate arithmetic mean"""
    return sum(x) / len(x)

def median(x: List[float]) -> float:
    """Calculate median"""
    s = sorted(x)
    n = len(s)
    if n % 2 == 0:
        return (s[n//2 - 1] + s[n//2]) / 2
    return s[n//2]

def var(x: List[float], ddof: int = 1) -> float:
    """Calculate variance (sample var with ddof=1)"""
    m = mean(x)
    return sum((xi - m) ** 2 for xi in x) / (len(x) - ddof)

def sd(x: List[float], ddof: int = 1) -> float:
    """Calculate standard deviation"""
    return math.sqrt(var(x, ddof))

def cov(x: List[float], y: List[float], ddof: int = 1) -> float:
    """Calculate covariance"""
    mx, my = mean(x), mean(y)
    n = len(x)
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (n - ddof)

def cor(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient"""
    return cov(x, y) / (sd(x) * sd(y))

def quantile(x: List[float], p: float) -> float:
    """Calculate quantile (0 <= p <= 1)"""
    s = sorted(x)
    idx = p * (len(s) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return s[lo]
    return s[lo] * (hi - idx) + s[hi] * (idx - lo)

def summary(x: List[float]) -> dict:
    """Return comprehensive summary statistics"""
    return {
        "Min": min(x),
        "Q1": quantile(x, 0.25),
        "Median": median(x),
        "Mean": mean(x),
        "Q3": quantile(x, 0.75),
        "Max": max(x),
        "SD": sd(x),
        "Var": var(x),
        "N": len(x)
    }

def min_val(x: List[float]) -> float:
    return min(x) if len(x) > 0 else None

def max_val(x: List[float]) -> float:
    return max(x) if len(x) > 0 else None

def range_stat(x: List[float]) -> float:
    return max(x) - min(x)

def sum_stat(x: List[float]) -> float:
    return sum(x)