# 父子檔合作、取名後悔的演算法：Bellman-Ford

**領域**：[圖論與最短路徑](../categories/graph.md) | **年代**：1955–1958 | **發明者**：Richard Bellman、Lester Ford Sr. & Jr.

---

1955 年，數學家理查·貝爾曼（Richard Bellman）在研究「多階段決策過程」時，發展出了**動態規劃**（Dynamic Programming）的理論框架。後來福特父子（Lester Ford Jr. 與 Lester Ford Sr.——沒錯，真的是父子檔！）將其應用於網路最短路徑問題。

Bellman-Ford 演算法的強大之處在於：它能處理**負權重邊**的圖——而 [Dijkstra](dijkstra.md) 在這種情況下會完全失效。這個特性讓它成為了網路路由協定（Distance-Vector Routing）的核心，你在學校機房裡每台電腦能互相連線，背後就有 Bellman-Ford 在默默運作。

最傳奇的逸事是：理查·貝爾曼後來**公開後悔**把這個方法取名為「動態規劃」。因為他故意取了一個聽起來很厲害的術語來取悅當時的國防部贊助人——「動態」聽起來很科學，「規劃」聽起來很務實——沒想到這個名字從此流傳千古，他自己都改不回來了。

---

**教訓**：名字取得好，可以流傳千古。貝爾曼可能沒想到他的一時投機成就了一個學科的命名。

**延伸閱讀**：[Dijkstra](dijkstra.md)、[Floyd-Warshall](floyd-warshall.md)、[動態規劃概念](../concepts/dynamic-programming.md)
