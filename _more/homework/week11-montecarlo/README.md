# Week11：數值積分與蒙地卡羅法作業

**AI 聲明**：本目錄下所有程式（.py）與文件（.md）均由 AI（opencode + GLM）協助產生，經人工檢視與測試修改。每個檔案內也都有標注 AI 使用聲明。

## 作業清單

| # | 習題 | 程式 | 文件 |
|---|---|---|---|
| 1 | 單變數數值微分與積分（中央差分、中點法、辛普森） | [q1_diff_int_1d.py](q1_diff_int_1d.py) | [q1_diff_int_1d.md](q1_diff_int_1d.md) |
| 2 | 蒙地卡羅法算單變數積分 | [q2_mc_1d.py](q2_mc_1d.py) | [q2_mc_1d.md](q2_mc_1d.md) |
| 3 | n 變數數值微分（梯度）與積分（超體積） | [q3_grad_integral_n.py](q3_grad_integral_n.py) | [q3_grad_integral_n.md](q3_grad_integral_n.md) |
| 4 | 蒙地卡羅法算 n 變數積分 | [q4_mc_n.py](q4_mc_n.py) | [q4_mc_n.md](q4_mc_n.md) |
| 5 | 黎曼積分法 `integral(f, low, high)`，n 維任意（1/2/5/100 維） | [q5_riemann_n.py](q5_riemann_n.py) | [q5_riemann_n.md](q5_riemann_n.md) |
| 6 | 蒙地卡羅法 `integral_mc(f, low, high)`，題目同 q5 | [q6_mc_generic.py](q6_mc_generic.py) | [q6_mc_generic.md](q6_mc_generic.md) |

## 共同範例

q5、q6 使用同一題目：$f(x)=x_1^2+\dots+x_n^2$，積分範圍 $[0,1]^n$（low=0, high=1），正解為 $n/3$，分別以 1、2、5、100 維測試。

## 重點觀察

- 低維度時黎曼和（中點法、辛普森法）收斂快且準。
- 高維度時黎曼和遭遇「維度災難」：格子數 $k^n$ 爆炸，q5 在 100 維被迫退化成隨機取樣。
- 蒙地卡羅誤差 $O(1/\sqrt{N})$ 與維度無關，是高維積分的標準做法。

## 執行方式

每個程式都是獨立教學腳本，內含測試（assert）：

```bash
python3 q1_diff_int_1d.py
python3 q2_mc_1d.py
python3 q3_grad_integral_n.py
python3 q4_mc_n.py
python3 q5_riemann_n.py
python3 q6_mc_generic.py
```
