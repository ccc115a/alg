"""
sde.py — 隨機微分方程數值求解器
=================================
方法：
  - Euler-Maruyama  (強收斂階 0.5)
  - Milstein        (強收斂階 1.0)
  - Runge-Kutta (隨機 RK4)  (弱收斂階 2.0)

SDE 形式：  dX = a(t,X) dt + b(t,X) dW
"""

import numpy as np
from typing import Callable, Tuple, Optional


Drift = Callable[[float, np.ndarray], np.ndarray]
Diffusion = Callable[[float, np.ndarray], np.ndarray]


class SDESolver:
    """
    數值求解一般 SDE：
      dX = a(t, X) dt + b(t, X) dW

    參數
    ----
    drift     : a(t, X)，漂移係數
    diffusion : b(t, X)，擴散係數
    X0        : float | np.ndarray，初始條件
    seed      : int | None
    """

    def __init__(
        self,
        drift: Drift,
        diffusion: Diffusion,
        X0: float = 1.0,
        seed: Optional[int] = None,
    ):
        self.a = drift
        self.b = diffusion
        self.X0 = np.atleast_1d(np.asarray(X0, dtype=float))
        self.rng = np.random.default_rng(seed)

    # ── Euler-Maruyama ─────────────────────────────────────────────────────

    def euler_maruyama(
        self,
        T: float = 1.0,
        n_steps: int = 1000,
        n_paths: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Euler-Maruyama 格式（強收斂階 1/2）：
          X_{n+1} = X_n + a(t_n, X_n)Δt + b(t_n, X_n)ΔW_n

        返回 (t, paths)
          t     : (n_steps+1,)
          paths : (n_paths, n_steps+1, dim)  若 dim=1 則壓縮為 (n_paths, n_steps+1)
        """
        dt = T / n_steps
        sqrt_dt = np.sqrt(dt)
        t = np.linspace(0, T, n_steps + 1)
        dim = len(self.X0)

        paths = np.zeros((n_paths, n_steps + 1, dim))
        paths[:, 0, :] = self.X0

        for i in range(n_steps):
            X = paths[:, i, :]           # (n_paths, dim)
            dW = self.rng.normal(0.0, sqrt_dt, size=(n_paths, dim))
            paths[:, i + 1, :] = (
                X
                + self.a(t[i], X) * dt
                + self.b(t[i], X) * dW
            )

        if dim == 1:
            return t, paths[:, :, 0]
        return t, paths

    # ── Milstein ──────────────────────────────────────────────────────────

    def milstein(
        self,
        T: float = 1.0,
        n_steps: int = 1000,
        n_paths: int = 1,
        b_prime: Optional[Callable] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Milstein 格式（強收斂階 1）：
          X_{n+1} = X_n + a·Δt + b·ΔW + ½b·b'·((ΔW)²-Δt)

        若 b_prime 為 None 則用有限差分近似 b'。
        """
        dt = T / n_steps
        sqrt_dt = np.sqrt(dt)
        t = np.linspace(0, T, n_steps + 1)
        dim = len(self.X0)

        eps = 1e-6  # 有限差分步長

        paths = np.zeros((n_paths, n_steps + 1, dim))
        paths[:, 0, :] = self.X0

        for i in range(n_steps):
            X = paths[:, i, :]
            dW = self.rng.normal(0.0, sqrt_dt, size=(n_paths, dim))
            b_val = self.b(t[i], X)

            if b_prime is not None:
                bp = b_prime(t[i], X)
            else:
                bp = (self.b(t[i], X + eps) - b_val) / eps  # 有限差分

            milstein_term = 0.5 * b_val * bp * (dW ** 2 - dt)
            paths[:, i + 1, :] = (
                X
                + self.a(t[i], X) * dt
                + b_val * dW
                + milstein_term
            )

        if dim == 1:
            return t, paths[:, :, 0]
        return t, paths

    # ── 強收斂誤差比較 ──────────────────────────────────────────────────────

    def convergence_study(
        self,
        T: float = 1.0,
        steps_list=None,
        n_paths: int = 2000,
        reference_steps: int = 65536,
        method: str = "euler",
    ) -> dict:
        """
        計算各 n_steps 下的強收斂誤差 E|X_T - X_T^ref|。

        返回 dict with keys: steps, errors, slopes
        """
        if steps_list is None:
            steps_list = [8, 16, 32, 64, 128, 256, 512]

        # 先用精細格當參考解（同一 dW 做粗格）
        dt_ref = T / reference_steps
        sqrt_dt_ref = np.sqrt(dt_ref)
        t_ref = np.linspace(0, T, reference_steps + 1)
        dim = len(self.X0)

        # 生成精細 dW
        dW_fine = self.rng.normal(
            0.0, sqrt_dt_ref, size=(n_paths, reference_steps, dim)
        )

        errors = []
        for n in steps_list:
            ratio = reference_steps // n
            # 累積粗格 dW
            dW_coarse = dW_fine.reshape(n_paths, n, ratio, dim).sum(axis=2)
            dt_c = T / n
            X = np.tile(self.X0, (n_paths, 1)).astype(float)
            t_c = np.linspace(0, T, n + 1)
            for i in range(n):
                dW_i = dW_coarse[:, i, :]
                a_i = self.a(t_c[i], X)
                b_i = self.b(t_c[i], X)
                if method == "milstein":
                    eps = 1e-6
                    bp = (self.b(t_c[i], X + eps) - b_i) / eps
                    X = X + a_i * dt_c + b_i * dW_i + 0.5 * b_i * bp * (dW_i ** 2 - dt_c)
                else:
                    X = X + a_i * dt_c + b_i * dW_i
            # 參考解
            X_ref = np.tile(self.X0, (n_paths, 1)).astype(float)
            for i in range(reference_steps):
                X_ref = X_ref + self.a(t_ref[i], X_ref) * dt_ref + self.b(t_ref[i], X_ref) * dW_fine[:, i, :]
            err = float(np.mean(np.abs(X[:, 0] - X_ref[:, 0])))
            errors.append(err)

        steps_arr = np.array(steps_list, dtype=float)
        dts = T / steps_arr
        # 用 log-log 擬合估計收斂階
        slope = float(np.polyfit(np.log(dts), np.log(errors), 1)[0])
        return {"steps": steps_list, "dts": dts.tolist(),
                "errors": errors, "slope": slope}
