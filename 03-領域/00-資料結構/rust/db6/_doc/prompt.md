# db6 -- Unified database with pluggable storage engines (Memory/BTree/LSM) KV + SQL + FTS

1. [x] 同時支援 LSM-tree, BTree 與 memory 記憶體模式。
    * 記憶體模式應該用什麼資料結構呢？（以 Page 為單位）
    * LSM-tree 參考 lsm6/
    * Btree 參考 btree6/ 
2. [x] 包含 key-value 的 api 與 sql 的 api
3. [x] 使用 LSM-tree 時，不支援那些不適合 LSM-tree 的 SQL 語法，例如 JOIN。
4. [x] 使用 Btree 時，支援完整的 sqlite 版本的語法。 （參考 sql6/)
5. [x] 支援全文檢索 (參考 sql6/，但是用 kv 介面來當基礎，最後支援 sql6 的全文檢索語法)
6. [x] 記得讓 sql 介面，建立在 kv 的基礎上
    * 可以繼承 KvStore ，加入 SortedStore 這類的類別，然後銜接到 SQL
7. [x] 0.xx 版，先專注 kv ， 1.xx 版，加入 fts 全文檢索， 2.xx 版，加入 sql 。
8. [x] lsm , btree, memory, kv, fts, sql 等模組，必須要能被外部引用並呼叫之
    * 請在 examples/ 下寫出直接使用的範例
    * 強化 lsm 模組（API 完整度，效能，穩定度)
    * 強化 fts 模組（API 完整度，效能，穩定度)
    * 強化 btree 模組（API 完整度，效能，穩定度)
    * 強化 memory 模組（API 完整度，效能，穩定度)
    * 強化後的 lsm , btree, memory, kv, fts, sql 等模組，必須要能被外部引用並呼叫之
    * 請在 examples/ 下寫出直接使用的範例，並寫出 test_examples.sh 測試結果的正確性
* [x] 目前 memory.rs 使用 btree 方式，效能會比較差嗎？如果改成類似 redis 會更快嗎？
    * 是否需要將 memory 分成兩版，一版像是 sqlite memory 支援 sql，另一版像是 redis 支援 kv
* [x] 要讓 kv, sql 前端都可以任意挑選後端 (btree/lsm/memory btree / memory hash) 
    * 但是有些功能 sql 不支援，使用時會提出錯誤（最好在編譯時期就能提出錯誤）
* [x] fts (fulltext) 功能改進
    * fts 應該有一組 API 應該和使用什麼儲存體無關
    * fts 應該能任意搭配 (btree/lsm/memory btree / memory hash)
    * kv api 應該有支援固定的 fts 檢索語法
    * sql api 應該有支援固定的 fts 檢索語法
    * 加入這些功能的 cargo test
    * 寫出 examples/ 中的上述範例。
* [x] 永久儲存於磁碟
    * LSM 現在具備永久儲存於磁碟的功能了嗎？
    * BTree 現在具備永久儲存於磁碟的功能了嗎？
    * BTree + LSM 的這些永久儲存功能，是否是立即性的（而非最後一次性的儲存呢）？
* [x] memory/ 功能，要能使用 mmap 映射到硬碟檔案儲存之。
    * 要測試儲存後，未來重新讀回（mmap 位址更換了），是否還能正常運作
    * 如果不能正常運作，要修正，讓他能正常運作。
* [x] sql 的 fulltext 語法 現在支援了嗎？
    * 讓 SQL 支援 FTS (Full-Text Search) 語法，像 SQLite 一樣。
* redis 的功能，目前有哪些重要卻沒有放入本系統 kv 中的？
* sqlite 的功能，目前有哪些重要卻沒有放入本系統 sql 中的？
* 利用 kv/ ，仿照 redis 加入 message queue 的功能
    * 放在 msgq/ 下
* [x] Fluent Interface	語法風格: query/ 模組
    * 連續點點點（Method Chaining）的設計模式	db.select().where().hidden()
    * sql 語法經常被 mapping 為 Fluent Interface 語法風格
    * kv 的 query ，也能被 db.select().where() 這樣的語法延伸使用。
    * 加入 query/ 模組，擴充 kv ，然後也能讓後端用 btree 支援 order , group 等功能。
    * 把 fts 功能也放入 query/ 中
    * 不需要支援 JOIN 和 Subquery (那個留給 SQL 去做)
    * 要支援 map, reduce 等函數

## 工具呼叫穩定性協議（防止生成中斷）
- 當你透過類似 `<invoke name="edit">` 的方法進行大規模的程式碼修改時，如果預估程式碼內容可能會接近你的單次最大輸出 Token 限制（max output token limit），**請絕對不要嘗試一次發送整塊龐大的程式碼**。
- 相反地，請執行**「分段與心跳（Split-and-Heartbeat）」模式**：將你的修改拆分成多個較小的 `<invoke>` 區塊分批執行。
- 當使用者或終端機介面輸入 `go` 之後，請立刻從剛才在中斷處 `<parameter name="newString">` 內留下的最後一個字元，完全無縫地繼續往下生成。

