# LSM Tree（Log-Structured Merge-tree）

## 概述

LSM Tree（Log-Structured Merge-tree，日誌結構合併樹）是一種針對寫入優化的資料結構，最初由 Patrick O'Neil 等人在 1996 年的論文中提出。與傳統的 B 樹系列相比，LSM Tree 將隨機寫入轉換為順序寫入，因此在大量寫入場景下表現優異。這種資料結構後來被廣泛應用於許多著名的儲存系統中，包括 Google 的 LevelDB、RocksDB、Cassandra、WiredTiger 等。

## 歷史背景

1996 年，Patrick O'Neil、Edward Cheng、Dick Scales 和 Ewen Shekita 發表了論文《The Log-Structured Merge-Tree (LSM-Tree)》，提出了 LSM Tree 的概念。論文的動機是解決傳統 B 樹在高寫入量場景下的效能問題。在許多應用中，寫入次數遠多於讀取次數（例如日誌記錄、事件追蹤、物聯網資料收集等），此時 B 樹的隨機寫入成本成為瓶頸。

LSM Tree 的核心靈感來自日誌結構檔案系統（Log-Structured File System）的思想：將所有寫入都當作順序 Append 來處理，利用順序 I/O 的高速特性。這個概念後來被證明非常適合現代的 SSD 儲存裝置，因為順序寫入的效能遠優於隨機寫入。

## 結構組成

LSM Tree 通常由多個層級組成，從上到下依序為：

### 1. MemTable（記憶體表）

MemTable 是 LSM Tree 最上層的元件，是一個記憶體中的有序資料結構（通常是 Skip List 或紅黑樹）。當資料寫入時，首先進入 MemTable。這種設計使得寫入操作完全在記憶體中完成，延遲極低。

MemTable 有大小限制，當它達到預設的容量上限時，會被轉換為 Immutable MemTable，並觸發一次 flush 操作將資料寫入磁碟。

### 2. WAL（Write-Ahead Log，提前寫入日誌）

WAL 是 LSM Tree 實現持久化和 crash recovery 的關鍵元件。在將資料写入 MemTable 之前，系统会先将操作记录到 WAL 中。如果系统崩溃重启，可以從 WAL 恢復尚未刷入磁碟的資料，確保資料不丢失。

WAL 的設計借鑒了關聯式資料庫的事務日誌概念，是 LSM Tree 能夠提供一定程度的持久性保證的基礎。

### 3. SSTable（Sorted String Table，有序字串表）

SSTable 是 LSM Tree 的核心持久化儲存結構。每一個 SSTable 檔案內部的鍵值對都是按鍵排序的，這種有序性使得範圍查詢和二分搜尋成為可能。

SSTable 的典型結構包含：
- **Data Block**：儲存實際的鍵值對，是最小的讀寫單位
- **Index Block**：儲存每個 Data Block 的起始鍵和位置
- **Filter Block**：用於快速判斷一個鍵是否可能存在於某個 SSTable 中
- **Footer**：包含元資料和索引區塊的位置資訊

### 4. Compaction（合併）

Compaction 是 LSM Tree 的核心維護操作。隨著寫入量增加，資料會在多個 SSTable 中重複出現（因為更新和刪除），Compaction 負責合併這些 SSTable，回收空間並維持查詢效能。

常見的 Compaction 策略包括：

**Level Compaction**（LevelDB、RocksDB 採用）：
- 將資料分為多個層級（L0, L1, L2, ...）
- 每層的總大小有上限，是前一層的 N 倍（通常是 10 倍）
- L0 是特殊層，來自 MemTable flush，內的 SSTable 可能鍵範圍重疊
- 從 L1 開始，每層的 SSTable 鍵範圍不重疊
- Compaction 會選擇一個 SSTable，與下一層有鍵範圍重疊的 SSTable 合併

**Size-Tiered Compaction**（Cassandra 採用）：
- 將 SSTable 按大小分組
- 當某個大小的 SSTable 累積到一定數量後，合併成更大的 SSTable
- 優點是空間放大較低，缺點是讀取時可能需要檢查多個 SSTable

## 讀取流程

LSM Tree 的讀取需要檢查多個元件：

1. **先查詢 MemTable**：最新的資料可能在 MemTable 中
2. **查詢 Immutable MemTable**（如果存在的話）
3. **從 L0 開始向下搜尋**：由於較新資料在較上層，需要由新到舊搜尋
4. **找到第一個匹配的鍵值對就返回**：因為較新資料在較上層

這種由上到下的搜尋方式確保了讀取到最新版本的資料，但也意味著讀取可能需要檢查多個層級，在資料結構龐大時可能影響效能。

## 寫入流程

寫入操作是 LSM Tree 的強項：

1. **寫入 WAL**：確保 crash recovery 能力
2. **寫入 MemTable**：記憶體操作，速度極快
3. **返回客戶端**：寫入完成

