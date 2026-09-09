# SQLite

## 概述

SQLite 是一個輕量級的嵌入式關聯式資料庫管理系統，以其零配置、無伺服器和單檔案儲存的特性著稱。SQLite 是世界上部署最廣泛的資料庫引擎，存在於幾乎每支智慧手機、大多數網頁瀏覽器和無數應用程式中。

與傳統的客戶端-伺服器資料庫（如 PostgreSQL、MySQL）不同，SQLite 不是一個資料庫伺服器，而是一個可直接嵌入應用程式的資料庫程式庫。

## 歷史

- **2000**：D. Richard Hipp 開始開發 SQLite，最初用於導彈驅逐艦的即時追蹤系統
- **2000**：SQLite 1.0 發布，使用 GNU GPL
- **2005**：SQLite 3.0 發布，重新設計的儲存引擎
- **2010**：SQLite 成為 iPhone 和 Android 的預設資料庫
- **2015**：SQLite 3.9.0，支援 JSON
- **2018**：SQLite 3.24.0，支援 UPSERT
- **2022**：SQLite 3.40，支援 RBU（Resumable Bulk Update）

## 設計哲學

SQLite 的設計哲學是「簡單、可靠、輕量」：

1. **無需設定**：下載後直接使用，無需安裝或設定
2. **無需伺服器**：資料庫操作在同一行程式中完成
3. **單檔案儲存**：整個資料庫是一個磁碟檔案
4. **交易完整性**：完整的 ACID 交易支援

## 架構

SQLite 的核心架構：

```
┌─────────────────────────────────────────┐
│           SQLite Application            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         SQLite Core (C library)          │
│  ┌───────────────────────────────────┐  │
│  │     Interface (sqlite3 CLI/API)    │  │
│  └────────────────┬──────────────────┘  │
│  ┌────────────────▼──────────────────┐  │
│  │       Query Parser & Planner        │  │
│  └────────────────┬──────────────────┘  │
│  ┌────────────────▼──────────────────┐  │
│  │         Code Generator              │  │
│  └────────────────┬──────────────────┘  │
│  ┌────────────────▼──────────────────┐  │
│  │         Virtual Machine (VDBE)      │  │
│  └────────────────┬──────────────────┘  │
└───────────────────┼─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│         Storage Engine (B-Tree)          │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │   B-Tree    │  │    Pager        │  │
│  │  Module     │  │    Module       │  │
│  └─────────────┘  └────────┬────────┘  │
│                            │           │
│  ┌─────────────────────────▼────────┐  │
│  │      OS Interface (POSIX/WIN32)   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 核心元件

**介面層（Interface）**：提供 sqlite3 CLI 和 C API。

**查詢解析器（Parser）**：將 SQL 語句解析為語法樹。

**查詢最佳化器（Query Optimizer）**：分析語法樹，生成最佳執行計畫。

**虛擬機器（Virtual Database Engine, VDBE）**：類 JVM 的位元組碼解釋器，執行由程式碼生成器產生的程式碼。

**B-Tree 模組**：使用改進的 B+Tree 結構儲存資料。每個表和索引都是獨立的 B+Tree。

**Pager 模組**：負責分頁記憶體管理和 crash recovery。處理 WAL 和日誌模式。

**OS 介面**：抽象不同作業系統的檔案操作差異。

## 儲存格式

SQLite 資料庫檔案的結構：

```
┌──────────────────┐
│   Header (100B)  │ - Magic string, version, page size
├──────────────────┤
│   Free-block     │ - First freeblock on page 1
│     List         │
├──────────────────┤
│   Cell Pointers  │ - Array of offsets to cells
│   (on page 1)    │
├──────────────────┤
│   Cell Content   │ - Actual data
│    Area          │
└──────────────────┘
```

### 頁大小

SQLite 的頁大小可以是 512、1024、2048、4096、16384 或 32768 位元組。預設為 4096 位元組。

## B-Tree 的使用方式

SQLite 使用的是一種 B-Tree 的變體，有以下特點：

1. **每個表一個 B-Tree**：叢集索引儲存整行的資料
2. **每個索引一個 B-Tree**：非叢集索引只儲存鍵和 ROWID
3. **葉節點包含完整資料**：類似 B+Tree
4. **使用 ROWID 作為隱式主鍵**：如果表沒有宣告主鍵

```sql
-- 叢集索引（預設）
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);
-- B-Tree: key=id, value=(id, name)

-- 非叢集索引
CREATE INDEX idx_users_name ON users(name);
-- B-Tree: key=name, value=ROWID
```

## WAL 模式

SQLite 3.7.0 引入的 WAL（Write-Ahead Logging）模式提供了更好的並發效能：

```sql
-- 啟用 WAL 模式
PRAGMA journal_mode=WAL;

-- 預設模式是 DELETE
PRAGMA journal_mode=DELETE;
```

WAL 的優勢：
- **讀寫可以並發**：讀取不需要封鎖寫入
- **寫入效能更好**：順序寫入日誌
- **crash recovery 更快**：無需回復日誌

## FTS5 全文檢索

SQLite 支援通過 FTS5 虛擬表實現全文檢索：

```sql
-- 建立 FTS5 表
CREATE VIRTUAL TABLE documents USING fts5(
    title,
    content
);

-- 全文檢索
SELECT * FROM documents WHERE documents MATCH 'database';
```

FTS5 使用倒排索引，支援：
- 布林運算（AND、OR、NOT）
- 前綴搜尋（datab*）
- 排名（BM25）

## 限制

SQLite 適用於中小規模應用，但有以下限制：

| 限制 | 值 |
|------|-----|
| 最大資料庫大小 | 281 TB |
| 最大表數量 | 無限（受限於檔案系統） |
| 最大索引數量 | 無限 |
| 最大列數 | 32767 |
| 最大 ROWID | 2^63 |
| 線程數量 | 建議單線程寫入 |

## 適用場景

SQLite 最適合：
- **嵌入式系統**：iOS、Android、IoT 設備
- **單機應用**：桌面應用、工具軟體
- **小型網站**：低至中等流量的網站
- **測試和開發**：無需設定即可快速開始

SQLite 不適合：
- **高並發寫入**：寫入是序列化的
- **大規模資料**：TB 級別的資料
- **需要網路存取的場景**：用戶端-伺服器架構

## 在 db6 中的角色

db6 的 [BTreeEngine](../src/engine/btree/) 移植自 sql6 的 pager/btree 實現，與 SQLite 的 B-Tree 有相似的設計理念。兩者都是：
- 使用頁（page）作為基本儲存單位
- 使用 B-Tree 組織索引
- 支援 WAL 模式的 crash recovery

db6 可以視為一個簡化版的 SQLite，專注於 KV 儲存，並提供 SQL 作為可選介面。

## 延伸閱讀

- SQLite Documentation: https://www.sqlite.org/docs.html
- The SQLite Database File Format: https://www.sqlite.org/fileformat.html
- Hipp, D. R. (2015). The Definitive Guide to SQLite. Apress.