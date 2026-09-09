# MongoDB

## 概述

MongoDB 是一個基於文件導向（document-oriented）的 NoSQL 資料庫，使用 JSON-Like 的 BSON 格式儲存資料。MongoDB 由 MongoDB Inc. 開發，以其靈活的資料模型、水平擴展能力和豐富的查詢功能著稱，廣泛應用於現代網路應用和即時分析場景。

## 歷史

- **2007**：MongoDB 公司成立
- **2009**：MongoDB 1.0 發布
- **2012**：MongoDB 2.0，改進效能和工具
- **2015**：MongoDB 3.0，支援 Percona Server
- **2017**：MongoDB 3.6，強制的架構驗證
- **2018**：MongoDB 4.0，支援多文件交易
- **2020**：MongoDB 4.4，增強效能
- **2022**：MongoDB 6.0，聚合增強

## 文件模型

MongoDB 的核心是文件（document），類似 JSON 物件：

```json
{
  "_id": ObjectId("..."),
  "name": "張三",
  "email": "zhang@example.com",
  "age": 30,
  "address": {
    "city": "台北",
    "district": "信義區"
  },
  "tags": ["vip", "premium"],
  "orders": [
    {"id": "o1", "total": 1000},
    {"id": "o2", "total": 2500}
  ]
}
```

## 核心特性

### 靈活的 Schema

MongoDB 的文件可以是動態結構：

```javascript
// 文件 A
{"name": "張三", "age": 30}

// 文件 B（同集合但結構不同）
{"name": "李四", "email": "li@example.com", "phone": "0912-345-678"}

// 新增欄位不需要 ALTER TABLE
db.users.updateOne(
  {"_id": ObjectId("...")},
  {$set: {"new_field": "value"}}
);
```

### 巢狀文件

複雜的資料關係可以直接儲存在文件中：

```javascript
// 一個使用者的完整輪廓
{
  "_id": ObjectId("..."),
  "profile": {
    "name": "張三",
    "contact": {
      "email": "zhang@example.com",
      "phone": "0912-345-678"
    }
  },
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

## CRUD 操作

### Create（插入）

```javascript
// 插入單一文件
db.users.insertOne({
  "name": "張三",
  "age": 30
});

// 插入多個文件
db.users.insertMany([
  {"name": "李四", "age": 25},
  {"name": "王五", "age": 35}
]);
```

### Read（讀取）

```javascript
// 查詢所有
db.users.find();

// 條件查詢
db.users.find({"age": {"$gte": 25}});

// 投影（只返回特定欄位）
db.users.find({}, {"name": 1, "age": 1, "_id": 0});

// 巢狀欄位查詢
db.users.find({"address.city": "台北"});

// 陣列查詢
db.users.find({"tags": "vip"});
```

### Update（更新）

```javascript
// 更新單一文件
db.users.updateOne(
  {"_id": ObjectId("...")},
  {
    $set: {"age": 31},
    $currentDate: {"updated_at": true}
  }
);

// 更新多個文件
db.users.updateMany(
  {"age": {"$lt": 18}},
  {$set: {"status": "minor"}}
);

// 陣列操作
db.users.updateOne(
  {"_id": ObjectId("...")},
  {$push: {"tags": "premium"}}  // 添加到陣列
);
```

### Delete（刪除）

```javascript
// 刪除單一文件
db.users.deleteOne({"_id": ObjectId("...")});

// 刪除多個文件
db.users.deleteMany({"status": "inactive"});
```

## 索引

MongoDB 支援多種索引類型：

```javascript
// 單欄索引
db.users.createIndex({"email": 1});

// 複合索引
db.orders.createIndex({"user_id": 1, "created_at": -1});

// 多鍵索引（陣列欄位）
db.users.createIndex({"tags": 1});

// 文字索引（全文檢索）
db.articles.createIndex({"content": "text"});

// 地理位置索引
db.places.createIndex({"location": "2dsphere"});
```

## 聚合管道

MongoDB 的聚合管道非常強大：

```javascript
db.orders.aggregate([
  // Stage 1: 過濾
  {$match: {"status": "completed"}},
  
  // Stage 2: 分組
  {$group: {
    "_id": "$user_id",
    "total_spent": {$sum: "$total"},
    "order_count": {$sum: 1}
  }},
  
  // Stage 3: 排序
  {$sort: {"total_spent": -1}},
  
  // Stage 4: 限制
  {$limit: 10}
]);
```

## 交易（Transaction）

MongoDB 4.0+ 支援多文件交易：

```javascript
const session = db.getMongo().startSession();

session.startTransaction({
  readConcern: {level: "snapshot"},
  writeConcern: {w: "majority"}
});

try {
  const users = session.getDatabase("mydb").users;
  const orders = session.getDatabase("mydb").orders;
  
  users.updateOne(
    {"_id": userId},
    {$inc: {balance: -100}},
    {session}
  );
  
  orders.insertOne({
    user_id: userId,
    amount: 100,
    date: new Date()
  }, {session});
  
  session.commitTransaction();
} catch (error) {
  session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}
```

## 分片（Sharding）

MongoDB 支援水平擴展，通過分片分散資料：

```
┌──────────────────────────────────────────────────────┐
│                    MongoDB Cluster                   │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Shard 1    │  │  Shard 2    │  │  Shard 3    │   │
│  │ (Primary)   │  │ (Secondary) │  │ (Secondary) │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│         │                │                │          │
│  ┌──────┴────────────────┴────────────────┴──────┐  │
│  │                  Config Server                  │  │
│  │         (元資料和路由資訊)                      │  │
│  └────────────────────────────────────────────────┘  │
│                     │                                │
│  ┌──────────────────┴──────────────────────────┐   │
│  │              Mongos Router                    │   │
│  │         (路由查詢到正確的分片)                │   │
│  └───────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
```

分片鍵選擇很重要：
```javascript
// 選擇分片鍵
sh.shardCollection("mydb.orders", {"user_id": "hashed"});
```

## 儲存引擎

MongoDB 支援多個儲存引擎：

| 引擎 | 說明 |
|------|------|
| WiredTiger（預設） | 壓縮、文件級鎖、叢集索引 |
| In-Memory | 全部在記憶體，極低延遲 |
| Encrypted | 靜態加密 |

### WiredTiger

預設引擎，特性：
- **文件級鎖**：並發效能好
- **壓縮**：預設使用 Snappy 或 Zstandard
- **快取**：使用 WiredTiger Cache（預設為 50% 可用 RAM）

```javascript
// 查看引擎統計
db.serverStatus().wiredTiger;
```

## 在 db6 中的比較

| 特性 | MongoDB | db6 |
|------|---------|-----|
| 資料模型 | 文件（BSON） | KV / SQL 表 |
| Schema | 動態 | 固定（未來可能動態） |
| 查詢語言 | MongoDB Query | SQL |
| 交易 | 完整多文件交易 | 單引擎交易 |
| 分片 | 原生支援 | 未來規劃 |
| 索引類型 | 多種 | B-Tree |

## 應用場景

MongoDB 適合：
- **內容管理系統**：靈活的文件結構
- **即時分析**：聚合管道
- **物聯網**：時間序列資料
- **行動應用**：JSON 格式原生支援
- **快速開發**：不需要預先定義 Schema

不適合：
- **強一致性要求的金融系統**（交易場景）
- **複雜的 JOIN 查詢**
- **高度正規化的資料模型**

## 延伸閱讀

- MongoDB Documentation: https://docs.mongodb.com/
- MongoDB University: https://learn.mongodb.com/
- "MongoDB: The Definitive Guide" by Shannon Bradshaw et al.