# msgq/error.md — 錯誤處理

## 統一錯誤型別

訊息佇列模組使用 `thiserror` crate 定義自己的錯誤型別 `MsgqError`：

```rust
#[derive(Error, Debug)]
pub enum MsgqError {
    QueueNotFound(String),
    QueueEmpty,
    MessageNotFound(String),
    MessageInFlight,
    InvalidFormat(String),
    InvalidEngine(String),
    InvalidOperation(String),
    Io(#[from] std::io::Error),
    Db(#[from] DbError),
    Serialization(String),
}
```

## 與底層錯誤的分離

msgq 有自己的錯誤型別，不直接暴露底層 `crate::error::Error`，這是為了：

1. **封裝** — 使用者不需要了解底層引擎的錯誤
2. **語意清晰** — 訊息佇列特有的錯誤 (如 `QueueEmpty`) 更容易理解
3. **轉換自動化** — 使用 `#[from]` 讓底層錯誤自動轉換

## From 轉換

```rust
impl From<crate::error::Error> for MsgqError {
    fn from(e: crate::error::Error) -> Self {
        MsgqError::Db(e)
    }
}

impl From<serde_json::Error> for MsgqError {
    fn from(e: serde_json::Error) -> Self {
        MsgqError::Serialization(e.to_string())
    }
}
```

## 相關資源

- `crate::error` — 全域錯誤型別
- `msgq/sync_queue.md` — 同步佇列的錯誤處理
