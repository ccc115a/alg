"""
calculus — Stochastic calculus module for math4py

Modules:
- ito : 伊藤積分與伊藤引理
- sde : 隨機微分方程求解器（Euler-Maruyama、Milstein）
- options : 期權定價（Black-Scholes，美式 / 歐式）
"""

from ..process import (
    BrownianMotion,
    GeometricBrownianMotion,
    OrnsteinUhlenbeck,
    BrownianBridge,
)
from .ito import ItoIntegral, ito_lemma_demo
from .sde import SDESolver
from .options import BlackScholes, AmericanOption
from math4py.plot.rplot_stochastic import brownian_motion, ito_integral_plot, options_plot

__all__ = [
    "BrownianMotion",
    "GeometricBrownianMotion",
    "OrnsteinUhlenbeck",
    "BrownianBridge",
    "ItoIntegral",
    "ito_lemma_demo",
    "SDESolver",
    "BlackScholes",
    "AmericanOption",
    "brownian_motion",
    "ito_integral_plot",
    "options_plot",
]
