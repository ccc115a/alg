# msgq/message.md — 訊息結構

## SyncQueueMessage

`SyncQueueMessage` 是訊息佇列系統中傳遞的基本單位，定義了訊息的中繼資料與內容：

```rust
pub struct SyncQueueMessage {
    pub id: String,                // 唯一識別碼
    pub payload: Vec<u8>,           // 訊息內容 (任意二進位)
    pub enqueued_at: u64,           // 入隊時間 (毫秒)
    pub delivery_count: u32,        // 傳遞次數
    pub visibility_timeout: u64,    // 可見性超時
    pub visible_after: u64,         // 何時可見
    pub priority: u8,               // 優先級
    pub metadata: Option<String>,   // 附屬中繼資料
}
```

## ID 生成

使用目前時間戳 (毫秒) + 隨機數：

```rust
let id = format!("{}:{:08x}", now, fastrand::u32(..));
```

這個設計保證了 ID 的全域唯一性與大致有序性。

## 可見性控制

- `is_visible()` — 檢查訊息是否可被消費者讀取
- `visible_after` — 消費者 Nack 後設定為當前時間，使訊息重新可見

## 序列化

使用 `serde` 搭配 `serde_bytes` 處理二進位 payload，確保 JSON/Bincode 等格式都能正確處理。

## 相關資源

- `msgq/sync_queue.md` — 同步佇列
- `msgq/async_queue/queue.md` — 非同步佇列
