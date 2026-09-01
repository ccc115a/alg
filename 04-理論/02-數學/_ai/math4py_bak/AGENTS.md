# math4py

Python 數學函式庫，目標統一 Python 數學運算 (代數、幾何、微積分、機率統計、物理)

## 設計原則

- **不用重造輪子**: numpy/sympy/matplotlib 已有的功能直接使用，不重新定義
- **包裝優於重寫**: scipy 架構混亂，但可重新包裝成一致 API；難用的部分才重寫
- **R 風格統計**: statistics/ 模組採用 R 語法，與 R 相容
- **sympy 留給 sympy**: 符號運算請直接用 sympy，**本套件不做符號相關部分**
- **僅做數值計算**: calculus/ 等模組僅實作數值方法

## 模組

- `algebra/` - 代數 (Matrix 包裝 numpy, Group/Ring/Field 代數結構)
- `geometry/` - N維幾何 (`Point`, `Vector`) 與 2D/3D 特化 (`Line2D`, `Line3D`, `Plane3D`, `Transform2D`)
- `statistics/` - R 風格統計 + 資訊論 (entropy, cross_entropy, kl_divergence, mutual_information)
- `stochastic/` - 隨機過程與微積分 (Brownian motion, Black-Scholes, SDE)
- `calculus/` - 數值微積分 (derivative, integral, trapezoidal, simpson)
- `plot/` - R 風格繪圖 + 隨機過程視覺化
- `physics/` - 物理 (待建置)
- `tensor/` - 張量 (待建置)

## 專案結構

- `src/math4py/` - 主套件 (src layout)
- `tests/` - 測試目錄 (需符合 `test_*.py` 檔名)
- `examples/` - 範例腳本
- `out/` - 測試輸出圖檔目錄

## 開發指令

```bash
pip install -e ".[dev]"      # 必須先安裝才能跑測試
pytest                       # 執行所有測試
pytest tests/plot/            # 執行繪圖測試 (輸出到 out/)
ruff check .                 # Lint
ruff format .                # 排版
```

## 匯出

- 代數: `Matrix`, `Group`, `Ring`, `Field`, `VectorSpace`
- 幾何: `Point`, `Vector`, `Line2D`, `Line3D`, `Plane3D`, `Transform2D`
- 統計: `dnorm`, `pnorm`, `qnorm`, `rnorm`, `dt`, `pt`, `qt`, `rt`, `dchisq`, `pchisq`, `qchisq`, `rchisq`, `df`, `pf`, `qf`, `rf`, `dbinom`, `pbinom`, `qbinom`, `rbinom`, `dpois`, `ppois`, `qpois`, `rpois`, `mean`, `median`, `var`, `sd`, `cov`, `cor`, `quantile`, `summary`, `t_test`, `z_test`, `chisq_test`, `anova`, `conf_interval`, `entropy`, `cross_entropy`, `kl_divergence`, `mutual_information`
- 繪圖: `plot`, `hist`, `boxplot`, `qqnorm`, `plot_entropy`, `plot_kl`, `StochPlot`

## 重要細節

- **測試配置**: `pyproject.toml` 設定 `testpaths = ["tests"]`
- **繪圖輸出**: 測試時用 `filename="xxx.png"` 輸出到 `out/`；`filename=None` 顯示到螢幕
- **ruff 配置**: py38 target, double quotes, indent 4, line-length 100
- **統計匯出**: `import math4py as R` 可使用 R 風格函數
