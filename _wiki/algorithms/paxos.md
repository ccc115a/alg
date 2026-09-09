# Paxos 教堂：被「請神下山」的古希臘故事

**領域**：[數理邏輯與電腦史](../categories/history.md) | **年代**：1989/1998 | **發明者**：[Leslie Lamport](../algorithms/byzantine-generals.md)

---

**趣味點**：Lamport 把嚴肅的分散式演算法寫成古希臘 Paxos 島議會的故事，審稿人看完氣炸退稿。結果 9 年後大家發現這是分散式共識的唯一解法，期刊編輯只好乖乖跑回去「請神下山」發表這篇奇文。

在[拜占庭將軍問題](byzantine-generals.md)之後，Leslie Lamport 繼續挑戰分散式系統的終極難題：如何在有網路延遲、封包遺失、甚至有惡意節點的情況下，讓多台電腦達成**一致共識**（例如金融轉帳、分散式資料庫的資料同步）。

但他不想再寫枯燥的數學與程式碼。1989 年，他寫下論文《**The Part-Time Parliament**（Paxos 教堂）》，把演算法整個包裝成一個虛構的古希臘小島——**Paxos 島**：

- 島上有一個議會，議員們靠投票通過法律
- 重點是這些議員「很不敬業」，經常偷跑去兼職（模擬**伺服器宕機**）
- 島上傳遞訊息全靠信差，而信差會迷路、會遲到（模擬**封包遺失與延遲**）
- 整篇論文甚至煞有介事地引用「Paxos 島上的考古發現」

結果：審稿人完全不賞識這個幽默，退稿理由是「故事太荒謬，請改成嚴肅的電腦科學論文」。Lamport 氣得撤稿，把論文扔進抽屜。

**歷史的逆轉**：1990 年代末，網際網路爆紅，分散式系統工程師們發現——不管怎麼努力，都繞不開這個演算法。1998 年，TOCS 期刊編輯主動聯繫 Lamport，懇求他發表。九年後，這篇古希臘議會論文終於重見天日。

Lamport 後來又補了一篇簡化版《Paxos Made Simple》，摘要只寫一句話：

> "The Paxos algorithm, when presented in plain English, is very simple."

如今 Paxos 及其衍生演算法（如 Raft 共識演算法）是 Google Bigtable/Spanner、亞馬遜 AWS 的定海神針。

**延伸閱讀**：[拜占庭將軍問題](byzantine-generals.md)、[中本聰與比特幣](bitcoin.md)、[乙太網 CSMA/CD](csma-cd.md)