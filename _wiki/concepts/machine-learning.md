# 機器學習

讓電腦從資料中自動學習，而不是被人類逐一寫死規則。發展史宛如一齣戲：感知機 → AI 寒冬 → 反向傳播 → 深度學習。

## 核心特性

- **從資料學習**：以損失函數衡量預測誤差，再用梯度等訊號調整參數。
- **優化驅動**：本質是數值最佳化，SGD 是當代主力。
- **泛化 vs 擬合**：目標是在沒見過的資料上表現好，而非記住訓練集。
- **歷史週期**：技術突破與「AI 寒冬」反覆交替。

## 經典演算法

- [感知機](../algorithms/perceptron.md) — 頭版頭條到 AI 寒冬
- [CNN](../algorithms/cnn.md) — 視覺皮質啟發的卷積神經網路
- [MCTS](../algorithms/mcts.md) — AlphaGo 背後的強化學習
- [Hopfield](../algorithms/hopfield.md) — 物理學家的聯想記憶模型
- [SGD](../algorithms/sgd.md) — 從賭場到訓練 GPT

## 相關概念

- [數值方法](numerical-methods.md) — 訓練就是不斷做數值近似計算
- [隨機化](randomization.md) — SGD 與倒轉本身都倚賴隨機性