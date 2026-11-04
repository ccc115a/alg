# 習題 5（進階）：IC 繞線的「現代方法」與 SOTA

程式：`5_ic_routing_modern.py`（執行：`python3 5_ic_routing_modern.py`）

**動畫**：`python3 5_ic_routing_modern_plot.py` 演出 PathFinder 逐輪談判
（紅格＝超載、兩輪收斂）與 Q-learning 學好後貪心走出最短路，存成
[5_ic_routing_modern.gif](5_ic_routing_modern.gif)。

前一篇 `5_ic_routing.md` 已示範三種**單條 net** 的格子搜尋（Lee / Hadlock / A*）。
這一篇補上真實 EDA 工具會用到的**四種更高階的做法**，
並在文末整理目前學界／業界的 SOTA 全景。

## 方法 4：線搜尋（Line Search，Soukup / Mikami-Tabuchi 思想）

### 原理

Lee / Hadlock / A* 的狀態是「一格」，一格一格推進；
線搜尋把狀態升級成「**一段直線**」：

* DFS 的骨架不變，但選好方向後**一次直衝一整段**，
  直到撞牆、重複、或「繼續直走不再更靠近目標」為止。
* 方向排序用「走一步後離目標的曼哈頓距離」由小到大 → 有方向感。
* 轉彎次數少（晶片上過孔 via 很貴，越少越好）、開展極快。
* **不保證最短**——這是拿「最佳性」換「速度」的取捨。

### 執行結果

```text
--- 方法 4：線搜尋 (Line Search) —— net (0,0) -> (5,2) ---
  線長 = 7（BFS 最短 = 7），開展 8 格，嘗試 2 段直線：

*.........
*.........
*...#.....
*.........
*...#.....
***.#.....
..........
..........
```

## 方法 5：Steiner 樹拓撲（FLUTE 的核心思想）

### 原理

多 pin net 不是「兩兩點對點」互連，而是連成一棵**總長最短的樹**——
這是 Rectilinear Steiner Minimal Tree (RSMT) 問題，全程式繞線的第一步。

兩個關鍵知識：

1. **Hanan 定理**：最佳 RST 的 Steiner 點，必落在
   「pin 的 y 座標集合 × x 座標集合」構成的 **Hanan grid** 交點上
   → 搜尋空間從「整張圖」縮到「最多 n×n 個交點」。
2. 業界標準工具 **FLUTE**（Chu & Wong, TCAD 2008）用查找表 (lookup table)
   存已解好的小 net 最佳樹，大 net 再拆開合併——
   「前瞻查表 + 精確小規模解」，幾乎所有現代全域繞線器都以它當起點。

本程式在 3-pin 特例上：窮舉 Hanan 交點子集 → 對每個子集做 Manhattan-MST →
取總長最小者（3-pin 時這樣窮舉即可得精確最佳解）。

### 執行結果

```text
--- 方法 5：3-pin Steiner 樹（FLUTE 的思想） ---
  只用 MST 互連 3 個 pin：總長 = 18

P - - - S - - - P
. . . . | . . . .
. . . . | . . . .
. . . . | . . . .
. . . . | . . . .
. . . . | . . . .
. . . . P . . . .
. . . . . . . . .

  Steiner 樹總長 = 14；使用的 Steiner 點 = [(0, 4)]
  → 加進 Steiner 點後省了 4（22%）的總線長！
```

三個 pin `(0,0) (0,8) (6,4)`：無腦兩兩互連要 18 格；
在 `(0,4)` 放一個 Steiner 點後變成一棵 T 形樹，總長 14。
**省下的 22% 就是 Steiner 讓「點對點搜尋」蛻變成「拓撲搜尋」的價值。**

## 方法 6：可協商擠塞繞線（Negotiated Congestion Routing，PathFinder）

### 原理

多條 net 在同一張格子上競爭**有限的容量**（晶片上 = 每個 GCell 的 metal track 數）。
本程式的模型：

