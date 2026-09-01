import numpy as np
import pytest
from math4py.stochastic.calculus import (
    BrownianMotion,
    GeometricBrownianMotion,
    OrnsteinUhlenbeck,
    BrownianBridge,
    BlackScholes,
    AmericanOption,
    ItoIntegral,
    ito_lemma_demo,
)


class TestBrownianMotion:
    def test_simulate_returns_correct_shapes(self):
        bm = BrownianMotion(seed=42)
        t, paths = bm.simulate(T=1.0, n_steps=100, n_paths=5)
        assert t.shape == (101,)
        assert paths.shape == (5, 101)

    def test_simulate_starts_at_zero(self):
        bm = BrownianMotion(seed=42)
        t, paths = bm.simulate(T=1.0, n_steps=100, n_paths=10)
        assert np.allclose(paths[:, 0], 0.0)

    def test_quadratic_variation_converges_to_T(self):
        bm = BrownianMotion(seed=42)
        t, qv = bm.quadratic_variation(T=1.0, n_steps=10_000)
        assert np.isclose(qv[-1], 1.0, atol=0.1)

    def test_autocorrelation(self):
        bm = BrownianMotion(sigma=1.0, seed=42)
        assert bm.autocorrelation(0.3, 0.7) == 0.3
        assert bm.autocorrelation(0.8, 0.2) == 0.2


class TestGeometricBrownianMotion:
    def test_simulate_returns_correct_shapes(self):
        gbm = GeometricBrownianMotion(S0=100.0, mu=0.05, sigma=0.2, seed=42)
        t, paths = gbm.simulate(T=1.0, n_steps=252, n_paths=10)
        assert t.shape == (253,)
        assert paths.shape == (10, 253)

    def test_positive_prices(self):
        gbm = GeometricBrownianMotion(S0=100.0, seed=42)
        t, paths = gbm.simulate()
        assert np.all(paths > 0)

    def test_expected_value(self):
        gbm = GeometricBrownianMotion(S0=100.0, mu=0.05, seed=42)
        expected = gbm.expected_value(1.0)
        assert np.isclose(expected, 100.0 * np.exp(0.05), rtol=1e-2)

    def test_initial_price(self):
        gbm = GeometricBrownianMotion(S0=100.0, seed=42)
        t, paths = gbm.simulate(n_paths=5)
        assert np.allclose(paths[:, 0], 100.0)


class TestOrnsteinUhlenbeck:
    def test_simulate_returns_correct_shapes(self):
        ou = OrnsteinUhlenbeck(mu=0.0, theta=1.0, sigma=0.3, seed=42)
        t, paths = ou.simulate(T=5.0, n_steps=1000, n_paths=10)
        assert t.shape == (1001,)
        assert paths.shape == (10, 1001)

    def test_stationary_mean(self):
        ou = OrnsteinUhlenbeck(mu=2.0, theta=1.0, sigma=0.5, seed=42)
        assert ou.stationary_mean() == 2.0

    def test_stationary_variance(self):
        ou = OrnsteinUhlenbeck(mu=0.0, theta=2.0, sigma=1.0, seed=42)
        expected_var = 1.0 ** 2 / (2 * 2.0)
        assert np.isclose(ou.stationary_variance(), expected_var)


class TestBrownianBridge:
    def test_simulate_returns_correct_shapes(self):
        bb = BrownianBridge(a=0.0, b=0.0, seed=42)
        t, paths = bb.simulate(T=1.0, n_steps=100, n_paths=5)
        assert t.shape == (101,)
        assert paths.shape == (5, 101)

    def test_endpoints(self):
        bb = BrownianBridge(a=0.0, b=0.0, seed=42)
        t, paths = bb.simulate(T=1.0, n_steps=1000, n_paths=100)
        assert np.allclose(paths[:, 0], 0.0, atol=0.01)
        assert np.allclose(paths[:, -1], 0.0, atol=0.01)


class TestBlackScholes:
    def test_call_price_positive(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        res = bs.price("call")
        assert res.price > 0

    def test_put_price_positive(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        res = bs.price("put")
        assert res.price > 0

    def test_in_the_money_call(self):
        bs = BlackScholes(S=110.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        res = bs.price("call")
        assert res.price > 10.0

    def test_put_call_parity(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        parity = bs.parity_check()
        assert parity["parity_error"] < 1e-8

    def test_monte_carlo_close_to_analytic(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        mc_call, se = bs.monte_carlo("call", n_paths=50_000, seed=42)
        analytic = bs.price("call").price
        assert abs(mc_call - analytic) < 3 * se

    def test_delta_call_in_range(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        res = bs.price("call")
        assert 0 < res.delta < 1

    def test_delta_put_in_range(self):
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        res = bs.price("put")
        assert -1 < res.delta < 0


class TestAmericanOption:
    def test_lsm_call_less_than_or_equal_to_s(self):
        am = AmericanOption(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        price, se = am.lsm("call", n_paths=10_000, n_steps=50, seed=42)
        assert price <= 100.0

    def test_binomial_tree_put(self):
        am = AmericanOption(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        price = am.binomial_tree("put", n_steps=200)
        assert price > 0

    def test_american_call_european_call_equal(self):
        am = AmericanOption(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        am_price = am.lsm("call", n_paths=20_000, n_steps=50, seed=42)[0]
        bs = BlackScholes(S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2)
        eu_price = bs.price("call").price
        assert abs(am_price - eu_price) < 2.0


class TestItoIntegral:
    def test_martingale_property(self):
        ito = ItoIntegral(integrand=lambda t, W: np.sin(W), seed=42)
        mean, se = ito.expected_value(T=1.0, n_steps=5000, n_paths=5000)
        assert abs(mean) < 3 * se

    def test_zero_integrand(self):
        ito = ItoIntegral(integrand=lambda t, W: np.zeros_like(t), seed=42)
        _, _, I = ito.compute(T=1.0, n_steps=1000)
        assert np.allclose(I, 0.0)

    def test_identity_integral(self):
        result = ito_lemma_demo(T=1.0, n_steps=50_000, n_paths=3, seed=42)
        W = result["W"]
        ito_int = result["ito_integral"]
        analytic = result["analytic"]
        for i in range(W.shape[0]):
            error = abs(ito_int[i, -1] - analytic[i, -1])
            assert error < 0.1


class TestIntegration:
    def test_imports_work(self):
        from math4py.stochastic.calculus import brownian_motion, ito_integral_plot, options_plot
        assert brownian_motion is not None
        assert ito_integral_plot is not None
        assert options_plot is not None