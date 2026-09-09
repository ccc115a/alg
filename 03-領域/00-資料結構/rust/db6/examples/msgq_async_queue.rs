use db6::msgq::Msgq;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. 創建綁定到 Memory 或 LSM/BTree 持久化引擎的 Msgq 實例
    let msgq = Msgq::new("memory")?;
    
    // 2. 初始化 AsyncQueue，自動包裝與映射至底層持久化儲存 (SyncQueue)
    let mut producer_queue = msgq.async_queue("tasks");
    // 為了能正確共享同一組 Tokio Notify 事件，必須透過 clone() 分享同一個佇列核心
    let mut consumer_queue = producer_queue.clone();
    
    // 3. 建立消費者任務 (Consumer Task)
    let consumer_handle = tokio::spawn(async move {
        println!("[Consumer] 等待任務中...");
        
        // 由於我們套用了 tokio::sync::Notify，這邊會完美觸發零次輪詢的非阻塞等待
        // 5秒內如果產生新事件，立刻被喚醒並執行
        while let Ok(Some(msg)) = consumer_queue.dequeue(5).await {
            let text = String::from_utf8_lossy(&msg.payload);
            println!("[Consumer] 收到 payload: '{}'", text);
            
            // 重要：處理完畢後切記 Ack 以將事件從佇列與 DB 中抹除
            consumer_queue.ack(&msg.id).await.unwrap();
            
            if text == "quit" {
                break;
            }
        }
        println!("[Consumer] 退出執行緒");
    });
    
    // 4. 建立生產者發送任務
    // 預留點時間讓 Consumer 安裝好 await
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await; 
    
    println!("[Producer] Enqueuing 'hello 1'");
    producer_queue.enqueue(b"hello 1".to_vec(), 30).await?; // 30 是 visibility timeout
    
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
    println!("[Producer] Enqueuing 'hello 2'");
    producer_queue.enqueue(b"hello 2".to_vec(), 30).await?;

    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
    println!("[Producer] Enqueuing 'quit'");
    producer_queue.enqueue(b"quit".to_vec(), 30).await?;
    
    // 5. 等待消費者結束
    consumer_handle.await?;
    println!("程式執行完畢！");
    Ok(())
}