* 每格容量 2（＝上下兩層金屬各一條 track），牆內容量 0。
* **第 1 輪**：所有 net 都「不知道別人存在」，各自走自己的最短路 → 必然超載。
* **第 2 輪起**：逐條重繞，成本函數：

```text
cost(c) = 1 + p_fac × present(c) + history(c)
                      ↑                  ↑
        這一刻別人在這格的次數   這格「曾经超載」留下歷史紀錄
```

* 超過容量的格子每輪把歷史 +1（永久漲價），`p_fac` 逐輪加倍。
* 談判收斂：擠塞像市場機制一樣自己被「勸退」，直到超載 = 0。

這是 **PathFinder（Ebeling, FPGA 1995）**的原始思想，
至今仍是 FPGA 繞線的事實標準：VTR / OpenROAD 的 AIR router 都是它的後代；
ASIC 詳細繞線器的 rip-up & reroute 迴圈同樣是這套心法。

### 執行結果

```text
--- 方法 6：可協商擠塞繞線 (PathFinder) ---
  第 1 輪：超載格數 = 3  超載格子 = [(3, 3), (3, 4), (3, 5)]
  第 2 輪：超載格數 = 0  超載格子 = []
  迭代 2 輪後收斂（超載 = 0），最終佈局：

A 1 1 . # . 1 1 1 A
. . 1 . # . 1 . . .
B 2 * 2 # 2 * 2 2 B
3 3 * * * * * 3 3 3
C . 1 1 # 1 1 . . C
4 4 4 * * * 4 4 4 4
D . . . # . . . . D
. . . . # . . . . .
  （* = 兩條 net 共用的格子——擠塞被談判掉，不超過容量）
```

### 解讀

* 第 1 輪：A、B、C 三條 net 都想走最近的上方通道（第 3 列），超載 3 格。
* 第 2 輪：超載格漲價後，net B 被勸去走下方通道（第 5 列）→ 超載 0，收斂。
* `*` 表示「兩條 net 共用、但未超過容量 2」的格子。
* 「先硬繞、超載就漲價、漲價逼讓路」——整個晶片繞線問題就這樣被談判化解。

## 方法 7：強化學習繞線（RL 的最小示意）

### 原理

前面的方法每次繞線都要重新展開搜尋；RL 的思路是
**先花一次訓練成本學出「策略 (policy)」，之後每次繞線只是照著走**：

* 狀態：格子座標；動作：上下左右；
* 報酬：每走一步 −1（越短越好）、到目標結束；
* 估計值：`Q(s, a) = 從 s 往 a 方向走、之後一直貪心的預期總報酬`；
* Q-learning 更新：`Q[s,a] += α × (r + γ×max Q[s′,·] − Q[s,a])`；
* ε-greedy 探索（ε 逐集衰減），訓練 600 集完訓。

