"""R4Py: Python Statistical Library inspired by R

A comprehensive statistical package for Python featuring:
- Probability distributions (normal, t, chi-square, F, binomial, Poisson)
- Descriptive statistics (mean, median, var, sd, cov, cor)
- Hypothesis tests (t-test, z-test, chi-square test, ANOVA)
- Confidence intervals with visualization
- Information theory (entropy, cross-entropy, KL divergence, mutual information)
"""

__version__ = "0.1.0"

from . import distributions as D
from . import tests as T
from .function import (
    mean, median, variance, std, covariance, correlation,
    quantile, summary, range_stat, iqr,
)
from .entropy import entropy, cross_entropy, kl_divergence, mutual_information

dnorm = D.dnorm; pnorm = D.pnorm; qnorm = D.qnorm; rnorm = D.rnorm
dt = D.dt; pt = D.pt; qt = D.qt; rt = D.rt
dchisq = D.dchisq; pchisq = D.pchisq; qchisq = D.qchisq; rchisq = D.rchisq
df = D.df; pf = D.pf; qf = D.qf; rf = D.rf
dbinom = D.dbinom; pbinom = D.pbinom; qbinom = D.qbinom; rbinom = D.rbinom
dpois = D.dpois; ppois = D.ppois; qpois = D.qpois; rpois = D.rpois

var = variance
sd = std
cov = covariance
cor = correlation

t_test = T.t_test; z_test = T.z_test; chisq_test = T.chisq_test
anova = T.anova; conf_interval = T.conf_interval

__all__ = [
    "dnorm", "pnorm", "qnorm", "rnorm",
    "dt", "pt", "qt", "rt",
    "dchisq", "pchisq", "qchisq", "rchisq",
    "df", "pf", "qf", "rf",
    "dbinom", "pbinom", "qbinom", "rbinom",
    "dpois", "ppois", "qpois", "rpois",
    "mean", "median", "variance", "std", "covariance", "correlation",
    "quantile", "summary", "range_stat", "iqr",
    "t_test", "z_test", "chisq_test", "anova", "conf_interval",
    "entropy", "cross_entropy", "kl_divergence", "mutual_information",
]