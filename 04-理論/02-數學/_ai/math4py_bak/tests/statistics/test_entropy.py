"""Tests for statistics/entropy.py - Information theory functions."""

import pytest
import numpy as np
from math4py.statistics.entropy import (
    entropy, cross_entropy, kl_divergence, mutual_information
)


class TestEntropy:
    def test_uniform_2(self):
        """Uniform distribution over 2 outcomes = 1 bit."""
        p = [0.5, 0.5]
        assert abs(entropy(p) - 1.0) < 1e-9

    def test_uniform_4(self):
        """Uniform distribution over 4 outcomes = 2 bits."""
        p = [0.25, 0.25, 0.25, 0.25]
        assert abs(entropy(p) - 2.0) < 1e-9

    def test_certain(self):
        """Certain event has entropy 0."""
        p = [1.0, 0.0, 0.0]
        assert abs(entropy(p)) < 1e-9

    def test_normalization(self):
        """Automatically normalizes if not sum to 1."""
        p = [1, 1]  # sum = 2, should normalize to [0.5, 0.5]
        assert abs(entropy(p) - 1.0) < 1e-9

    def test_base_e(self):
        """Test natural log base."""
        p = [0.5, 0.5]
        expected = np.log(2)  # in nats
        assert abs(entropy(p, base=np.e) - expected) < 1e-9


class TestCrossEntropy:
    def test_perfect_prediction(self):
        """If p = q, cross-entropy = entropy."""
        p = [0.5, 0.5]
        assert abs(cross_entropy(p, p) - entropy(p)) < 1e-9

    def test_uniform(self):
        p = [0.5, 0.5]
        q = [0.5, 0.5]
        assert abs(cross_entropy(p, q) - 1.0) < 1e-9

    def test_mismatched(self):
        p = [0.8, 0.2]
        q = [0.5, 0.5]
        ce = cross_entropy(p, q)
        # H(p) + D(p||q)
        assert ce > entropy(p)


class TestKLDivergence:
    def test_identical(self):
        """KL divergence of identical distributions is 0."""
        p = [0.5, 0.5]
        assert abs(kl_divergence(p, p)) < 1e-9

    def test_different(self):
        """KL divergence of different distributions > 0."""
        p = [0.5, 0.5]
        q = [0.8, 0.2]
        kl = kl_divergence(p, q)
        assert kl > 0

    def test_normalization(self):
        """Automatically normalizes inputs."""
        p = [1, 1]
        q = [2, 2]
        assert abs(kl_divergence(p, q)) < 1e-9


class TestMutualInformation:
    def test_independent(self):
        """Independent variables have MI = 0."""
        # Joint of independent fair coins: P(X,Y) = P(X)P(Y)
        joint = [[0.25, 0.25], [0.25, 0.25]]
        assert abs(mutual_information(joint)) < 1e-9

    def test_perfect_correlation(self):
        """Perfect correlation has positive MI."""
        # If X=Y always
        joint = [[0.5, 0.0], [0.0, 0.5]]
        mi = mutual_information(joint)
        assert mi > 0

    def test_marginal_entropy(self):
        """MI = H(X) + H(Y) - H(X,Y)."""
        joint = [[0.5, 0.0], [0.0, 0.5]]
        p_x = [0.5, 0.5]
        p_y = [0.5, 0.5]
        expected = entropy(p_x) + entropy(p_y) - entropy([0.5, 0.0, 0.0, 0.5])
        mi = mutual_information(joint)
        assert abs(mi - expected) < 1e-9
