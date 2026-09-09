# Alice 與 Bob：密碼學界的國民情侶

**領域**：[數理邏輯與電腦史](../categories/history.md) | **年代**：1978 | **相關**：[密碼學](../concepts/cryptography.md)

---

**趣味點**：密碼學論文過去一直用「A 方與 B 方」描述傳輸，枯燥又容易混淆。RSA 發明者引入了 Alice 與 Bob，後來學者們還加入「竊聽者 Eve」和「壞蛋 Mallory」，硬生生把密碼學論文寫成了八點檔連續劇。

1978 年，[RSA](../algorithms/rsa.md) 加密演算法的發明者們（Ron Rivest 等人）在論文中引入了 **Alice（發送者）與 Bob（接收者）**，用來簡化「A 方傳送訊息給 B 方」的枯燥敘述。

這個角色設定瞬間點燃了整個學界：大家開始自行加戲——
- **Eve**（Eavesdropper）：潛伏在線路上偷聽的竊聽者
- **Mallory**（Malicious）：會動手腳的惡意攻擊者
- 甚至還有更後期的 **Carol**、**Dave**、**Oscar** 等等

從此，Alice 和 Bob 成為全球密碼學與量子力學論文的「國民情侶」，所有通訊協定論文的開場白都是「Alice wants to send a message to Bob...」。

**延伸閱讀**：[RSA](rsa.md)、[Diffie-Hellman 金鑰交換](diffie-hellman.md)、[橢圓曲線加密](ecc.md)