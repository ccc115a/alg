"""統計函數：統計計算函數。

描述統計、假設檢定輔助函數。
"""

import numpy as np
from typing import List, Tuple, Callable


def mean(x: List[float]) -> float:
    """樣本平均。

    Args:
        x: 資料

    Returns:
        平均值
    """
    return np.mean(x)


def variance(x: List[float], ddof: int = 1) -> float:
    """變異數。

    Args:
        x: 資料
        ddof: 自由度調整

    Returns:
        變異數
    """
    return np.var(x, ddof=ddof)


def std(x: List[float], ddof: int = 1) -> float:
    """標準差。

    Args:
        x: 資料
        ddof: 自由度調整

    Returns:
        標準差
    """
    return np.std(x, ddof=ddf)


def covariance(x: List[float], y: List[float], ddof: int = 1) -> float:
    """共變異數。

    Args:
        x: 資料 1
        y: 資料 2
        ddof: 自由度調整

    Returns:
        共變異數
    """
    return np.cov(x, y, ddof=ddof)[0, 1]


def correlation(x: List[float], y: List[float]) -> float:
    """Pearson 相關係數。

    Args:
        x: 資料 1
        y: 資料 2

    Returns:
        相關係數
    """
    return np.corrcoef(x, y)[0, 1]


def quantile(x: List[float], p: float) -> float:
    """分位數。

    Args:
        x: 資料
        p: 機率 (0-1)

    Returns:
        分位數
    """
    return np.quantile(x, p)


def iqr(x: List[float]) -> float:
    """四分位距 (IQR)。

    Args:
        x: 資料

    Returns:
        IQR
    """
    q75 = np.quantile(x, 0.75)
    q25 = np.quantile(x, 0.25)
    return q75 - q25


def z_score(x: float, mu: float, sigma: float) -> float:
    """Z-score。

    Args:
        x: 觀測值
        mu: 均值
        sigma: 標準差

    Returns:
        z 分數
    """
    return (x - mu) / sigma


def standardize(x: List[float]) -> List[float]:
    """標準化 (Z-score)。

    Args:
        x: 資料

    Returns:
        標準化後的資料
    """
    mu = np.mean(x)
    sigma = np.std(x)
    return [(xi - mu) / sigma for xi in x]


def bootstrap_ci(x: List[float], statistic_fn: Callable, n_bootstrap: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
    """Bootstrap 信賴區間。

    Args:
        x: 原始資料
        statistic_fn: 統計量函數
        n_bootstrap: Bootstrap 次數
        alpha: 顯著水準

    Returns:
        (下界, 上界)
    """
    stats = [statistic_fn(np.random.choice(x, size=len(x), replace=True)) for _ in range(n_bootstrap)]
    lower = np.quantile(stats, alpha / 2)
    upper = np.quantile(stats, 1 - alpha / 2)
    return lower, upper


def log_likelihood(y: List[float], y_pred: List[float]) -> float:
    """對數概似。

    Args:
        y: 真實值
        y_pred: 預測值

    Returns:
        log-likelihood
    """
    return -np.sum((np.array(y) - np.array(y_pred))**2) / 2


def aic(n: int, log_lik: float, k: int) -> float:
    return 2 * k - 2 * log_lik


def bic(n: int, log_lik: float, k: int) -> float:
    return k * np.log(n) - 2 * log_lik


def median(x) -> float:
    s = sorted(x)
    n = len(s)
    if n % 2 == 0:
        return (s[n//2 - 1] + s[n//2]) / 2
    return s[n//2]


def summary(x) -> dict:
    return {
        "min": min(x),
        "q1": quantile(x, 0.25),
        "median": median(x),
        "mean": mean(x),
        "q3": quantile(x, 0.75),
        "max": max(x),
        "sd": std(x),
        "var": variance(x),
        "n": len(x)
    }


def range_stat(x) -> float:
    return max(x) - min(x)


__all__ = [
    "mean", "median", "variance", "std", "covariance", "correlation",
    "quantile", "iqr", "z_score", "standardize", "bootstrap_ci",
    "log_likelihood", "aic", "bic", "summary", "range_stat",
]