這正是 DeepPR (ISPD'23)、PRNet、NeuralSteiner (NeurIPS 2024)、
offline RL 調 cost 權重 (arXiv 2025) 等 SOTA RL 繞線研究的最小示意。

### 執行結果

```text
--- 方法 7：強化學習繞線 (Q-learning) —— net (7,0) -> (0,9) ---
  訓練 600 episodes（共 25866 次走步）後，貪心策略走出的路：

.........Q
.........Q
....#....Q
.........Q
....#....Q
....#....Q
.......QQQ
QQQQQQQQ..

  學到的路徑長 = 16 步；BFS 標準答案 = 16 步  （已達最短）
```

agent 沒有任何「BFS / A*」知識，只靠試錯就學出了最短路——
訓練完成後繞新 net **只需走 L 步**（不用再展開搜尋樹）。
RL 繞線 SOTA 論文追求的就是把這個思想擴到「多 net 一起排名、
擠塞預測、rip-up 決策」這些結構上。

---

## 現代繞線流程與目前 SOTA 全景

### 業界流程（兩階段）

```text
全域繞線 Global Routing      →  拓撲（Steiner 樹 / Hanan grid）+ 擠塞分配 + pattern routing
        ↓ 遞交 routing guide
詳細繞線 Detailed Routing    → 軌道級的精確路徑（A*/Dijkstra 變體 + rip-up & reroute + DRC 修復）
```

### 經典基石（仍被所有工具使用）

| 演算法 | 年代 | 去向 |
|--------|------|------|
| Lee 演算法（BFS 迷宮） | 1961 | 單 net 迷宮繞線的起點 |
| Hadlock / A* 變形 | 1970s | 迷宮繞線的速度最佳化 |
| Mikami-Tabuchi / Soukup 線搜尋 | 1968 / 1978 | 線搜尋、少轉彎 |
| Hanan 定理 + Steiner 樹 | 1965 | 全域繞線拓撲 |
| FLUTE | 2008 | 至今仍是業界 RSMT 事實標準 |
| PathFinder 協商擠塞 | 1995 | FPGA 繞線標準（VTR AIR）、ASIC RRR 核心 |
| FastRoute 1-4.1 | 2006-2018 | OpenROAD/FPGA 全域繞線 |
| Dr. CU / Dr. CU 2.0 | 2019-2022 | 學界最強開源 ASIC 詳細繞線器（sparse grid graph + guide-based） |
| TritonRoute(-WXL) | 2019-2023 | OpenROAD 的詳細繞線器 |

### 目前 SOTA 走向（2023-2026）

1. **計算最佳化加強**：Route-based ILP（把 rip-up & reroute 的 DRC 修復寫成整數規劃）
   —— CUHK 的 DRoute（TCAD 2026）在 ISPD18/19 上超越 Dr. CU 2.0 等既有最優。
2. **GPU / 大規模平行**：ISPD 2024 競賽主題就是 GPU 全域繞線；
   InstantGR、PAGR 以平行化把全域繞線推到大晶片級 runtime。
3. **深度強化學習**：
   * DeepPR（ISPD'23）：RL 決定 route planning 的「逐步方向決策」；
   * NeuralSteiner（NeurIPS 2024）：學 Steiner 樹生成、直接最小化 overflow；
   * T-RL net ordering（IJCAI 2025）：Transformer+RL 學「net 的繞線順序」；
   * Offline RL 調權重（arXiv 2025）：讓 RL 去調 A*/RRR 的 cost 權重。
4. **可微繞線**：DGR（DAC 2024）把繞線離散化為可微分的 route DAG，
   端到端 gradient descent 選 Steiner 樹與路徑。
5. **LLM 輔助調參**：AlphaRoute 將 LLM / SHAP 事後解釋拿來自適應調
   PathFinder 懲罰參數與 rip-up 策略。
6. **3D IC 繞線**：ISPD 2025-2026 主題之一；3D 異質整合讓繞線變成
   本質上跨層的 3D 搜尋。

一句話總結：**Lee/Hadlock/A* 這些「格子搜尋」的骨架一甲子未變，
真正的演化在「競爭與談判（NCR）、拓撲（Steiner/FLUTE）、
平行（GPU）、以及讓搜尋成本被「學」出來（RL）」。**

## 本程式的四種方法 vs 5_ic_routing.py 的三種

| # | 方法 | 狀態 / 成本概念 | 保證 | 對應真實工具 |
|---|------|----------------|------|--------------|
| 1 | Lee（BFS） | 一格，成本 1 | 最短 | 早期迷宮繞線 |
| 2 | Hadlock | 一格 + detour | 最短 | Lee 速度改良 |
| 3 | A* | 一格，f=g+h | 最短 | 迷宮繞線工業基礎 |
| 4 | 線搜尋 | **一段直線** | 否（快但近） | Soukup / Mikami-Tabuchi |
| 5 | Steiner 樹（FLUTE 思想） | **樹拓撲** | 3-pin 精確 | 全域繞線 FLUTE |
| 6 | PathFinder 協商擠塞 | 多 net + history/present 成本 | 收斂到合法解 | FPGA/ASIC RRR |
| 7 | Q-learning 繞線 | **學出 policy** | 收斂到最短（本例） | DeepPR / PRNet 思想 |
