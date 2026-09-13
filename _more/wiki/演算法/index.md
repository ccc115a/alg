# 演算法

演算法研究解決問題的計算方法與效率分析。

## 概念

- [演算法的歷史](演算法的歷史.md) - 從歐幾里得到量子計算 | tags: 計算理論, 發展
- [時間複雜度](時間複雜度.md) - 演算法執行時間分析 | tags: Big-O, Omega, Theta
- [空間複雜度](空間複雜度.md) - 演算法記憶體需求分析 | tags: Big-O
- [資料結構](資料結構.md) - 資料組織與存取方式 | tags: 陣列, 樹, 圖

## 主題

- [字串演算法](字串演算法.md) - 高效文本處理技術 | tags: KMP, Boyer-Moore, 字典樹
- [網路流](網路流.md) - 圖論中的流量優化 | tags: 最大流, 最小割, Ford-Fulkerson
- [計算幾何](計算幾何.md) - 幾何問題的演算法 | tags: 凸包, 旋轉卡尺, 最近點對
- [近似演算法](近似演算法.md) - NP-困難問題的近似解 | tags: 近似比, 貪心, FPTAS
- [隨機演算法](隨機演算法.md) - 概率驅動的演算法 | tags: 拉斯維加斯, 蒙特卡羅, Karger
- [線性規劃](線性規劃.md) - 線性約束下的優化 | tags: 單形法, 對偶理論, 整數規劃
- [排序演算法](排序演算法.md) - 元素排序方法 | tags: QuickSort, MergeSort
- [搜尋法](搜尋法.md) - 元素查找技術 | tags: BinarySearch, Hash
- [圖形演算法](圖形演算法.md) - 圖結構處理方法 | tags: BFS, DFS, Dijkstra
- [動態規劃法](動態規劃法.md) - 最優子結構問題求解 | tags: DP, Memoization
- [貪婪法](貪婪法.md) - 區域最优解策略 | tags: Greedy
- [分割擊破法](分割擊破法.md) - 分治問題解決範式 | tags: Divide-Conquer
- [列舉法](列舉法.md) - 暴力搜尋與組合問題求解 | tags: Brute-Force, Backtracking

## 工具

- [Python](Python.md) - 通用程式語言 | tags: 資料科學, 腳本

## 歷史故事

### 排序與搜尋

- [二元搜尋的 60 年 Bug](binary-search-bug.md) - 全世界頂尖工程師被一個加號卡關
- [快速排序](quick-sort.md) - 莫斯科留學時為翻譯字典而發明
- [Fisher-Yates 洗牌](fisher-yates.md) - 保證絕對公平的洗牌法
- [基數排序](radix-sort.md) - 美國人口普查催生的非比較排序

### 圖論與最短路徑

- [Dijkstra 最短路徑](dijkstra.md) - 咖啡館裡 20 分鐘構思的傳奇
- [Bellman-Ford](bellman-ford.md) - 父子檔合作、取名後悔的演算法
- [Floyd-Warshall](floyd-warshall.md) - 「教學生的小練習」變經典
- [A* 搜尋](a-star.md) - 寫在機票存根背面的公式
- [最小生成樹](mst.md) - 貪心策略竟然 100% 最優
- [拓撲排序](topological-sort.md) - npm、make 背後的隱形英雄

### 字串處理

- [KMP 字串搜尋](kmp.md) - 為出國留學推薦信而做的研究
- [Levenshtein 編輯距離](levenshtein.md) - 冷戰時期誕生的「您是不是要找…」

### 密碼學

- [RSA 加密](rsa.md) - 酒後失眠的靈光乍現
- [Diffie-Hellman 金鑰交換](diffie-hellman.md) - 浴室裡的顏料混合實驗
- [橢圓曲線加密](ecc.md) - 純數學家闖入密碼學界
- [Shor 演算法](shor.md) - 量子電腦對 RSA 的死刑宣告

### 壓縮

- [哈夫曼編碼](huffman.md) - 為了買房、為了免考期末考
- [LZ77 與 LZW](lz77.md) - 從觀察重複到催生 ZIP 與 GIF
- [JPEG 與 DCT](jpeg.md) - 為省電話費而發明的圖像壓縮

### 機器學習與 AI

- [感知機](perceptron.md) - 頭版頭條到 AI 寒冬
- [卷積神經網路](cnn.md) - 貓的視覺皮質到 ImageNet 革命
- [蒙地卡羅樹搜尋與 AlphaGo](mcts.md) - 隨機模擬擊敗圍棋冠軍
- [Hopfield 網路](hopfield.md) - 物理學家的記憶體數學模型
- [隨機梯度下降](sgd.md) - 從賭場到訓練 GPT

### 網路

- [乙太網 CSMA/CD](csma-cd.md) - 隨機扔骰子的防撞機制
- [BBR 擁塞控制](bbr.md) - 讓 YouTube 變快的水管比喻
- [PageRank](pagerank.md) - 用論文引用次數打敗搜尋引擎垃圾

### 其他經典

- [蒙地卡羅模擬](monte-carlo.md) - 接龍撲克催生的隨機方法
- [模擬退火](simulated-annealing.md) - 打鐵鑄造啟發的最佳化
- [Kelly 公式](kelly.md) - 被賭場列入黑名單的下注公式
- [Viterbi 演算法](viterbi.md) - 從作業題到創立高通
- [Karmarkar 演算法](karmarkar.md) - 差點被列為軍事機密
- [Gale-Shapley 穩定匹配](gale-shapley.md) - 拿諾貝爾獎的「相親演算法」
- [蟻群演算法](ant-colony.md) - 螞蟻的費洛蒙與最短路徑

> 資料結構故事見 [資料結構](../資料結構/index.md)；電腦史與數理邏輯故事見 [歷史故事](../歷史故事/index.md)。

## 日誌

- 參見 [log.md](log.md)