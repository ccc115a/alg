# NoSQL（非關聯式資料庫）

## 概述

NoSQL（Not Only SQL，非關聯式資料庫）是一類不遵循傳統關聯式資料庫模型的資料庫系統。NoSQL 的興起主要為了應對：
- 大規模資料處理的需求
- 靈活的資料模型需求
- 高效能寫入需求
- 分散式架構的需求

NoSQL 資料庫並非要取代 SQL，而是提供了另一種資料處理的範式。兩者各有優勢，適用於不同的場景。

## NoSQL 的分類

NoSQL 資料庫可以分為四大類：

### 1. 文件資料庫（Document Database）

文件資料庫以文件（如 JSON、BSON、XML）為基本儲存單位，每個文件可以有不同的結構：

```json
{
  "user_id": "123",
  "name": "張三",
  "email": "zhang@example.com",
  "orders": [
    {"id": "o1", "total": 100},
    {"id": "o2", "total": 250}
  ]
}
```

代表系統：
- **MongoDB**：最流行的文件資料庫，使用 BSON 格式
- **CouchDB**：Apache 專案，支援離線同步
- **RethinkDB**：即時推送的 文件資料庫

### 2. 鍵值資料庫（Key-Value Database）

鍵值資料庫是最簡單的 NoSQL 模型，每個鍵對應一個值：

```
key: "users:123" → value: {name: "張三", age: 25}
key: "users:124" → value: {name: "李四", age: 30}
```

代表系統：
- **Redis**：記憶體鍵值資料庫，支援多種資料結構
- **Amazon DynamoDB**：AWS 的完全托管鍵值資料庫
- **etcd**：分散式鍵值資料庫，用於服務發現
- **Riak**：分散式鍵值資料庫

### 3. 寬欄位資料庫（Wide Column Database）

寬欄位資料庫（如 Cassandra）使用類似二維鍵值對的結構，支援動態欄位：

```sql
CREATE TABLE users (
    user_id text,
    name text,
    email text,
    orders map<text, int>,
    PRIMARY KEY (user_id)
);
```

代表系統：
- **Apache Cassandra**：高度可擴展的分散式資料庫
- **Google Bigtable**：Google 的原始寬欄位資料庫
- **HBase**：Apache 的 Hadoop 生態系統專案

### 4. 圖資料庫（Graph Database）

圖資料庫使用圖結構儲存資料，專門最佳化節點和關係的查詢：

```
節點：張三、李四、王五
關係：張三 -朋友→ 李四、張三 -同事→ 王五
```

代表系統：
- **Neo4j**：最流行的圖資料庫，使用 Cypher 查詢語言
- **Amazon Neptune**：AWS 的圖資料庫服務
- **TigerGraph**：高效能圖資料庫

## NoSQL 的優勢

### 高可擴展性

NoSQL 資料庫通常設計為分散式架構，可以水平擴展：

- 資料自動分片（sharding）
- 新節點可以透明加入
- 不需要修改應用程式邏輯

### 靈活的資料模型

文件資料庫的無 schema 特性：
- 可以儲存任意結構的資料
- 可以隨時新增或修改欄位
- 適合快速開發和迭代

### 高效能

針對特定場景的效能最佳化：

- LSM Tree 實現的 KV-Store：寫入效能極高
- 記憶體資料庫（如 Redis）：延遲極低
- 圖資料庫：複雜關係查詢效率高

### 高可用性

分散式 NoSQL 資料庫通常提供：
- **最終一致性**：犧牲即時一致性換取可用性
- **多副本複製**：資料有多個副本
- **自動容錯**：節點故障時自動恢復

## NoSQL 的劣勢

### 缺乏標準化

- 沒有統一的查詢語言（如 SQL）
- 每個系統有自己的 API 和查詢方式
- 應用程式難以在不同系統間遷移

### 一致性挑戰

- 很多 NoSQL 系統預設最終一致性
- 需要應用程式處理衝突
- 交易支援有限

### 成熟度

- 相比傳統關聯式資料庫，NoSQL 系統較新
- 文件和工具不如關聯式資料庫豐富
- 社群和專業人才相對較少

## SQL vs NoSQL

| 特性 | SQL | NoSQL |
|------|-----|-------|
| **資料模型** | 關聯式表格 | 文件、KV、寬欄位、圖 |
| **Schema** | 固定（需 Migration） | 動態（無 schema） |
| **交易** | 完整 ACID | 有限或最終一致性 |
| **擴展方式** | 垂直擴展為主 | 水平擴展為主 |
| **查詢語言** | 標準化 SQL | 各系統專屬 API |
| **JOIN** | 支援 | 通常不支援或效率低 |
| **適用場景** | OLTP、複雜查詢 | 大資料、即時處理 |

## CAP 定理

NoSQL 資料庫的設計選擇離不開 CAP 定理：

> 在分散式系統中，一致性（Consistency）、可用性（Availability）、分割容忍（Partition Tolerance）三者只能同時滿足兩者。

大多數 NoSQL 資料庫選擇：
- **CP**：犧牲可用性，確保一致性（如 Cassandra 的可調一致性其實兩者皆可）
- **AP**：犧牲一致性，確保可用性（如 DynamoDB、Cassandra）

詳細說明請參閱 [CAP-theorem.md](CAP-theorem.md)。

## 與 SQL 資料庫的整合

現代應用程式常見的架構：

```
┌─────────────┐     ┌─────────────┐
│   Web/App   │────▶│   API       │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌────────┐   ┌─────────┐   ┌────────┐
        │  SQL   │   │  NoSQL  │   │  Cache │
        │(pg/mysql)│   │(mongo/redis)│  │(Redis)│
        └────────┘   └─────────┘   └────────┘
```

常見模式：
- **快取模式**：SQL 為主要儲存，Redis 為快取層
- **多模型模式**：不同資料類型使用不同資料庫
- **CQRS**：讀寫分離，SQL 處理寫入，NoSQL 處理讀取

## 在 db6 中的位置

db6 是一個 KV-Store 基礎的資料庫框架，屬於 NoSQL 的鍵值資料庫範疇。db6 的三個引擎可以與其他 NoSQL 系統比較：

| 特性 | db6 | Redis | MongoDB |
|------|-----|-------|---------|
| 資料模型 | KV | KV + 多結構 | 文件 |
| 持久化 | 可選 | 可選 | 預設持久化 |
| 查詢語言 | SQL（可選） | 專屬指令 | MongoDB Query |
| 分散式 | 未來規劃 | Redis Cluster | 原生分散式 |

## 延伸閱讀

- Stonebraker, M. (2010). SQL Databases v. NoSQL Databases. Communications of the ACM.
- Brewer, E. (2012). CAP Twelve Years Later: How the "Rules" Have Changed. IEEE Computer.
- NoSQL Databases: https://nosql-database.org/