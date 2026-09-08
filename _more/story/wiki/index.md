# 演算法故事 Wiki

> 從花拉子米到 AlphaGo，一部以故事串連的演算法發展史。

---

## 分類

| 分類 | 故事數 | 精選 |
|------|--------|------|
| [排序與搜尋](categories/sorting-searching.md) | 4 | 二元搜尋的打字錯誤、公平洗牌 |
| [圖論與最短路徑](categories/graph.md) | 6 | 咖啡館裡的 Dijkstra、飛機餐巾紙上的 A* |
| [字串處理](categories/string.md) | 2 | 為留學推薦信而發明的 KMP |
| [資料結構](categories/data-structures.md) | 5 | 波音的 B 樹、「寧可錯殺」的 Bloom Filter |
| [密碼學](categories/cryptography.md) | 4 | 酒後失言的 RSA、浴室裡的 Diffie-Hellman |
| [壓縮](categories/compression.md) | 3 | 為了買房的 Huffman、GIF 專利之亂 |
| [機器學習與 AI](categories/machine-learning.md) | 5 | 頭版頭條到 AI 寒冬、AlphaGo 的誕生 |
| [數值方法](categories/numerical.md) | 4 | 飛機餐巾紙上的 FFT、登月的卡爾曼濾波 |
| [計算幾何](categories/geometry.md) | 3 | 餐巾紙上的凸包、黑洞照片 |
| [網路](categories/networking.md) | 3 | 乙太網防撞、YouTube 變快的 BBR |
| [其他經典](categories/misc.md) | 8 | 賭場黑名單的 Kelly 公式、百萬美元的 NP |
| [數理邏輯與電腦史](categories/history.md) | 45 | 拜占庭將軍、Paxos 教堂、阿波羅 1202 警報 |

---

## 全部故事一覽

### 排序與搜尋
- [二元搜尋的 60 年 Bug](algorithms/binary-search-bug.md) — 全世界頂尖工程師被一個加號卡關
- [快速排序](algorithms/quick-sort.md) — 莫斯科留學時為翻譯字典而發明
- [Fisher-Yates 洗牌](algorithms/fisher-yates.md) — 保證絕對公平的洗牌法
- [基數排序](algorithms/radix-sort.md) — 美國人口普查催生的非比較排序

### 圖論與最短路徑
- [Dijkstra 最短路徑](algorithms/dijkstra.md) — 咖啡館裡 20 分鐘構思的傳奇
- [Bellman-Ford](algorithms/bellman-ford.md) — 父子檔合作、取名後悔的演算法
- [Floyd-Warshall](algorithms/floyd-warshall.md) — 「教學生的小練習」變經典
- [A* 搜尋](algorithms/a-star.md) — 寫在機票存根背面的公式
- [最小生成樹](algorithms/mst.md) — 貪心策略竟然 100% 最優
- [拓撲排序](algorithms/topological-sort.md) — npm、make 背後的隱形英雄

### 字串處理
- [KMP 字串搜尋](algorithms/kmp.md) — 為出國留學推薦信而做的研究
- [Levenshtein 編輯距離](algorithms/levenshtein.md) — 冷戰時期誕生的「您是不是要找…」

### 資料結構
- [B-Tree 與 B+ 樹](algorithms/b-tree.md) — 波音的「B」代表什麼？
- [紅黑樹](algorithms/red-black-tree.md) — 讓 Linux 核心變快的著色規則
- [跳過表](algorithms/skip-list.md) — 玩具實驗意外媲美平衡樹
- [Bloom Filter](algorithms/bloom-filter.md) — 寧可錯殺不可放過的機率過濾器
- [連結串列](algorithms/linked-list.md) — 一行程式碼改變世界

### 密碼學
- [RSA 加密](algorithms/rsa.md) — 酒後失眠的靈光乍現
- [Diffie-Hellman 金鑰交換](algorithms/diffie-hellman.md) — 浴室裡的顏料混合實驗
- [橢圓曲線加密](algorithms/ecc.md) — 純數學家闖入密碼學界
- [Shor 演算法](algorithms/shor.md) — 量子電腦對 RSA 的死刑宣告

