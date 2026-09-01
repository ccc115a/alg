"""math4py - A Python library for mathematics."""

from .geometry import Vector, Point
from .geometry._3d import Line3D, Plane3D
from . import statistics as R

from .statistics import (
    dnorm, pnorm, qnorm, rnorm,
    dt, pt, qt, rt,
    dchisq, pchisq, qchisq, rchisq,
    df, pf, qf, rf,
    dbinom, pbinom, qbinom, rbinom,
    dpois, ppois, qpois, rpois,
    mean, median, variance, std, covariance, correlation,
    quantile, summary, range_stat,
    t_test, z_test, chisq_test, anova, conf_interval,
    entropy, cross_entropy, kl_divergence, mutual_information,
)

from .plot import (
    plot, hist, boxplot, qqnorm,
    plot_entropy, plot_kl,
    brownian_motion, ito_integral_plot, options_plot,
)

__all__ = [
    "Vector", "Point", "Line", "Plane",
    "R",
    "dnorm", "pnorm", "qnorm", "rnorm",
    "dt", "pt", "qt", "rt",
    "dchisq", "pchisq", "qchisq", "rchisq",
    "df", "pf", "qf", "rf",
    "dbinom", "pbinom", "qbinom", "rbinom",
    "dpois", "ppois", "qpois", "rpois",
    "mean", "median", "var", "sd", "cov", "cor", "quantile", "summary",
    "t_test", "z_test", "chisq_test", "anova", "conf_interval",
    "entropy", "cross_entropy", "kl_divergence", "mutual_information",
    "plot", "hist", "boxplot", "qqnorm",
    "plot_entropy", "plot_kl",
    "brownian_motion", "ito_integral_plot", "options_plot",
]
__version__ = "0.1.0"
