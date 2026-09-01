"""stochastic - Stochastic processes and calculus for math4py."""
from . import calculus as C
from .process import (
    BrownianMotion,
    GeometricBrownianMotion,
    OrnsteinUhlenbeck,
    BrownianBridge,
)

from .calculus import (
    ItoIntegral,
    ito_lemma_demo,
    SDESolver,
    BlackScholes,
    AmericanOption,
    brownian_motion,
    ito_integral_plot,
    options_plot,
)

__all__ = [
    "C",
    "process",
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