"""隨機過程函數。

布朗運動、伊藤積分、Black-Scholes 等計算函數。
"""

import numpy as np
from typing import Callable, Tuple


def brownian_motion(T: float, n_steps: int = 100, seed: int = None) -> Tuple[np.ndarray, np.ndarray]:
    """標準布朗運動模擬。

    Args:
        T: 終止時間
        n_steps: 步數
        seed: 隨機種子

    Returns:
        (時間陣列, 路徑)
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)

    dW = np.sqrt(dt) * np.random.randn(n_steps + 1)
    W = np.cumsum(dW)
    W[0] = 0

    return t, W


def geometric_brownian_motion(S0: float, mu: float, sigma: float, T: float, n_steps: int = 100, n_paths: int = 1, seed: int = None) -> Tuple[np.ndarray, np.ndarray]:
    """幾何布朗運動模擬。

    dS = μS dt + σS dW
    S(t) = S0 * exp((μ - σ²/2)t + σW(t))

    Args:
        S0: 初始價格
        mu: 漂移率
        sigma: 波動率
        T: 終止時間
        n_steps: 步數
        n_paths: 路徑數
        seed: 隨機種子

    Returns:
        (時間陣列, 價格路徑)
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)

    Z = np.random.randn(n_paths, n_steps + 1)
    dW = np.sqrt(dt) * Z
    W = np.cumsum(dW, axis=1)
    W[:, 0] = 0

    drift = (mu - 0.5 * sigma**2) * t
    diffusion = sigma * W
    S = S0 * np.exp(drift + diffusion)

    return t, S


def ito_integral(f: Callable, T: float, n_steps: int = 100, seed: int = None) -> float:
    """伊藤積分 ∫₀ᵀ f(t) dW(t)。

    Args:
        f: 被積分函數 f(t, W(t))
        T: 終止時間
        n_steps: 步數
        seed: 隨機種子

    Returns:
        伊藤積分值
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)
    dW = np.sqrt(dt) * np.random.randn(n_steps + 1)
    W = np.cumsum(dW)
    W[0] = 0

    f_vals = np.array([f(t[i], W[i]) for i in range(n_steps + 1)])
    increments = f_vals[:-1] * dW[1:]
    return np.sum(increments)


def black_scholes_call(S0: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes 歐式看漲期權定價。

    Args:
        S0: 現貨價格
        K: 履約價
        T: 到期日
        r: 無風險利率
        sigma: 波動率

    Returns:
        期權價格
    """
    from scipy.stats import norm

    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def black_scholes_put(S0: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes 歐式看跌期權定價。

    Args:
        S0: 現貨價格
        K: 履約價
        T: 到期日
        r: 無風險利率
        sigma: 波動率

    Returns:
        期權價格
    """
    from scipy.stats import norm

    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)


def greeks(S0: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict:
    """計算 Black-Scholes Greeks。

    Args:
        S0: 現貨價格
        K: 履約價
        T: 到期日
        r: 無風險利率
        sigma: 波動率
        option_type: "call" 或 "put"

    Returns:
        Greeks 字典
    """
    from scipy.stats import norm

    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        delta = norm.cdf(d1)
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    else:
        delta = norm.cdf(d1) - 1
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

    gamma = norm.pdf(d1) / (S0 * sigma * np.sqrt(T))
    vega = S0 * norm.pdf(d1) * np.sqrt(T)
    theta = -S0 * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2)

    if option_type == "put":
        theta = -S0 * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)

    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta,
        "rho": rho
    }


__all__ = [
    "brownian_motion",
    "geometric_brownian_motion",
    "ito_integral",
    "black_scholes_call",
    "black_scholes_put",
    "greeks",
]