### 壓縮
- [哈夫曼編碼](algorithms/huffman.md) — 為了買房、為了免考期末考
- [LZ77 與 LZW](algorithms/lz77.md) — 從觀察重複到催生 ZIP 與 GIF
- [JPEG 與 DCT](algorithms/jpeg.md) — 為省電話費而發明的圖像壓縮

### 機器學習與 AI
- [感知機](algorithms/perceptron.md) — 頭版頭條到 AI 寒冬
- [卷積神經網路](algorithms/cnn.md) — 貓的視覺皮質到 ImageNet 革命
- [蒙地卡羅樹搜尋與 AlphaGo](algorithms/mcts.md) — 隨機模擬擊敗圍棋冠軍
- [Hopfield 網路](algorithms/hopfield.md) — 物理學家的記憶體數學模型
- [隨機梯度下降](algorithms/sgd.md) — 從賭場到訓練 GPT

### 數值方法
- [快速傅立葉變換](algorithms/fft.md) — 飛機餐巾紙上的冷戰演算法
- [卡爾曼濾波](algorithms/kalman.md) — 從登月導航到賭場輪盤
- [龍格-庫塔法](algorithms/runge-kutta.md) — 幫助太空人回家的數值方法
- [SVD 奇異值分解](algorithms/svd.md) — 歐拉 1750 年的純數學，220 年後變身推薦系統

### 計算幾何
- [Graham Scan 凸包](algorithms/graham-scan.md) — 餐巾紙上塗塗改改的幾何奇蹟
- [Marching Cubes](algorithms/marching-cubes.md) — CT 掃描到《魔鬼終結者 2》
- [Ramer-Douglas-Peucker](algorithms/rdp.md) — Google Maps 背後的線段簡化

### 網路
- [乙太網 CSMA/CD](algorithms/csma-cd.md) — 隨機扔骰子的防撞機制
- [BBR 擁塞控制](algorithms/bbr.md) — 讓 YouTube 變快的水管比喻
- [PageRank](algorithms/pagerank.md) — 用論文引用次數打敗搜尋引擎垃圾

### 其他經典
- [蒙地卡羅模擬](algorithms/monte-carlo.md) — 接龍撲克催生的隨機方法
- [模擬退火](algorithms/simulated-annealing.md) — 打鐵鑄造啟發的最佳化
- [Kelly 公式](algorithms/kelly.md) — 被賭場列入黑名單的下注公式
- [Viterbi 演算法](algorithms/viterbi.md) — 從作業題到創立高通
- [Karmarkar 演算法](algorithms/karmarkar.md) — 差點被列為軍事機密
- [Gale-Shapley 穩定匹配](algorithms/gale-shapley.md) — 拿諾貝爾獎的「相親演算法」
- [蟻群演算法](algorithms/ant-colony.md) — 螞蟻的費洛蒙與最短路徑
- [NP 完全性](algorithms/np-completeness.md) — 用數學證明「不可能」的終極邊界

### 數理邏輯與電腦史

#### 數理邏輯的起源（1900–1945）
- [希爾伯特的 23 個問題](algorithms/hilbert.md) — 一場「我們終將知道一切」的宣言
- [哥德爾不完備定理](algorithms/godel.md) — 用編碼自毀數學的美麗炸彈
- [Lambda 演算](algorithms/lambda-calculus.md) — 一行函數推翻一切極限
- [圖靈機](algorithms/turing-machine.md) — 「預測腳趾甲長度的怪異機器」走向現實
- [馮·紐曼架構](algorithms/von-neumann-architecture.md) — 把指令和資料一起放進記憶體
- [LISP 與 Steve Russell](algorithms/lisp.md) — 研究生用 9 小時「打臉」老師

