
Python 的數學套件很混亂， math4py 企圖成為 Python 數值世界的大統一數學套件。

(不包含符號世界，符號世界留給 sympy， 符號功能本套件不支援)

1. numpy/matplotlib 裡面有的，本套件就不創建，直接使用 numpy/matplotlib
    * 這些套件不足的部分，math4py 要去補充，例如 plot 套件，要能支援中文字型（跨平台設定）
2. numpy/matplotlib 沒有的數學函數，收錄到本套件中，盡量包裝得好用，有一致性
    * scipy 我覺得做得不好，非常混亂，我們重新用 R 的角度來建構
3. 核心數學區分為代數 algebra/ ，幾何 geometry/ 微積分 calculus/ 機率統計 statistic/ 
    * 線性代數放在 algebra/matrix.py 中(要包含矩陣，特徵值， SVD 分解等等)
    * 張量已經由 numpy 處理了，不夠的地方，請補在 algebra/tensor.py 下
4. statistics/ 採用 R 的函式庫語法設計，盡量和 R 相容一致
5. 代數，幾何，微積分，機率統計，矩陣，線性代數，數學規劃，微分方程，傅立葉級數與轉換，隨機微積分，複變函數，向量微積分，泛函分析，微分幾何（可作為相對論基礎），拓樸學等等，都要納入到一個統一的框架當中，有一致性的物件和函數設計。
    * 這些在 numpy/matplotlib 中有處理的，可以適當在 math4py 中包裝後，讓他更好用。

## 相關計劃

* lean4py: 另一個計劃，用來做數學證明，盡量和 lean4 mathlib 一致
* physics4py: 另一個計劃，物理套件，用來包含『傳統力學，光學，電磁學，量子力學，相對論』
* sym4py: 將 sympy 包裝得更好用。（這個可能不會做，似乎沒價值）
