"""隨機過程定理驗證。

用 function.py 中的計算函數驗證定理是否成立。
"""

import numpy as np
import math
from .function import (
    brownian_motion,
    geometric_brownian_motion,
    ito_integral,
    black_scholes_call,
    black_scholes_put,
    greeks,
)


def brownian_motion_properties():
    """布朗運動性質驗證。

    1. W(0) = 0
    2. E[W(t)] = 0
    3. Var[W(t)] = t
    """
    T = 1.0
    n_steps = 1000
    n_paths = 1000
    np.random.seed(42)

    t, W = brownian_motion(T, n_steps, seed=42)

    final_values = []
    for _ in range(n_paths):
        _, W = brownian_motion(T, n_steps)
        final_values.append(W[-1])

    final_values = np.array(final_values)

    mean_W = np.mean(final_values)
    var_W = np.var(final_values)

    return {
        "W(0)": W[0],
        "E[W(T)]": mean_W,
        "Var[W(T)]": var_W,
        "exact_mean": 0.0,
        "exact_var": T,
        "pass": bool(abs(mean_W) < 0.1 and abs(var_W - T) < 0.2)
    }


def geometric_brownian_motion_properties():
    """幾何布朗運動性質驗證。

    E[S(t)] = S0 * e^(μt)
    """
    S0 = 100
    mu = 0.05
    sigma = 0.2
    T = 1.0
    n_steps = 100
    n_paths = 1000
    np.random.seed(42)

    t, S = geometric_brownian_motion(S0, mu, sigma, T, n_steps, n_paths)

    final_prices = S[:, -1]
    mean_S = np.mean(final_prices)
    exact_mean = S0 * math.exp(mu * T)

    return {
        "S0": S0,
        "exact_mean": exact_mean,
        "sample_mean": mean_S,
        "error": abs(mean_S - exact_mean),
        "pass": bool(abs(mean_S - exact_mean) < 3.0)
    }


def ito_integral_martingale():
    """伊藤積分是鞅。

    E[∫f dW] = 0
    """
    f = lambda t, W: W
    np.random.seed(42)

    result = ito_integral(f, 1.0, 1000, seed=42)

    return {
        "E[∫W dW]": result,
        "expected": 0.0,
        "pass": bool(abs(result) < 0.5)
    }


def black_scholes_call_put_parity():
    """Call-Put 平價定理驗證。

    C - P = S - K * e^(-rT)
    """
    S0 = 100
    K = 100
    T = 1.0
    r = 0.05
    sigma = 0.2

    call = black_scholes_call(S0, K, T, r, sigma)
    put = black_scholes_put(S0, K, T, r, sigma)

    lhs = call - put
    rhs = S0 - K * math.exp(-r * T)
    error = abs(lhs - rhs)

    return {
        "C": call,
        "P": put,
        "C - P": lhs,
        "S - K*exp(-rT)": rhs,
        "error": error,
        "pass": bool(error < 0.01)
    }


def black_scholes_greeks():
    """Black-Scholes Greeks 性質驗證。

    1. Delta + N(d1) in [0, 1]
    2. Gamma 為正
    3. Vega > 0
    """
    S0 = 100
    K = 100
    T = 1.0
    r = 0.05
    sigma = 0.2

    g_call = greeks(S0, K, T, r, sigma, "call")
    g_put = greeks(S0, K, T, r, sigma, "put")

    call_delta_ok = 0 <= g_call["delta"] <= 1
    put_delta_ok = -1 <= g_put["delta"] <= 0
    gamma_ok = g_call["gamma"] > 0
    vega_ok = g_call["vega"] > 0

    return {
        "call_delta": g_call["delta"],
        "put_delta": g_put["delta"],
        "gamma": g_call["gamma"],
        "vega": g_call["vega"],
        "call_delta_ok": call_delta_ok,
        "put_delta_ok": put_delta_ok,
        "gamma_positive": gamma_ok,
        "vega_positive": vega_ok,
        "pass": bool(call_delta_ok and put_delta_ok and gamma_ok and vega_ok)
    }


def ito_lemma_simple():
    """伊藤引理簡單驗證。

    d(W²) = 2W dW + dt
    """
    np.random.seed(42)

    T = 1.0
    n_steps = 1000

    _, W = brownian_motion(T, n_steps, seed=42)

    W_squared = W ** 2
    dW2 = np.diff(W_squared)
    dt = T / n_steps

    lhs_mean = np.mean(dW2)
    rhs_term = 2 * W[:-1] * np.diff(W)
    rhs_mean = np.mean(rhs_term) + dt

    return {
        "E[d(W²)]": lhs_mean,
        "E[2W dW + dt]": rhs_mean,
        "error": abs(lhs_mean - rhs_mean),
        "pass": bool(abs(lhs_mean - rhs_mean) < 0.1)
    }


__all__ = [
    "brownian_motion_properties",
    "geometric_brownian_motion_properties",
    "ito_integral_martingale",
    "black_scholes_call_put_parity",
    "black_scholes_greeks",
    "ito_lemma_simple",
]