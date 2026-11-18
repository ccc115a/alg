# q4：用蒙地卡羅法算 n 變數積分（超體積）

**AI 聲明**：本程式與文件由 AI（opencode + GLM）協助產生，經人工檢視修改。

## 原理

n 維蒙地卡羅積分和 1 維一樣，只是把隨機點換成「超方體內的隨機向量」：

$$\int_{V} f(\mathbf{x})\,d\mathbf{x} \approx V \cdot \frac{1}{n}\sum_i f(\mathbf{x}_i)$$

其中 $V=\prod_i (b_i-a_i)$ 是超方體體積，$\mathbf{x}_i$ 是在 $[a_1,b_1]\times\cdots\times[a_n,b_n]$ 內均勻取樣的隨機點。

**最大優點**：誤差 $O(1/\sqrt{n})$ 與維度無關，所以 100 維也能算！

## 測試結果

```
2 維 ∫ (x₁²+x₂²) ≈ 0.6668 （正解 2/3）
5 維 ∫ (x₁²+...+x₅²) ≈ 1.6637 （正解 5/3）
```

## 執行

```bash
python3 q4_mc_n.py
```
