# smith_waterman_dp.py — Smith-Waterman 本地比對

## 用途

找出兩 DNA 序列間分數最高的本地比對區段（local alignment）。

## 函式

| 函式 | 說明 |
|---|---|
| `smith_waterman(a, b, match=2, mismatch=-1, gap=-1)` | 回傳 `(最高分, a 的區間, b 的區間)` |

## 原理

允許比對從任意位置開始、任意位置結束，中途可插入 gap。
與全域比對 (Needleman-Wunsch) 的差異在於引入 **0 重新起點**：
分數掉到負值就歸零，讓最佳區段自然浮現。

## 狀態定義

```
H[i][j] = 以 a[0..i-1] 結尾、b[0..j-1] 結尾的最佳本地比對分數
```

## 轉移方程

```
H[i][j] = max( 0,                              # 重新起點
               H[i-1][j-1] + s(a[i-1],b[j-1]), # 對角：配對/錯配
               H[i-1][j]   + gap,               # 刪除（gap 在 b）
               H[i][j-1]   + gap )              # 插入（gap 在 a）
其中 s(match)=+2, s(mismatch)=-1, gap=-1
```

## 回溯

從全表最大值 `(i,j)` 出發，沿「等於當前分數的來源」退回，
直到 `H[i][j] == 0`，得到兩條序列上的區間。

## 複雜度

- 時間 **O(nm)**
- 空間 **O(nm)**（只求分數可用 Hirschberg 或 rolling array 壓到 O(min(n,m))）

## 特性

- 保證最優本地比對（生物資訊學的精確基準）
- 全資料庫掃描（query × 數十億 bp）不可行 → 實務上用 BLAST 啟發式取代
