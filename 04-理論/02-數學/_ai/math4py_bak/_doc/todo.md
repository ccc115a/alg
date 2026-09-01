
* 請在 math4py/examples/statistics/clt.py 中，寫一個展示中央極限定理的程式，分別用 『丟銅板，擲骰子，均等分布，常態分布』， 1, 2, 10, 20 個樣本，展現中央極限定理的圖形。
* 目前的 geometry 預設都是 3d 的版本，但是 geometry 還有 2d,  nd 甚至是微分幾何 的可能，該如何處理呢？

方案 1：維度作為參數（推薦）
# 簡潔，多數情況夠用
Point(x=1, y=2)           # 2D
Point(x=1, y=2, z=3)      # 3D (預設)
Point([1, 2, 3, 4])       # ND
# 向量類似的設計
Vector([1, 0, 0])         # 3D (預設)
Vector([1, 0])            # 2D
Vector([1, 2, 3, 4])      # 4D