整個過程是順序的記憶體寫入，沒有隨機 I/O，這是 LSM Tree 寫入效能出色的根本原因。

更新和刪除操作也遵循相同的流程，只是使用特殊的鍵類型（墓碑鍵）來標記資料的過期或刪除。

## 優點

### 寫入效能極佳

LSM Tree 的最大優勢是寫入效能。由於所有寫入都是順序的記憶體操作（或順序的檔案 append），它能夠充分利用現代儲存裝置的效能。對於需要高寫入量的應用（如時序資料庫、日誌系統、物聯網資料收集）來說，LSM Tree 是首選。

### 空間效率

LSM Tree 可以通過 Compaction 回收被覆蓋或刪除的空間，保持較好的空間使用率。而且，通過壓縮技術（如 zstd、zlib），可以進一步減少儲存空間。

### 適合 SSD

LSM Tree 的順序寫入特性與 SSD 的特性完美匹配。對於大量隨機寫入會造成 SSD 磨損和效能下降的問題，LSM Tree 的設計能夠顯著延長 SSD 壽命並保持穩定效能。

## 缺點

### 讀取效能較差

LSM Tree 的主要缺點是讀取效能。為了找到一個鍵，可能需要檢查多個層級的 SSTable，最壞情況下需要讀取所有層級的資料。這種問題稱為「讀取放大」（Read Amplification）。

可以通過以下方式緩解：
- **Bloom Filter**：每個 SSTable 維護一個 Bloom Filter，可以快速判斷某個鍵是否不存在
- **Index Cache**：將 SSTable 的索引緩存在記憶體中
- **減少層級數量**：增加每層大小上限，減少總層級數

### 寫入放大

每次 Compaction 都會讀取多個 SSTable 並寫入新的 SSTable，實際寫入的資料量可能遠大於客戶端寫入的資料量。這種現象稱為「寫入放大」（Write Amplification）。

在大資料量和高頻 Compaction 的場景下，寫入放大會消耗大量的 I/O 頻寬，影響寫入效能和 SSD 壽命。

### 空間放大

由於 Compaction 的延遲性，LSM Tree 在某段時間內可能儲存了多個版本的相同鍵，導致實際使用的空間大於邏輯資料大小。這種現象稱為「空間放大」（Space Amplification）。

## 應用場景

LSM Tree 適用於以下場景：

1. **寫入密集型應用**：日誌收集、事件追蹤、IoT 資料收集、監控時序資料
2. **需要高寫入吞吐量**：大數據分析的前置處理、ETL 流水線
3. **基於 SSD 的儲存系統**：充分發揮 SSD 的順序寫入優勢
4. **需要快速啟動的嵌入式資料庫**：記憶體表的存在使得資料庫可以快速開機

不適合 LSM Tree 的場景：
1. **讀取密集型應用**：需要頻繁進行點查詢的 OLTP 場景
2. **需要很強的即時一致性**： LSM Tree 的最終一致性模型可能不滿足需求
3. **小資料量、隨機讀取為主的場景**：此時 B+ 樹是更好的選擇

## 知名實現

### LevelDB

Google 開源的 LSM Tree 實現，作為 Chrome 的 IndexedDB 的底層引擎而聞名。設計簡單，適用於嵌入式場景。

### RocksDB

Facebook 基於 LevelDB 開發的改良版，引入了 Column Family、事物支援、CDC（Change Data Capture）等企業級功能，廣泛用於各大互聯網公司的儲存系統中。

### Cassandra

Apache Cassandra 是一個分散式 NoSQL 資料庫，使用 LSM Tree 作為其儲存引擎。結合了 LSM Tree 的寫入優勢和分散式架構的擴展性。

### WiredTiger

MongoDB 的預設儲存引擎，同時支援 B 樹和 LSM Tree 兩種模式。WiredTiger 的 LSM Tree 實現特別優化了空間放大問題。

### TitanDB

基於 RocksDB 的圖資料庫儲存引擎，將 LSM Tree 與圖資料模型結合。

## 在 db6 中的應用

db6 專案的 [LsmEngine](../src/engine/lsm.rs) 移植自 lsm5，是專案的三大儲存引擎之一。LSM 引擎特別適合需要高寫入量的場景，例如日誌儲存、事件收集等。通過統一的 StorageEngine trait，db6 的應用可以在不同引擎之間無縫切換，根據場景選擇最適合的儲存引擎。

## 延伸閱讀

- 原始論文：O'Neil, P., Cheng, E., Gawlick, D., & O'Neil, E. (1996). The Log-Structured Merge-Tree (LSM-Tree). Acta Informatica, 33(4), 351-385.
- RocksDB 官方文檔：https://github.com/facebook/rocksdb/wiki
- LevelDB 官方文檔：https://github.com/google/leveldb