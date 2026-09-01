"""Tests for calculus/theorem.py."""

import pytest
import math
from math4py.calculus.theorem import (
    fundamental_theorem,
    mean_value_theorem,
    rolle_theorem,
    intermediate_value_theorem,
    taylor_theorem,
    leibniz_rule,
    wallis_product,
)


class TestFundamentalTheorem:
    def test_fundamental_theorem(self):
        """微積分基本定理。

        若 F'(x) = f(x)，則 ∫[a,b] f(x)dx = F(b) - F(a)
        """
        result = fundamental_theorem()
        assert result["pass"] is True
        assert abs(result["exact"] - 2.0) < 1e-10


class TestMeanValueTheorem:
    def test_mean_value_theorem(self):
        """均值定理：存在 c 使得 f'(c) = (f(b) - f(a)) / (b - a)"""
        result = mean_value_theorem()
        assert result["pass"] is True
        assert result["error"] < 1e-5


class TestRolleTheorem:
    def test_rolle_theorem(self):
        """Rolle 定理：f(a)=f(b) 時存在 c 使得 f'(c)=0"""
        result = rolle_theorem()
        assert result["pass"] is True


class TestIntermediateValue:
    def test_intermediate_value_theorem(self):
        """中介值定理"""
        result = intermediate_value_theorem()
        assert result["pass"] is True


class TestTaylor:
    def test_taylor_theorem(self):
        """Taylor 級數"""
        result = taylor_theorem()
        assert result["pass"] is True


class TestSeries:
    def test_leibniz_rule(self):
        """Leibniz 級數收斂到 π/4"""
        result = leibniz_rule(1000)
        assert result["pass"] is True
        assert result["error"] < 1e-3

    def test_wallis_product(self):
        """Wallis 積收斂到 π/2"""
        result = wallis_product(1000)
        assert result["pass"] is True
        assert result["error"] < 1e-3