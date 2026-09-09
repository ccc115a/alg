# CAP 定理（CAP Theorem）

## 概述

CAP 定理（也稱為 Brewer's theorem）是分散式系統領域最重要的理論基礎之一，由加州大學柏克萊分校的分校教授 Eric Brewer 在 2000 年的 PODC（Principles of Distributed Computing）會議上提出，並在 2002 年由 Seth Gilbert 和 Nancy Lynch 形式化證明。

CAP 定理表明：任何分散式資料庫系統只能同時滿足以下三個特性中的兩個：

- **C**onsistency（一致性）
- **A**vailability（可用性）
- **P**artition Tolerance（分割容忍）

## 定理內容

> 在存在網路分割（network partition）的情況下，一個分散式系統無法同時保證一致性和可用性。

這個定理的關鍵前提是**網路分割必然會發生**。在大規模分散式系統中，網路設備故障、網路壅塞、機櫃層級的網路問題等都可能導致網路分割。因此，系統設計者必須在一致性和可用性之間做出選擇。

## 三個特性

### 一致性（Consistency）

在 CAP 理論中，一致性指的是**線性一致性（Linearizability）**或**原子一致性**：對系統的任何讀取都會返回最近一次寫入的結果，所有節點看到相同的資料。

```python
# 線性一致性的例子
# 在節點 A 寫入
write(A, "value1")
# 隨後在節點 B 讀取，必定能得到 "value1" 或更新的值
# 不可能讀到 "value1" 之前的值
```

### 可用性（Availability）

可用性指的是**每次請求都會收到（非錯誤的）響應**。系統在任何情況下（除非整個系統故障）都必須能夠處理請求並返回結果。

```python
# 可用性的例子
# 無論何時發送請求，都能得到回應
result = read(A)  # 總是返回結果（可能是舊值）
```

### 分割容忍（Partition Tolerance）

分割容忍指的是系統能夠容忍網路分割：即使網路中的一部分節點無法與其他節點通訊，系統仍然能繼續運作。

在現實中，網路分割是**必然會發生**的：
- 網路設備故障
- 機房網路中斷
- 資料中心之間的連線問題

因此，分散式系統**必須**是分割容忍的。

## 為什麼只能同時滿足兩個？

假設有兩個節點 A 和 B，它們之間發生了網路分割：

```
┌─────────┐       ✗       ┌─────────┐
│    A    │ ─────────── │    B    │
│ (寫入)  │   網路分割   │ (讀取)  │
└─────────┘              └─────────┘
```

**如果選擇 C（一致性）+ P（分割容忍）**：
- A 和 B 之間的連線斷開後
- 為了保持一致，系統必須停止服務（拒絕寫入），直到分割修復
- 可用性犧牲

**如果選擇 A（可用性）+ P（分割容忍）**：
- A 和 B 之間的連線斷開後
- 系統繼續處理請求
- 但 A 和 B 的資料可能不一致（各自為自己的客戶端提供服務）
- 一致性犧牲

**如果選擇 C（一致性）+ A（可用性）**：
- 這只在不存在網路分割的情況下才可能
- 但網路分割是必然發生的，所以這不是一個現實的選擇

## CAP 的常見誤解

### 誤解 1：只能在三個特性中選一個

這是對 CAP 定理最常見的誤解。實際上：
- 分割容忍是**必須**的（因為網路分割必然發生）
- 因此真正的選擇是：**在 C 和 A 之間選擇**

### 誤解 2：CAP 是二元選擇

實際上，許多系統提供的是**可調一致性（tunable consistency）**：
- Cassandra 提供可調一致性，可以為每個查詢選擇一致性級別
- 可以犧牲一些一致性來提高可用性

### 誤解 3：CAP 意味著完全放棄其中一個特性

在正常運作（無網路分割）時，系統可以同時提供 C、A、P。只有在分割發生時，才需要做出取捨。

## 實際應用

### 選擇 CP 的系統

**HBase**：
- 使用 ZooKeeper 進行協調
- 分割期間 Region Server 不可用
- 確保強一致性

**MongoDB（大多數配置）**：
- 使用主從複製
- 分割期間主節點不可用

**etcd**：
- 基於 Raft 共識演算法
- 需要大多數節點同意才能確認寫入

### 選擇 AP 的系統

**Cassandra**：
- 使用最終一致性
- 任何節點都可以接受寫入
- 讀取可能返回過時資料

**Amazon DynamoDB**：
- 預設最終一致性
- 提供強一致性讀取選項

**CouchDB**：
- 為可用性優化
- 衝突通過應用層解決

### 混合策略

**Google Spanner**：
- 正常運作時提供強一致性和高可用性
- 使用 TrueTime API（基於時鐘同步）來判斷分割是否發生
- 分割期間可能犧牲一些可用性

**cockroachdb**：
- 提供可調一致性
- 可以選擇 READ COMMITTED 或 SERIALIZABLE

## PACELC 模型

為了解決 CAP 定理的不足，Daniel J. Abadi 提出了 PACELC 模型：

```
If (Partition):
  - Choose: Either Consistency or Availability (CAP)

Else (No Partition):
  - Choose: Either Latency or Consistency
```

這個模型強調：在沒有分割時，系統設計者需要在延遲和一致性之間做出選擇。

## 在 db6 中的考慮

db6 目前是一個單機、多引擎的資料庫框架。在未來規劃的分散式版本中，需要考慮 CAP 定理：

| 引擎 | 一致性 | 可用性 | 說明 |
|------|--------|--------|------|
| Memory | 強一致 | 高 | 無持久化，無網路問題 |
| BTree | 強一致 | 高 | 支援交易，磁碟持久化 |
| LSM | 最終一致 | 高 | 寫入快，讀取可能需檢查多層 |

如果要擴展為分散式系統，db6 可能需要：
- 使用 Raft 共识协议處理副本同步
- 或像 Cassandra 一樣選擇 AP 模型
- 提供可調一致性給應用程式選擇

## 延伸閱讀

- Brewer, E. (2012). CAP Twelve Years Later: How the "Rules" Have Changed. IEEE Computer.
- Gilbert, S., & Lynch, N. (2002). Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services. ACM SIGACT News.
- Abadi, D. J. (2012). Consistency Tradeoffs in Modern Distributed Database System Design. IEEE Computer.