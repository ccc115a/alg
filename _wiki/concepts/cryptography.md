# 密碼學

保護數位世界的通訊安全。從古典的 Enigma 到公鑰加密 RSA，再到量子電腦對現行體系的威脅，密碼學總在攻防之間演化。

## 核心特性

- **機密性**：確保只有持有金鑰的人能讀取內容。
- **公鑰機制**：加密與解密使用不同金鑰，解決金鑰交換難題。
- **數學難題**：安全強度奠基於因數分解、離散對數等公認困難的問題。
- **量子威脅**：Shor 演算法能破解 RSA 與 ECC，推動後量子密碼學。

## 經典演算法

- [RSA](../algorithms/rsa.md) — 因數分解困難度奠基的公鑰加密
- [Diffie-Hellman](../algorithms/diffie-hellman.md) — 公開交換共用金鑰
- [ECC](../algorithms/ecc.md) — 用更短金鑰達成同等安全的橢圓曲線
- [Shor](../algorithms/shor.md) — 量子電腦對 RSA 的死刑宣告

## 相關概念

- [資訊論](information-theory.md) — 金鑰的熵決定安全強度