"""
options.py — 期權定價模組
==========================
實作：
  - BlackScholes   : 歐式期權（英國期權）解析定價 + Greeks
  - AmericanOption : 美式期權（最優停止）— Longstaff-Schwartz LSM + 二項樹
"""

import numpy as np
from scipy import stats
from typing import Literal, Optional, Tuple
from dataclasses import dataclass


OptionType = Literal["call", "put"]


# ---------------------------------------------------------------------------
# 1. Black-Scholes 歐式期權（英國期權）
# ---------------------------------------------------------------------------

@dataclass
class BSResult:
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    d1: float
    d2: float


class BlackScholes:
    """
    Black-Scholes 歐式期權定價（英國期權 European Option）。

    模型假設：
      dS = r*S dt + sigma*S dW  （風險中立測度）

    參數
    ----
    S     : float, 現貨價格
    K     : float, 履約價
    T     : float, 到期時間（年）
    r     : float, 無風險利率
    sigma : float, 波動率
    q     : float, 連續股利率（預設 0）
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0,
    ):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.q = q

    def _d1_d2(self) -> Tuple[float, float]:
        d1 = (
            np.log(self.S / self.K)
            + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T
        ) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        return d1, d2

    def price(self, option_type: OptionType = "call") -> BSResult:
        """
        解析定價。
        Call  : S·e^{-qT}·N(d1) - K·e^{-rT}·N(d2)
        Put   : K·e^{-rT}·N(-d2) - S·e^{-qT}·N(-d1)
        """
        d1, d2 = self._d1_d2()
        Nd1 = stats.norm.cdf(d1)
        Nd2 = stats.norm.cdf(d2)
        nd1 = stats.norm.pdf(d1)
        sqrt_T = np.sqrt(self.T)

        if option_type == "call":
            price = (
                self.S * np.exp(-self.q * self.T) * Nd1
                - self.K * np.exp(-self.r * self.T) * Nd2
            )
            delta = np.exp(-self.q * self.T) * Nd1
            rho   = self.K * self.T * np.exp(-self.r * self.T) * Nd2 / 100
        else:  # put
            price = (
                self.K * np.exp(-self.r * self.T) * stats.norm.cdf(-d2)
                - self.S * np.exp(-self.q * self.T) * stats.norm.cdf(-d1)
            )
            delta = np.exp(-self.q * self.T) * (Nd1 - 1)
            rho   = -self.K * self.T * np.exp(-self.r * self.T) * stats.norm.cdf(-d2) / 100

        gamma = (
            np.exp(-self.q * self.T)
            * nd1
            / (self.S * self.sigma * sqrt_T)
        )
        theta = (
            -np.exp(-self.q * self.T) * self.S * nd1 * self.sigma
            / (2 * sqrt_T)
            - self.r * self.K * np.exp(-self.r * self.T) * (Nd2 if option_type == "call" else stats.norm.cdf(-d2))
            + self.q * self.S * np.exp(-self.q * self.T) * (Nd1 if option_type == "call" else stats.norm.cdf(-d1))
        ) / 365   # 日為單位
        vega = self.S * np.exp(-self.q * self.T) * nd1 * sqrt_T / 100

        return BSResult(
            price=float(price),
            delta=float(delta),
            gamma=float(gamma),
            theta=float(theta),
            vega=float(vega),
            rho=float(rho),
            d1=float(d1),
            d2=float(d2),
        )

    def implied_volatility(
        self,
        market_price: float,
        option_type: OptionType = "call",
        tol: float = 1e-6,
        max_iter: int = 200,
    ) -> float:
        """Newton-Raphson 求隱含波動率。"""
        sigma = 0.2  # 初始猜測
        for _ in range(max_iter):
            bs = BlackScholes(self.S, self.K, self.T, self.r, sigma, self.q)
            res = bs.price(option_type)
            diff = res.price - market_price
            if abs(diff) < tol:
                return sigma
            sigma -= diff / (res.vega * 100)   # vega 單位修正
            sigma = max(sigma, 1e-8)
        return sigma

    def monte_carlo(
        self,
        option_type: OptionType = "call",
        n_paths: int = 100_000,
        n_steps: int = 252,
        seed: Optional[int] = 42,
        antithetic: bool = True,
    ) -> Tuple[float, float]:
        """
        風險中立 Monte-Carlo 定價，回傳 (價格, 標準誤)。
        使用對偶變數法（antithetic variates）降低變異數。
        """
        rng = np.random.default_rng(seed)
        dt = self.T / n_steps
        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * dt
        vol = self.sigma * np.sqrt(dt)

        half = n_paths // 2 if antithetic else n_paths
        Z = rng.standard_normal((half, n_steps))
        if antithetic:
            Z = np.concatenate([Z, -Z], axis=0)

        log_S = np.log(self.S) + np.sum(drift + vol * Z, axis=1)
        S_T = np.exp(log_S)

        if option_type == "call":
            payoffs = np.maximum(S_T - self.K, 0)
        else:
            payoffs = np.maximum(self.K - S_T, 0)

        discounted = np.exp(-self.r * self.T) * payoffs
        price = float(discounted.mean())
        se = float(discounted.std() / np.sqrt(n_paths))
        return price, se

    def parity_check(self) -> dict:
        """驗證 Put-Call Parity：C - P = S·e^{-qT} - K·e^{-rT}"""
        call = self.price("call").price
        put  = self.price("put").price
        lhs  = call - put
        rhs  = self.S * np.exp(-self.q * self.T) - self.K * np.exp(-self.r * self.T)
        return {"call": call, "put": put, "C-P": lhs, "S·e⁻ᵠᵀ-K·e⁻ʳᵀ": rhs,
                "parity_error": abs(lhs - rhs)}

    def simulate_paths(
        self,
        n_paths: int = 10,
        n_steps: int = 252,
        seed: Optional[int] = 42,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """產生 GBM 路徑用於視覺化。"""
        from .process import GeometricBrownianMotion
        gbm = GeometricBrownianMotion(self.S, self.r - self.q, self.sigma, seed)
        return gbm.simulate(self.T, n_steps, n_paths)


# ---------------------------------------------------------------------------
# 2. 美式期權 (American Option)
# ---------------------------------------------------------------------------

class AmericanOption:
    """
    美式期權定價，支援：
      (a) Longstaff-Schwartz LSM（回歸 Monte-Carlo）
      (b) Cox-Ross-Rubinstein（CRR）二項樹

    美式 vs 歐式差異：
      - 美式可在到期日前任何時間執行（最優停止問題）
      - 美式 put 的提前執行溢價 = American Price - European Price

    參數
    ----
    S, K, T, r, sigma, q : 同 BlackScholes
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0,
    ):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.q = q

    # ── (a) Longstaff-Schwartz LSM ─────────────────────────────────────────

    def lsm(
        self,
        option_type: OptionType = "put",
        n_paths: int = 50_000,
        n_steps: int = 50,
        poly_degree: int = 3,
        seed: Optional[int] = 42,
        antithetic: bool = True,
    ) -> Tuple[float, float]:
        """
        Longstaff-Schwartz 回歸 Monte-Carlo（LSM）演算法。

        核心思想：
          - 在每個時間步，對價內期權做最小二乘回歸
          - 比較 "立即執行" vs "繼續持有（回歸估計期望）"
          - 向後歸納（backward induction）

        返回 (美式期權價格, 標準誤)
        """
        rng = np.random.default_rng(seed)
        dt = self.T / n_steps
        discount = np.exp(-self.r * dt)

        # ── 生成路徑 ──────────────────────────────────────────────────────
        half = n_paths // 2 if antithetic else n_paths
        Z = rng.standard_normal((half, n_steps))
        if antithetic:
            Z = np.vstack([Z, -Z])

        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * dt
        vol   = self.sigma * np.sqrt(dt)

        log_S = np.log(self.S) + np.cumsum(drift + vol * Z, axis=1)
        S_paths = np.concatenate(
            [np.full((n_paths, 1), self.S), np.exp(log_S)], axis=1
        )  # shape: (n_paths, n_steps+1)

        # ── 到期日收益 ────────────────────────────────────────────────────
        if option_type == "call":
            payoff = lambda S: np.maximum(S - self.K, 0.0)
        else:
            payoff = lambda S: np.maximum(self.K - S, 0.0)

        cash_flows = payoff(S_paths[:, -1]).copy()   # 到期日現金流

        # ── 向後歸納 ──────────────────────────────────────────────────────
        for step in range(n_steps - 1, 0, -1):
            S_now = S_paths[:, step]
            immediate = payoff(S_now)
            itm = immediate > 0           # 只對價內路徑回歸

            if itm.sum() < poly_degree + 1:
                cash_flows *= discount
                continue

            # 折現未來現金流
            future_pv = cash_flows[itm] * discount

            # 多項式基函數回歸（Laguerre-like）
            X = S_now[itm]
            basis = np.column_stack(
                [X ** k for k in range(poly_degree + 1)]
            )
            coef, *_ = np.linalg.lstsq(basis, future_pv, rcond=None)
            continuation = basis @ coef

            # 提前執行判斷
            exercise = immediate[itm] > continuation
            exercise_idx = np.where(itm)[0][exercise]

            cash_flows *= discount
            cash_flows[exercise_idx] = immediate[itm][exercise] / discount * discount

        cash_flows *= discount  # 折現到 t=0

        price = float(cash_flows.mean())
        se    = float(cash_flows.std() / np.sqrt(n_paths))
        return price, se

    # ── (b) CRR 二項樹 ──────────────────────────────────────────────────────

    def binomial_tree(
        self,
        option_type: OptionType = "put",
        n_steps: int = 500,
    ) -> float:
        """
        Cox-Ross-Rubinstein 二項樹（美式期權）。

        參數：
          u = exp(sigma * sqrt(dt))
          d = 1/u
          p = (exp((r-q)*dt) - d) / (u - d)   風險中立機率
        """
        dt = self.T / n_steps
        u = np.exp(self.sigma * np.sqrt(dt))
        d = 1.0 / u
        p = (np.exp((self.r - self.q) * dt) - d) / (u - d)
        disc = np.exp(-self.r * dt)

        # 到期日資產價格
        j = np.arange(n_steps + 1)
        S_T = self.S * (u ** (n_steps - j)) * (d ** j)

        if option_type == "call":
            V = np.maximum(S_T - self.K, 0.0)
        else:
            V = np.maximum(self.K - S_T, 0.0)

        # 向後遞推
        for step in range(n_steps - 1, -1, -1):
            S = self.S * (u ** (step - np.arange(step + 1))) * (d ** np.arange(step + 1))
            V = disc * (p * V[:-1] + (1 - p) * V[1:])
            if option_type == "call":
                intrinsic = np.maximum(S - self.K, 0.0)
            else:
                intrinsic = np.maximum(self.K - S, 0.0)
            V = np.maximum(V, intrinsic)

        return float(V[0])

    # ── 提前執行溢價 ─────────────────────────────────────────────────────────

    def early_exercise_premium(
        self,
        option_type: OptionType = "put",
        n_paths: int = 50_000,
        n_steps: int = 50,
        seed: int = 42,
    ) -> dict:
        """
        計算：
          美式價格（LSM）
          歐式價格（BS 解析）
          提前執行溢價 = 美式 - 歐式
        """
        american_price, american_se = self.lsm(
            option_type, n_paths, n_steps, seed=seed
        )
        bs = BlackScholes(self.S, self.K, self.T, self.r, self.sigma, self.q)
        european_price = bs.price(option_type).price
        premium = american_price - european_price
        binomial_price = self.binomial_tree(option_type)

        return {
            "american_lsm":     american_price,
            "american_se":      american_se,
            "american_binomial": binomial_price,
            "european_bs":      european_price,
            "early_exercise_premium": premium,
            "option_type":      option_type,
        }

    def optimal_exercise_boundary(
        self,
        option_type: OptionType = "put",
        n_steps: int = 100,
        n_paths: int = 20_000,
        seed: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        估計最優執行邊界 S*(t)：
        對每個時間步，找出使 "立即執行 = 繼續持有" 的臨界股價。
        """
        rng = np.random.default_rng(seed)
        dt = self.T / n_steps
        t = np.linspace(0, self.T, n_steps + 1)

        Z = rng.standard_normal((n_paths, n_steps))
        drift = (self.r - self.q - 0.5 * self.sigma ** 2) * dt
        vol   = self.sigma * np.sqrt(dt)
        log_S = np.log(self.S) + np.cumsum(drift + vol * Z, axis=1)
        S_paths = np.concatenate(
            [np.full((n_paths, 1), self.S), np.exp(log_S)], axis=1
        )

        if option_type == "call":
            payoff = lambda S: np.maximum(S - self.K, 0.0)
        else:
            payoff = lambda S: np.maximum(self.K - S, 0.0)

        cash_flows = payoff(S_paths[:, -1]).copy()
        boundary = [np.nan] * (n_steps + 1)

        for step in range(n_steps - 1, 0, -1):
            S_now = S_paths[:, step]
            immediate = payoff(S_now)
            itm = immediate > 0
            cash_flows *= np.exp(-self.r * dt)

            if itm.sum() > 5:
                X = S_now[itm]
                basis = np.column_stack([X ** k for k in range(4)])
                future_pv = cash_flows[itm]
                try:
                    coef, *_ = np.linalg.lstsq(basis, future_pv, rcond=None)
                    cont = basis @ coef
                    exercise = immediate[itm] > cont
                    if exercise.sum() > 0 and (~exercise).sum() > 0:
                        # 邊界 ≈ 執行與不執行路徑的股價分界
                        ex_S = X[exercise]
                        no_S = X[~exercise]
                        if option_type == "put":
                            boundary[step] = float(max(ex_S.max(), no_S.min()))
                        else:
                            boundary[step] = float(min(ex_S.min(), no_S.max()))
                except Exception:
                    pass

            exercise_idx = np.where(itm)[0]
            cash_flows[exercise_idx] = np.maximum(
                immediate[itm], cash_flows[exercise_idx]
            )

        return t, np.array(boundary)
