"""
process.py — 隨機過程核心模組
============================
實作：
  - BrownianMotion         標準布朗運動 (Wiener Process)
  - GeometricBrownianMotion 幾何布朗運動
  - OrnsteinUhlenbeck      O-U 均值回歸過程
  - BrownianBridge         布朗橋
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# 基底類別
# ---------------------------------------------------------------------------

class StochasticProcess:
    """所有隨機過程的基底類別。"""

    def simulate(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


# ---------------------------------------------------------------------------
# 1. 標準布朗運動 (Wiener Process)
# ---------------------------------------------------------------------------

class BrownianMotion(StochasticProcess):
    """
    標準布朗運動 W(t)，滿足：
      W(0) = 0
      W(t) - W(s) ~ N(0, t-s)  for t > s
      增量獨立

    參數
    ----
    mu    : float, 漂移項（預設 0，純擴散）
    sigma : float, 波動率（預設 1）
    seed  : int | None, 隨機種子
    """

    def __init__(self, mu: float = 0.0, sigma: float = 1.0,
                 seed: Optional[int] = None):
        self.mu = mu
        self.sigma = sigma
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        T: float = 1.0,
        n_steps: int = 1000,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        模擬布朗運動路徑。

        返回
        ----
        t       : shape (n_steps+1,)          時間格
        paths   : shape (n_paths, n_steps+1)  各路徑值
        """
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        # 標準常態增量
        dW = self.rng.normal(0.0, np.sqrt(dt), size=(n_paths, n_steps))
        # 加入漂移
        dX = self.mu * dt + self.sigma * dW

        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 1:] = np.cumsum(dX, axis=1)
        return t, paths

    def quadratic_variation(
        self, T: float = 1.0, n_steps: int = 1000, seed: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        計算二次變分 [W]_t = t（驗證布朗運動性質）。
        返回 (時間格, 累積二次變分)。
        """
        if seed is not None:
            rng = np.random.default_rng(seed)
        else:
            rng = self.rng
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)
        dW = rng.normal(0.0, np.sqrt(dt), size=n_steps)
        qv = np.concatenate([[0.0], np.cumsum(dW ** 2)])
        return t, qv

    def autocorrelation(self, s: float, t: float) -> float:
        """E[W(s)W(t)] = min(s, t)"""
        return self.sigma ** 2 * min(s, t)

    def __repr__(self):
        return f"<BrownianMotion mu={self.mu} sigma={self.sigma}>"


# ---------------------------------------------------------------------------
# 2. 幾何布朗運動 (GBM)
# ---------------------------------------------------------------------------

class GeometricBrownianMotion(StochasticProcess):
    """
    幾何布朗運動：
      dS = mu*S dt + sigma*S dW
      S(t) = S0 * exp((mu - sigma²/2)*t + sigma*W(t))

    參數
    ----
    S0    : float, 初始價格
    mu    : float, 漂移（年化）
    sigma : float, 波動率（年化）
    seed  : int | None
    """

    def __init__(self, S0: float = 100.0, mu: float = 0.05,
                 sigma: float = 0.2, seed: Optional[int] = None):
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        T: float = 1.0,
        n_steps: int = 252,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        精確模擬（利用解析解）。

        返回
        ----
        t     : shape (n_steps+1,)
        paths : shape (n_paths, n_steps+1)  股價路徑
        """
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        Z = self.rng.normal(0.0, 1.0, size=(n_paths, n_steps))
        drift = (self.mu - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * np.sqrt(dt) * Z

        log_increments = drift + diffusion
        log_paths = np.concatenate(
            [np.zeros((n_paths, 1)), np.cumsum(log_increments, axis=1)],
            axis=1,
        )
        paths = self.S0 * np.exp(log_paths)
        return t, paths

    def expected_value(self, t: float) -> float:
        """E[S(t)] = S0 * exp(mu * t)"""
        return self.S0 * np.exp(self.mu * t)

    def variance(self, t: float) -> float:
        """Var[S(t)] = S0² exp(2μt)(exp(σ²t) - 1)"""
        return (
            self.S0 ** 2
            * np.exp(2 * self.mu * t)
            * (np.exp(self.sigma ** 2 * t) - 1)
        )

    def __repr__(self):
        return (
            f"<GeometricBrownianMotion S0={self.S0} "
            f"mu={self.mu} sigma={self.sigma}>"
        )


# ---------------------------------------------------------------------------
# 3. Ornstein-Uhlenbeck（均值回歸）過程
# ---------------------------------------------------------------------------

class OrnsteinUhlenbeck(StochasticProcess):
    """
    O-U 過程（Vasicek 型）：
      dX = theta*(mu - X) dt + sigma dW

    參數
    ----
    mu    : float, 長期均值
    theta : float, 回歸速度
    sigma : float, 波動率
    X0    : float, 初始值
    seed  : int | None
    """

    def __init__(self, mu: float = 0.0, theta: float = 1.0,
                 sigma: float = 0.3, X0: float = 0.0,
                 seed: Optional[int] = None):
        self.mu = mu
        self.theta = theta
        self.sigma = sigma
        self.X0 = X0
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        T: float = 5.0,
        n_steps: int = 1000,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """精確模擬（條件分布為常態分佈）。"""
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        e = np.exp(-self.theta * dt)
        std = self.sigma * np.sqrt((1 - e ** 2) / (2 * self.theta))

        paths = np.zeros((n_paths, n_steps + 1))
        paths[:, 0] = self.X0
        Z = self.rng.normal(size=(n_paths, n_steps))

        for i in range(n_steps):
            paths[:, i + 1] = (
                self.mu * (1 - e) + e * paths[:, i] + std * Z[:, i]
            )
        return t, paths

    def stationary_mean(self) -> float:
        return self.mu

    def stationary_variance(self) -> float:
        return self.sigma ** 2 / (2 * self.theta)

    def __repr__(self):
        return (
            f"<OrnsteinUhlenbeck mu={self.mu} "
            f"theta={self.theta} sigma={self.sigma}>"
        )


# ---------------------------------------------------------------------------
# 4. 布朗橋 (Brownian Bridge)
# ---------------------------------------------------------------------------

class BrownianBridge(StochasticProcess):
    """
    布朗橋：在 [0,T] 上固定端點的布朗運動。
      B(0) = a, B(T) = b

    參數
    ----
    a, b : float, 起點 / 終點
    seed : int | None
    """

    def __init__(self, a: float = 0.0, b: float = 0.0,
                 seed: Optional[int] = None):
        self.a = a
        self.b = b
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        T: float = 1.0,
        n_steps: int = 1000,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """先模擬布朗運動再條件化。"""
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        dW = self.rng.normal(0.0, np.sqrt(dt), size=(n_paths, n_steps))
        W = np.concatenate(
            [np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1
        )
        # 條件化：B(t) = W(t) + (a - W(0))*(1 - t/T) + (b - W(T))*(t/T)
        ratio = t / T
        paths = (
            W
            + (self.a - W[:, [0]]) * (1 - ratio)
            + (self.b - W[:, [-1]]) * ratio
        )
        return t, paths

    def __repr__(self):
        return f"<BrownianBridge a={self.a} b={self.b}>"
