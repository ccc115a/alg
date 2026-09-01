"""Statr: Python Statistical Library inspired by R

A comprehensive statistical package for Python featuring:
- Probability distributions (normal, t, chi-square, F, binomial, Poisson)
- Descriptive statistics (mean, median, var, sd, cov, cor)
- Hypothesis tests (t-test, z-test, chi-square test, ANOVA)
- Confidence intervals with visualization
"""

__version__ = "0.1.0"

from . import distributions as D
from . import stats as S
from . import tests as T
from . import plot as P

dnorm = D.dnorm; pnorm = D.pnorm; qnorm = D.qnorm; rnorm = D.rnorm
dt = D.dt; pt = D.pt; qt = D.qt; rt = D.rt
dchisq = D.dchisq; pchisq = D.pchisq; qchisq = D.qchisq; rchisq = D.rchisq
df = D.df; pf = D.pf; qf = D.qf; rf = D.rf
dbinom = D.dbinom; pbinom = D.pbinom; qbinom = D.qbinom; rbinom = D.rbinom
dpois = D.dpois; ppois = D.ppois; qpois = D.qpois; rpois = D.rpois

mean = S.mean; median = S.median; var = S.var; sd = S.sd
cov = S.cov; cor = S.cor; quantile = S.quantile; summary = S.summary

t_test = T.t_test; z_test = T.z_test; chisq_test = T.chisq_test
anova = T.anova; conf_interval = T.conf_interval

plot_t_ci = P.plot_t_ci; plot_z_ci = P.plot_z_ci
plot_chisq_ci = P.plot_chisq_ci; plot_anova_ci = P.plot_anova_ci
plot_distribution = P.plot_distribution

__all__ = [
    "dnorm", "pnorm", "qnorm", "rnorm",
    "dt", "pt", "qt", "rt",
    "dchisq", "pchisq", "qchisq", "rchisq",
    "df", "pf", "qf", "rf",
    "dbinom", "pbinom", "qbinom", "rbinom",
    "dpois", "ppois", "qpois", "rpois",
    "mean", "median", "var", "sd", "cov", "cor", "quantile", "summary",
    "t_test", "z_test", "chisq_test", "anova", "conf_interval",
    "plot_t_ci", "plot_z_ci", "plot_chisq_ci", "plot_anova_ci", "plot_distribution"
]