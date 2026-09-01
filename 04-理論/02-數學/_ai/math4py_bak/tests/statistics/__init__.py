"""Test suite for math4py statistics module"""

import pytest
from math4py.statistics.distributions import dnorm, pnorm, qnorm, rnorm
from math4py.statistics.stats import mean, median, var, sd
from math4py.statistics.tests import t_test, z_test

def test_dnorm():
    assert abs(dnorm(0, 0, 1) - 0.3989422804014317) < 1e-10

def test_pnorm():
    assert abs(pnorm(0, 0, 1) - 0.5) < 1e-10

def test_mean():
    assert mean([1, 2, 3, 4, 5]) == 3.0

def test_median():
    assert median([1, 2, 3, 4, 5]) == 3.0

def test_var():
    assert abs(var([1, 2, 3, 4, 5]) - 2.5) < 1e-10

def test_t_test():
    data = [101, 102, 100, 99, 101, 103, 100, 101]
    result = t_test(data, mu=100)
    assert "statistic" in result
    assert result["df"] == 7

def test_z_test():
    data = [101, 102, 100, 99, 101, 103, 100, 101]
    result = z_test(data, sigma=2, mu=100)
    assert "statistic" in result