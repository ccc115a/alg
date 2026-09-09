use db6::msgq::Msgq;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. 初始化 Msgq 並綁定資料庫（以此範例，純記憶體引擎）
    let msgq = Msgq::new("memory")?;
    
    // 2. 獲取 AsyncPubSub 子系統
    // 該系統自動包裹了 SyncPubSub 來將歷史紀錄寫入資料庫
    // 並同時維持了 tokio broadcast 無阻塞實時推播
    let pubsub = msgq.async_pubsub();
    
    // 3. 訂閱 Channel
    // 建立 2 個訂閱者與各自的 receivers
    let mut rx1 = pubsub.subscribe("news").await?;
    let mut rx2 = pubsub.subscribe("news").await?;
    
    let sub1_handle = tokio::spawn(async move {
        println!("[Subscriber 1] 等待推播...");
        // 透過 tokio broadcast channel，不產生任何資料庫讀取壓力！
        if let Ok(msg) = rx1.recv().await {
            println!("[Subscriber 1] 收到 '{}' 於時間戳 {}", String::from_utf8_lossy(&msg.payload), msg.timestamp);
        }
    });

    let sub2_handle = tokio::spawn(async move {
        println!("[Subscriber 2] 等待推播...");
        if let Ok(msg) = rx2.recv().await {
            println!("[Subscriber 2] 收到 '{}' 於時間戳 {}", String::from_utf8_lossy(&msg.payload), msg.timestamp);
        }
    });
    
    // 給訂閱者掛載事件的時間
    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    
    // 4. 發佈推播
    println!("[Publisher] 送出: 'Breaking News!'");
    // 此動作會先寫入 DB (供 History 使用)，隨後 Push 進 Broadcast
    let msg_id = pubsub.publish("news", b"Breaking News!".to_vec()).await?;
    println!("[Publisher] 已成功發送訊息 ID: {}", msg_id);
    
    sub1_handle.await?;
    sub2_handle.await?;
    
    // 5. 證實與底層 `SyncPubSub` 共同享有的特性功能 (歷史追溯)
    println!("\n[Publisher] 嘗試透過資料庫手動撈回 Channel 的歷史紀錄：");
    let history = pubsub.get_history("news", 10).await?;
    for m in history {
        println!(" - 歷史資料: '{}'", String::from_utf8_lossy(&m.payload));
    }
    
    Ok(())
}
