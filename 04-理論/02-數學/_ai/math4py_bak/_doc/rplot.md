# R 風格繪圖函數設計規劃

## 設計目標

提供 R 風格的繪圖函數，讓熟悉 R 的使用者能快速上手。
底層使用 matplotlib，但包裝成 R 風格的 API。

## 使用方式

```python
# 方式一：直接從 math4py.plot 匯入
from math4py.plot import plot, hist, boxplot, qqnorm

# 方式二：匯入為别名
import math4py.plot as plot

# 方式三：從 math4py 主套件匯入（若加入 __init__.py）
from math4py import plot, hist, boxplot
```

## 核心函數設計

### 1. 泛型繪圖 `plot()`

仿 R 的 `plot()` 泛型函數，根據輸入類型自動選擇圖形。

```python
def plot(x, y=None, type="p", main="", xlab="", ylab="", ...):
    """泛型繪圖函數（仿 R plot()）。

    Args:
        x: x 軸資料，或單一資料（此時 y 為 None）
        y: y 軸資料（可選）
        type: 圖形類型
            "p" = 散點圖（points）
            "l" = 折線圖（lines）
            "b" = 點線圖（both points and lines）
            "h" = 直方圖（histogram style）
        main: 標題（支援中文）
        xlab: x 軸標籤（支援中文）
        ylab: y 軸標籤（支援中文）
        ...: 其他傳給 matplotlib 的參數

    Examples:
        plot(x, y)                    # 散點圖
        plot(x, y, type="l")           # 折線圖
        plot(x)                        # 時間序列圖（索引 vs 值）
    """
```

### 2. 直方圖 `hist()`

仿 R 的 `hist()`。

```python
def hist(x, breaks=10, main="", xlab="", col="skyblue", ...):
    """直方圖（仿 R hist()）。

    Args:
        x: 資料
        breaks: 區間數或區間點
        main: 標題
        xlab: x 軸標籤
        col: 柱狀顏色

    Examples:
        hist(data, breaks=20, main="資料分佈", xlab="值")
    """
```

### 3. 盒鬚圖 `boxplot()`

仿 R 的 `boxplot()`。

```python
def boxplot(*data, names=None, main="", xlab="", ylab="", ...):
    """盒鬚圖（仿 R boxplot()）。

    Args:
        *data: 多組資料
        names: 每組資料的名稱
        main: 標題
        xlab: x 軸標籤
        ylab: y 軸標籤

    Examples:
        boxplot(group1, group2, names=["A", "B"], main="比較")
    """
```

### 4. Q-Q 圖 `qqnorm()`

仿 R 的 `qqnorm()`，用於檢驗常態性。

```python
def qqnorm(x, main="Q-Q Plot", xlab="Theoretical Quantiles", ylab="Sample Quantiles", ...):
    """Q-Q 圖（仿 R qqnorm()）。

    Args:
        x: 資料
        main: 標題
        xlab: x 軸標籤
        ylab: y 軸標籤

    Examples:
        qqnorm(data, main="常態性檢驗")
    """
```

### 5. 資訊論圖形

```python
def plot_entropy(p, base=2, main="Entropy", ...):
    """繪製熵長條圖。"""

def plot_kl_divergence(p, q, base=2, main="KL Divergence", ...):
    """視覺化 KL 散度。"""
```

## 參數命名規範（仿 R）

| R 參數 | math4py 參數 | 說明 |
|--------|----------------|------|
| `main` | `main` | 圖形標題 |
| `xlab` | `xlab` | x 軸標籤 |
| `ylab` | `ylab` | y 軸標籤 |
| `col` | `col` | 顏色 |
| `pch` | `marker` | 點的形狀 |
| `lty` | `linestyle` | 線的樣式 |
| `lwd` | `linewidth` | 線的寬度 |
| `breaks` | `breaks` | 直方圖區間數 |

## 中文支援

依賴 `plot/__init__.py` 已設定的中文字型：

- `_pick_cjk_fonts()` 自動選擇平台字型
- `matplotlib.rcParams["font.family"]` 已設定
- 使用者直接傳入中文標題/標籤即可正常顯示

```python
from math4py.plot import hist
hist(data, main="成績分佈", xlab="分數", col="orange")
```

## 實作計畫

1. 在 `statistics/plot.py` 或新建 `plot/rplot.py` 實作上述函數
2. 更新 `statistics/__init__.py` 匯出必要函數
3. 撰寫 `tests/statistics/test_rplot.py` 測試
4. 更新 `AGENTS.md` 記錄新增功能

## 與現有 `plot/` 模組的關係

- `plot/__init__.py` 已有 `StochPlot` 類別（用於隨機過程）
- 新建的 R 風格函數應放在 `statistics/plot.py` 或 `plot/rplot.py`
- 兩者共用 `_pick_cjk_fonts()` 和 `_style()` 設定
- 使用者可根據需求選擇：
  - `from math4py.plot import StochPlot` → 隨機過程圖
  - `from math4py.plot import plot, hist` → R 風格圖
