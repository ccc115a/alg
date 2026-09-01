"""
ito.py — 伊藤積分模組
======================
實作：
  - ItoIntegral  : 數值計算 ∫ f(t, W(t)) dW(t)
  - ito_lemma_demo : 驗證伊藤引理 df = f'dW + ½f''dt
"""

import numpy as np
from typing import Callable, Tuple, Optional


class ItoIntegral:
    """
    數值伊藤積分：∫₀ᵀ f(t, W(t)) dW(t)

    使用左端點 Riemann 求和（伊藤積分定義）：
      I = Σ f(tᵢ, W(tᵢ)) * ΔWᵢ

    參數
    ----
    integrand : Callable[[np.ndarray, np.ndarray], np.ndarray]
                被積函數 f(t, W)，接受陣列輸入
    seed      : int | None
    """

    def __init__(
        self,
        integrand: Callable[[np.ndarray, np.ndarray], np.ndarray],
        seed: Optional[int] = None,
    ):
        self.f = integrand
        self.rng = np.random.default_rng(seed)

    def compute(
        self,
        T: float = 1.0,
        n_steps: int = 10_000,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        計算伊藤積分。

        返回
        ----
        t          : shape (n_steps+1,)          時間格
        W_paths    : shape (n_paths, n_steps+1)  布朗路徑
        I_paths    : shape (n_paths, n_steps+1)  積分路徑（累積）
        """
        dt = T / n_steps
        t = np.linspace(0, T, n_steps + 1)

        dW = self.rng.normal(0.0, np.sqrt(dt), size=(n_paths, n_steps))
        W = np.concatenate(
            [np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1
        )

        # 左端點：f(tᵢ, W(tᵢ)) * ΔWᵢ
        f_vals = self.f(t[:-1], W[:, :-1])          # (n_paths, n_steps)
        increments = f_vals * dW                      # 伊藤積分增量

        I = np.concatenate(
            [np.zeros((n_paths, 1)), np.cumsum(increments, axis=1)], axis=1
        )
        return t, W, I

    def expected_value(
        self,
        T: float = 1.0,
        n_steps: int = 10_000,
        n_paths: int = 5_000,
    ) -> Tuple[float, float]:
        """
        用 Monte-Carlo 估計期望值與標準誤差。
        伊藤積分的期望值理論上為 0（鞅性質）。
        """
        _, _, I = self.compute(T, n_steps, n_paths)
        finals = I[:, -1]
        return float(finals.mean()), float(finals.std() / np.sqrt(n_paths))


# ---------------------------------------------------------------------------
# 經典範例：∫ W dW = ½W² - ½T  （伊藤引理驗證）
# ---------------------------------------------------------------------------

def ito_lemma_demo(
    T: float = 1.0,
    n_steps: int = 10_000,
    n_paths: int = 1,
    seed: Optional[int] = 42,
) -> dict:
    """
    驗證伊藤引理：
      f(W) = W²  →  df = 2W dW + dt
      ∫₀ᵀ W dW = ½W(T)² - ½T

    返回包含路徑與理論值的字典，方便繪圖比較。

    返回
    ----
    dict with keys:
      t           : 時間格
      W           : 布朗路徑
      ito_integral: ∫₀ᵀ W dW（伊藤積分數值）
      analytic    : ½W² - ½T（解析解）
      ito_correction : ½T（伊藤修正項）
      riemann     : 中點 Riemann 積分（對比用）
    """
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)

    dW = rng.normal(0.0, np.sqrt(dt), size=(n_paths, n_steps))
    W = np.concatenate(
        [np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1
    )

    # ── 伊藤積分（左端點）∫ W dW ─────────────────────────────────────────
    ito_inc = W[:, :-1] * dW
    ito_integral = np.concatenate(
        [np.zeros((n_paths, 1)), np.cumsum(ito_inc, axis=1)], axis=1
    )

    # ── 解析解：½W(t)² - ½t ─────────────────────────────────────────────
    analytic = 0.5 * W ** 2 - 0.5 * t[np.newaxis, :]

    # ── Stratonovich 積分（中點）對比 ─────────────────────────────────────
    W_mid = 0.5 * (W[:, :-1] + W[:, 1:])
    strat_inc = W_mid * dW
    strat_integral = np.concatenate(
        [np.zeros((n_paths, 1)), np.cumsum(strat_inc, axis=1)], axis=1
    )

    return {
        "t": t,
        "W": W,
        "ito_integral": ito_integral,
        "analytic": analytic,
        "ito_correction": 0.5 * t,
        "stratonovich": strat_integral,
        "dt": dt,
        "n_steps": n_steps,
        "T": T,
    }


# ---------------------------------------------------------------------------
# 二次變分驗證
# ---------------------------------------------------------------------------

def quadratic_variation_demo(
    T: float = 1.0,
    n_steps: int = 10_000,
    seed: int = 42,
) -> dict:
    """
    驗證 [W, W]_T = T（布朗運動二次變分）。
    同時對比一次變分（有界變差過程會 → 0，布朗運動 → ∞）。
    """
    rng = np.random.default_rng(seed)
    dt = T / n_steps
    t = np.linspace(0, T, n_steps + 1)
    dW = rng.normal(0.0, np.sqrt(dt), size=n_steps)
    W = np.concatenate([[0.0], np.cumsum(dW)])

    qv = np.concatenate([[0.0], np.cumsum(dW ** 2)])        # 二次變分
    fv = np.concatenate([[0.0], np.cumsum(np.abs(dW))])     # 一次變分（∞）
    return {"t": t, "W": W, "quadratic_variation": qv, "first_variation": fv}
