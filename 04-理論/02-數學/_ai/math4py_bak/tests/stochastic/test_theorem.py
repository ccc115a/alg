"""Tests for stochastic/theorem.py."""

import pytest
import math
from math4py.stochastic.theorem import (
    brownian_motion_properties,
    geometric_brownian_motion_properties,
    ito_integral_martingale,
    black_scholes_call_put_parity,
    black_scholes_greeks,
    ito_lemma_simple,
)


class TestBrownianMotion:
    def test_brownian_motion_properties(self):
        """布朗運動性質"""
        result = brownian_motion_properties()
        assert result["pass"] is True


class TestGeometricBrownianMotion:
    def test_geometric_brownian_motion_properties(self):
        """幾何布朗運動"""
        result = geometric_brownian_motion_properties()
        assert result["pass"] is True


class TestItoIntegral:
    def test_ito_integral_martingale(self):
        """伊藤積分是鞅"""
        result = ito_integral_martingale()
        assert result["pass"] is True


class TestBlackScholes:
    def test_call_put_parity(self):
        """Call-Put 平價"""
        result = black_scholes_call_put_parity()
        assert result["pass"] is True

    def test_greeks(self):
        """Greeks 性質"""
        result = black_scholes_greeks()
        assert result["pass"] is True


class TestItoLemma:
    def test_ito_lemma_simple(self):
        """伊藤引理"""
        result = ito_lemma_simple()
        assert result["pass"] is True