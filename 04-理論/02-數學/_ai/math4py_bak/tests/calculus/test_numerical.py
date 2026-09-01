"""Tests for calculus/numeric.py - 數值微積分."""

import pytest
import numpy as np
from math4py.calculus import derivative, integral, trapezoidal, simpson


class TestDerivative:
    def test_derivative_x2_at_2(self):
        f = lambda x: x**2
        result = derivative(f, 2)
        assert abs(result - 4.0) < 1e-5

    def test_derivative_sin_at_0(self):
        f = np.sin
        result = derivative(f, 0)
        assert abs(result - 1.0) < 1e-5

    def test_derivative_exp_at_0(self):
        f = np.exp
        result = derivative(f, 0)
        assert abs(result - 1.0) < 1e-5


class TestIntegral:
    def test_integral_x2_0_to_1(self):
        f = lambda x: x**2
        result = integral(f, 0, 1)
        assert abs(result - 1/3) < 1e-3

    def test_integral_sin_0_to_pi(self):
        f = np.sin
        result = integral(f, 0, np.pi)
        assert abs(result - 2.0) < 1e-2

    def test_integral_exp_0_to_1(self):
        f = np.exp
        result = integral(f, 0, 1)
        expected = np.exp(1) - 1
        assert abs(result - expected) < 1e-2


class TestTrapezoidal:
    def test_trapezoidal_x2_0_to_1(self):
        f = lambda x: x**2
        result = trapezoidal(f, 0, 1)
        assert abs(result - 1/3) < 1e-3


class TestSimpson:
    def test_simpson_x2_0_to_1(self):
        f = lambda x: x**2
        result = simpson(f, 0, 1)
        assert abs(result - 1/3) < 1e-4

    def test_simpson_sin_0_to_pi(self):
        f = np.sin
        result = simpson(f, 0, np.pi, n=100)
        assert abs(result - 2.0) < 1e-3
