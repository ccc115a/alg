# 隨機化演算法

在演算法中引入隨機性來提升效率或打破最壞情況。分為 **Monte Carlo**（速度一定快，結果可能錯）與 **Las Vegas**（結果一定對，但速度可能慢）。

## 核心特性

- **Monte Carlo**：以機率犧牲正確性，換取保證的時間複雜度。
- **Las Vegas**：結果永遠正確，運氣好時更快，最壞情況機率極低。
- **機率分析**：用期望值或「失敗機率可調小」來分析。
- **打散最壞情況**：隨機化可避免敵意輸入引爆結構性最壞情況。

## 經典演算法

- [蒙地卡羅](../algorithms/monte-carlo.md) — 隨機抽樣逼近數值
- [Bloom Filter](../algorithms/bloom-filter.md) — 犧牲正確性換取空間
- [MCTS](../algorithms/mcts.md) — 隨機模擬引導搜尋
- [SGD](../algorithms/sgd.md) — 隨機取樣加速梯度下降

## 相關概念

- [資訊論](information-theory.md) — 隨機性與熵在理論上相互連結