#### 早期電腦與作業系統（1946–1975）
- [第一個「真·電腦 Bug」](algorithms/grace-hopper-bug.md) — 一隻被電死的蛾
- [第一個電腦病毒 Creeper 與 Reaper](algorithms/creeper-reaper.md) — 「有本事來抓我啊！」
- [阿波羅 11 號的 1202 警報](algorithms/apollo-1202.md) — 排程演算法救回登月
- [脫胎於遊戲機的 UNIX](algorithms/unix.md) — 為了玩遊戲寫出作業系統
- [所有展示之母](algorithms/mother-of-all-demos.md) — 木頭滑鼠驚呆全場
- [Pong 的投幣箱意外](algorithms/pong.md) — 不是 Bug，是硬幣塞爆
- [第一封 Email](algorithms/first-email.md) — 忘了內容的發明者
- [Hello, World!](algorithms/hello-world.md) — 隨手的問候成了入會儀式
- [哲學家就餐問題](algorithms/dining-philosophers.md) — 五隻筷子講清死鎖
- [Brooks 定律](algorithms/brooks-law.md) — 加人只會讓專案更慢
- [摩爾定律](algorithms/moores-law.md) — 半導體界的「預言式」經驗法則

#### 個人電腦與分散式系統（1975–1990）
- [拜占庭將軍問題](algorithms/byzantine-generals.md) — 名字取得好，論文就紅了
- [GNU 宣言](algorithms/stallman-gnu.md) — 一臺印表機震撼開源世界
- [Apple II 的 40 欄螢幕](algorithms/apple2-40col.md) — 省錢省出縮寫壞習慣
- [Alice 與 Bob](algorithms/alice-and-bob.md) — 密碼學界的國民情侶
- [第一封垃圾郵件](algorithms/first-spam.md) — 偷懶群發的下場
- [宇宙終極答案 42](algorithms/number-42.md) — 極客彩蛋的祖師爺
- [蓋茲的 640KB 傳說](algorithms/gates-640k.md) — 「夠用了」永遠不夠用
- [肯·湯普森的魔鬼編譯器](algorithms/ken-thompson-compiler.md) — 連原始碼都查不出後門
- [莫里斯蠕蟲](algorithms/morris-worm.md) — 想測量網路，反而癱瘓了它
- [Paxos 教堂](algorithms/paxos.md) — 被「請神下山」的古希臘故事

#### 網路時代（1990–2008）
- [全球資訊網「切勿關機」](algorithms/www.md) — 紅貼紙守護的 NeXT
- [Linux 的小專案](algorithms/linux.md) — 一個「興趣」統治世界
- [企鵝 Tux 與鴨嘴獸](algorithms/tux-penguin.md) — 被咬出來的吉祥物
- [Pentium 除法 Bug](algorithms/pentium-fdiv.md) — 4.75 億美元的鑰匙圈
- [404 的都市傳說](algorithms/http-404.md) — CERN 的 404 號房
- [10 天寫出的 JavaScript](algorithms/javascript.md) — 雷鋒與雷峰塔的關係
- [信鴿傳輸 IP 封包](algorithms/rfc1149.md) — RFC 1149 真的被執行
- [無限猴子通訊協定](algorithms/rfc2795-monkeys.md) — 猴子沒香蕉吃了
- [火星軌道器的單位悲劇](algorithms/mars-climate-orbiter.md) — 1.25 億美元打水漂
- [Y2K 千禧蟲](algorithms/y2k.md) — 兩個位數的萬年蟲

#### 現代（2008–2024）
- [中本聰與比特幣](algorithms/bitcoin.md) — 留下百萬顆比特幣消失的男人
- [Heartbleed 心臟出血](algorithms/heartbleed.md) — 第一個被「品牌化」的漏洞
- [left-pad 的 11 行程式碼](algorithms/left-pad.md) — 癱瘓半個網路
- [第一張黑洞照片](algorithms/chirp.md) — 用搬家貨車運 5PB 硬碟
- [瀏覽器版本號突破 100](algorithms/browser-version-100.md) — Y2K 的重演
- [ChatGPT 世代](algorithms/chatgpt.md) — 5 天破百萬的 AI 軍備競賽
- [CrowdStrike 全球藍屏](algorithms/crowdstrike.md) — 防毒防到全世界中毒
