"""
stoc4py — 隨機微積分 Python 套件
=====================================
模組：
  - process   : 隨機過程（布朗運動、幾何布朗運動、O-U 過程等）
  - ito        : 伊藤積分與伊藤引理
  - sde        : 隨機微分方程求解器（Euler-Maruyama、Milstein）
  - options    : 期權定價（Black-Scholes，美式 / 歐式）
  - plot       : 視覺化工具
"""

from .process import (
    BrownianMotion,
    GeometricBrownianMotion,
    OrnsteinUhlenbeck,
    BrownianBridge,
)
from .ito import ItoIntegral, ito_lemma_demo
from .sde import SDESolver
from .options import BlackScholes, AmericanOption
from .plot import StochPlot

__version__ = "1.0.0"
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
    "StochPlot",
]
