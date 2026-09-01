"""統計定理。

Central Limit Theorem, Law of Large Numbers, etc.
"""

import numpy as np
from typing import Callable, Tuple, List


def central_limit_theorem(sample_fn: Callable, n: int, n_samples: int = 10000) -> Tuple[float, float]:
    """中央極限定理。

    樣本均值趨近 N(μ, σ²/n)

    Args:
        sample_fn: 產生隨機樣本的函數
        n: 每次樣本數
        n_samples: 重複次數

    Returns:
        (均值, 標準差)
    """
    sample_means = [np.mean(sample_fn(n)) for _ in range(n_samples)]
    return np.mean(sample_means), np.std(sample_means)


def law_of_large_numbers(sample_fn: Callable, n: int) -> float:
    """大數定律。

    樣本均值趨近期望值

    Args:
        sample_fn: 產生隨機樣本的函數
        n: 樣本數

    Returns:
        收斂值
    """
    return np.mean(sample_fn(n))


def chebyshev_inequality(var: float, k: float) -> float:
    """柴比雪夫不等式。

    P(|X-μ| ≥ kσ) ≤ 1/k²

    Args:
        var: 變異數
        k: 倍數

    Returns:
        上界
    """
    return 1.0 / (k ** 2)


def markov_inequality(x: List[float], k: float) -> float:
    """馬可夫不等式。

    P(X ≥ k) ≤ E[X]/k

    Args:
        x: 樣本
        k: 閾值

    Returns:
        上界
    """
    return np.mean(x) / k


def bernoulli_trials(n: int, p: float, k: int) -> float:
    """二項分布。

    P(X=k) = C(n,k) p^k (1-p)^(n-k)

    Args:
        n: 試驗次數
        p: 成功機率
        k: 成功次數

    Returns:
        機率
    """
    from scipy.stats import binom
    return binom.pmf(k, n, p)


def multinomial_prob(counts: List[int], probs: List[float]) -> float:
    """多項分布。

    P(X1=n1, ..., Xk=nk) = n! / (n1! ... nk!) * p1^n1 * ...

    Args:
        counts: 各類次數
        probs: 各類機率

    Returns:
        機率
    """
    from scipy.stats import multinomial
    n = sum(counts)
    return multinomial.pmf(counts, n, probs)


def normal_approx_binom(n: int, p: float, k: int) -> float:
    """常態近似二項分布。

    Args:
        n: 試驗次數
        p: 成功機率
        k: 成功次數

    Returns:
        近似機率
    """
    from scipy.stats import norm
    mu = n * p
    sigma = np.sqrt(n * p * (1 - p))
    return norm.pdf(k, mu, sigma)


def poisson_approx_binom(n: int, p: float, k: int) -> float:
    """卜瓦松近似。

    λ = np

    Args:
        n: 試驗次數
        p: 成功機率
        k: 成功次數

    Returns:
        近似機率
    """
    from scipy.stats import poisson
    lam = n * p
    return poisson.pmf(k, lam)


def bayes_theorem(p_a: float, p_b_given_a: float, p_b: float) -> float:
    """貝斯定理。

    P(A|B) = P(B|A) P(A) / P(B)

    Args:
        p_a: P(A)
        p_b_given_a: P(B|A)
        p_b: P(B)

    Returns:
        P(A|B)
    """
    return p_b_given_a * p_a / p_b


def posterior(prior: List[float], likelihood: List[float]) -> List[float]:
    """事後機率 (Bayes)。

    Args:
        prior: 先驗
        likelihood: 概似

    Returns:
        事後
    """
    unnorm = np.array(prior) * np.array(likelihood)
    return unnorm / unnorm.sum()


def crlb_lower_bound(fisher_info: float, n: int) -> float:
    """克拉美-羅下界。

    Var(θ̂) ≥ 1 / (n I(θ))

    Args:
        fisher_info: 費雪資訊
        n: 樣本數

    Returns:
        下界
    """
    return 1.0 / (n * fisher_info)


def information_entropy(p: List[float], base: float = 2.0) -> float:
    """資訊熵。

    H(X) = -Σ p(x) log(p(x))

    Args:
        p: 機率分佈
        base: 對數底

    Returns:
        熵
    """
    p = np.array(p)
    p = p[p > 0]
    return -np.sum(p * np.log(p) / np.log(base))


def mutual_information(x: List[float], y: List[float]) -> float:
    """互資訊。

    I(X;Y) = H(X) + H(Y) - H(X,Y)

    Args:
        x: 隨機變數 1
        y: 隨機變數 2

    Returns:
        互資訊
    """
    return information_entropy(x) + information_entropy(y) - information_entropy(x + y)


__all__ = [
    "central_limit_theorem",
    "law_of_large_numbers",
    "chebyshev_inequality",
    "markov_inequality",
    "bernoulli_trials",
    "multinomial_prob",
    "normal_approx_binom",
    "poisson_approx_binom",
    "bayes_theorem",
    "posterior",
    "crlb_lower_bound",
    "information_entropy",
    "mutual_information",
]