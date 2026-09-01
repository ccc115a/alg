"""Pytest tests for math4py statistics module"""

import pytest
import math

from math4py.statistics.distributions import (
    dnorm, pnorm, qnorm, rnorm,
    dt, pt, qt, rt,
    dchisq, pchisq, qchisq, rchisq,
    dbinom, pbinom, qbinom, rbinom,
    dpois, ppois, qpois, rpois,
    df as f_distr, pf as f_pf
)
from math4py.statistics.stats import mean, median, var, sd, cov, cor, quantile, summary, min_val, max_val
from math4py.statistics.tests import t_test, z_test, chisq_test, anova, conf_interval

class TestNormalDistribution:
    def test_dnorm(self):
        assert abs(dnorm(0, 0, 1) - 0.3989422804014317) < 1e-10

    def test_pnorm(self):
        assert abs(pnorm(0, 0, 1) - 0.5) < 1e-10

    def test_qnorm(self):
        assert abs(qnorm(0.5, 0, 1) - 0.0) < 1e-10

    def test_rnorm(self):
        samples = rnorm(100, 0, 1)
        assert len(samples) == 100
        assert abs(mean(samples)) < 0.3

class TestTDistribution:
    def test_dt(self):
        assert dt(0, 10) > 0

    def test_pt(self):
        assert abs(pt(0, 10) - 0.5) < 1e-10

    def test_qt(self):
        assert abs(qt(0.975, 10) - 2.228) < 0.01

class TestChiSquare:
    def test_dchisq(self):
        assert dchisq(1, 1) > 0

    def test_pchisq(self):
        assert pchisq(0, 1) == 0

    def test_qchisq(self):
        assert qchisq(0.95, 1) > 0

class TestFDistribution:
    def test_df(self):
        assert f_distr(1, 3, 10) > 0

    def test_pf(self):
        assert f_pf(0, 3, 10) == 0

    def test_qf(self):
        assert f_pf(0.5, 3, 10) > 0

class TestBinomial:
    def test_dbinom(self):
        assert dbinom(5, 10, 0.5) > 0

    def test_pbinom(self):
        assert abs(pbinom(5, 10, 0.5) - 0.623) < 0.01

class TestPoisson:
    def test_dpois(self):
        assert dpois(3, 3) > 0

    def test_ppois(self):
        assert ppois(2, 3) > 0

class TestDescriptiveStats:
    def test_mean(self):
        assert mean([1, 2, 3, 4, 5]) == 3.0

    def test_median_odd(self):
        assert median([1, 2, 3, 4, 5]) == 3.0

    def test_median_even(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_var(self):
        assert abs(var([1, 2, 3, 4, 5]) - 2.5) < 1e-10

    def test_sd(self):
        assert abs(sd([1, 2, 3, 4, 5]) - math.sqrt(2.5)) < 1e-10

    def test_quantile(self):
        x = [1, 2, 3, 4, 5]
        assert quantile(x, 0.5) == 3.0

    def test_summary(self):
        s = summary([1, 2, 3, 4, 5])
        assert "Mean" in s
        assert "Median" in s
        assert "SD" in s

class TestTTest:
    def test_t_test_one_sample(self):
        data = [101, 102, 100, 99, 101, 103, 100, 101]
        result = t_test(data, mu=100)
        assert "statistic" in result
        assert "p_value" in result
        assert "df" in result
        assert "ci" in result

    def test_t_test_two_sample(self):
        g1 = [85, 90, 88, 92, 87]
        g2 = [78, 82, 80, 76, 79]
        result = t_test(g1, g2)
        assert result["statistic"] > 0

    def test_t_test_paired(self):
        before = [100, 102, 98, 105, 101]
        after = [95, 99, 96, 100, 98]
        result = t_test(before, after, paired=True)
        assert "statistic" in result

class TestZTest:
    def test_z_test(self):
        data = [101, 102, 100, 99, 101, 103, 100, 101]
        result = z_test(data, sigma=2, mu=100)
        assert "statistic" in result
        assert "p_value" in result

class TestChiSquareTest:
    def test_chisq_test(self):
        observed = [[10, 20], [15, 15]]
        result = chisq_test(observed)
        assert "statistic" in result
        assert "df" in result
        assert "p_value" in result

class TestAnova:
    def test_anova(self):
        g1 = [22, 25, 28, 24]
        g2 = [30, 33, 28, 31]
        g3 = [18, 20, 22, 19]
        result = anova(g1, g2, g3)
        assert "statistic" in result
        assert "p_value" in result
        assert "df1" in result
        assert "df2" in result

class TestConfInterval:
    def test_conf_interval(self):
        data = [10.2, 9.8, 10.1, 10.3, 9.9]
        result = conf_interval(data)
        assert "estimate" in result
        assert "ci" in result
        assert result["ci"][0] < result["estimate"] < result["ci"][1]