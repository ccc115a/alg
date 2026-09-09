# error.rs — 統一錯誤系統

## 為什麼需要統一錯誤型別？

在一個多層次、多模組的資料庫系統中，各層產生的錯誤型別各異：

- 儲存引擎層可能產生 IO 錯誤、資料毀損
- SQL 層可能產生語法錯誤、型別錯誤
- 交易層可能產生死結、衝突

統一錯誤型別 (unified error type) 讓上游呼叫者不需要處理每層各自的錯誤，簡化了錯誤傳播 (error propagation) 邏輯。

## 實作方式

採用 `thiserror` crate 提供的 `#[derive(Error)]` 巨集，自動實作 `std::error::Error` 與 `Display` trait。

```
Error
├── Io(String)            — IO 錯誤
├── KeyNotFound            — 鍵不存在
├── NotSupported(String)   — 不支援的操作
├── Corruption(String)     — 資料毀損
├── TransactionError       — 交易失敗 (含 rollback)
├── Transaction(String)    — 交易相關錯誤
├── InvalidConfig(String)  — 無效設定
├── InvalidEngine(String)  — 無效引擎
├── Sql(String)            — SQL 錯誤
└── Fts(String)            — 全文搜尋錯誤
```

## From 轉換

實作了 `From<std::io::Error>` 讓 `?` 運算子可以自動將標準 IO 錯誤轉換為 `Error::Io`。

## 相關資源

- `lib.rs` — 公開匯出 `Result` 與 `Error`
- `msgq/error.rs` — 訊息佇列專用的錯誤型別
