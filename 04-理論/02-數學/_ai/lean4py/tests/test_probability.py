import pytest
import math
from lean4py.probability import (
    ProbabilitySpace, Event, RandomVariable,
    ExpectedValue, Variance, StandardDeviation, Covariance, Correlation,
    NormalDistribution, BinomialDistribution, PoissonDistribution, UniformDistribution,
    bayes_theorem, law_of_total_probability, hypothesis_test, confidence_interval
)

class TestProbabilitySpace:
    def test_uniform_space(self):
        ps = ProbabilitySpace.uniform({1, 2, 3, 4, 5, 6})
        assert abs(ps.probability(3) - 1/6) < 1e-10

    def test_dice_space(self):
        ps = ProbabilitySpace.dice()
        assert len(ps.sample_space) == 6

    def test_conditional_probability(self):
        ps = ProbabilitySpace.uniform({1, 2, 3, 4, 5, 6})
        even = {2, 4, 6}
        greater_than_3 = {4, 5, 6}
        p_even_given_gt3 = ps.conditional_probability(even, greater_than_3)
        assert abs(p_even_given_gt3 - 2/3) < 1e-10

class TestEvent:
    def test_event_init(self):
        e = Event({1, 2, 3}, "A")
        assert e.elements == {1, 2, 3}
        assert e.name == "A"

    def test_event_intersection(self):
        e1 = Event({1, 2, 3})
        e2 = Event({2, 3, 4})
        result = e1 & e2
        assert result.elements == {2, 3}

    def test_event_union(self):
        e1 = Event({1, 2})
        e2 = Event({2, 3})
        result = e1 | e2
        assert result.elements == {1, 2, 3}

class TestRandomVariable:
    def test_rv_init(self):
        rv = RandomVariable('X', {1: 0.5, 2: 0.3, 3: 0.2})
        assert rv.name == 'X'

    def test_expected_value(self):
        rv = RandomVariable('X', {1: 0.5, 2: 0.3, 3: 0.2})
        assert abs(ExpectedValue(rv) - 1.7) < 1e-10

    def test_variance(self):
        rv = RandomVariable('X', {0: 0.5, 1: 0.5})
        assert abs(Variance(rv) - 0.25) < 1e-10

    def test_std_dev(self):
        rv = RandomVariable('X', {0: 0.5, 1: 0.5})
        assert abs(StandardDeviation(rv) - 0.5) < 1e-10

class TestNormalDistribution:
    def test_normal_pdf(self):
        N = NormalDistribution(0, 1)
        assert abs(N.pdf(0) - 0.3989422804014317) < 1e-6

    def test_normal_cdf(self):
        N = NormalDistribution(0, 1)
        assert abs(N.cdf(0) - 0.5) < 1e-6

    def test_normal_mean(self):
        N = NormalDistribution(5, 4)
        assert N.mean() == 5

    def test_normal_variance(self):
        N = NormalDistribution(5, 4)
        assert N.variance() == 4

class TestBinomialDistribution:
    def test_binomial_pdf(self):
        B = BinomialDistribution(10, 0.5)
        assert abs(B.pdf(5) - 0.24609375) < 1e-6

    def test_binomial_mean(self):
        B = BinomialDistribution(10, 0.3)
        assert abs(B.mean() - 3.0) < 1e-10

    def test_binomial_variance(self):
        B = BinomialDistribution(10, 0.5)
        assert abs(B.variance() - 2.5) < 1e-10

class TestPoissonDistribution:
    def test_poisson_pdf(self):
        P = PoissonDistribution(3)
        assert abs(P.pdf(2) - 0.22404180765553775) < 1e-6

    def test_poisson_mean(self):
        P = PoissonDistribution(5)
        assert P.mean() == 5

class TestUniformDistribution:
    def test_uniform_pdf(self):
        U = UniformDistribution(0, 1)
        assert abs(U.pdf(0.5) - 1.0) < 1e-10

    def test_uniform_cdf(self):
        U = UniformDistribution(0, 1)
        assert abs(U.cdf(0.5) - 0.5) < 1e-10

    def test_uniform_mean(self):
        U = UniformDistribution(2, 5)
        assert abs(U.mean() - 3.5) < 1e-10

class TestBayesTheorem:
    def test_bayes_simple(self):
        p_a_given_b = 0.8
        p_b_given_a = 0.3
        p_a = 0.4
        p_b = 0.5
        result = bayes_theorem(p_a_given_b, p_b_given_a, p_a, p_b)
        expected = (0.3 * 0.4) / 0.5
        assert abs(result - expected) < 1e-10

class TestHypothesisTest:
    def test_z_test(self):
        sample = [10.2, 9.8, 10.1, 10.3, 9.9]
        result = hypothesis_test('z', sample, mu=10.0)
        assert 'z' in result
        assert 'p_value' in result

    def test_t_test(self):
        sample = [10.2, 9.8, 10.1, 10.3, 9.9]
        result = hypothesis_test('t', sample, mu=10.0)
        assert 't' in result
        assert 'p_value' in result

class TestConfidenceInterval:
    def test_confidence_interval(self):
        sample = [10.2, 9.8, 10.1, 10.3, 9.9]
        lower, upper = confidence_interval(sample, 0.95)
        assert lower < upper
        assert 10.0 >= lower and 10.0 <= upper