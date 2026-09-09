//! Example 07: Async Operations
//!
//! 展示非同步操作：AsyncQueue, AsyncPubSub

#[tokio::main]
async fn main() {
    println!("=== Example 07: Async Operations ===\n");

    // 建立引擎
    let engine = db6::KvEngine::new("memory").unwrap();
    let engine = std::sync::Arc::new(std::sync::RwLock::new(engine));

    // AsyncQueue 範例
    println!("--- AsyncQueue ---");
    let mut queue = db6::msgq::AsyncQueue::new("tasks", engine.clone());

    // 非同步入隊
    let id1 = queue.enqueue(b"task1".to_vec(), 30).await.unwrap();
    let id2 = queue.enqueue(b"task2".to_vec(), 30).await.unwrap();
    let id3 = queue.enqueue(b"task3".to_vec(), 30).await.unwrap();
    println!("Enqueued: {}, {}, {}", id1, id2, id3);
    println!("Queue length: {}", queue.length().await.unwrap());

    // 非同步出隊
    if let Some(msg) = queue.dequeue(0).await.unwrap() {
        println!("Dequeued: {}", String::from_utf8_lossy(&msg.payload));
        queue.ack(&msg.id).await.unwrap();
    }

    // AsyncPubSub 範例
    println!("\n--- AsyncPubSub ---");
    let ps = db6::msgq::AsyncPubSub::new(engine.clone());

    // 訂閱頻道
    let mut rx = ps.subscribe("updates").await.unwrap();
    
    // 發布訊息
    let id = ps.publish("updates", b"Hello async world!".to_vec()).await.unwrap();
    println!("Published: {}", id);

    // 接收訊息（非阻塞）
    match rx.recv().await {
        Ok(msg) => println!("Received: {}", String::from_utf8_lossy(&msg.payload)),
        Err(e) => println!("Receive error: {:?}", e),
    }

    // 歷史訊息
    let _id2 = ps.publish("updates", b"Second message".to_vec()).await.unwrap();
    let history = ps.get_history("updates", 5).await.unwrap();
    println!("History ({} messages):", history.len());
    for msg in history {
        println!("  - {}", String::from_utf8_lossy(&msg.payload));
    }

    // Concurrency Limiter (from common module)
    println!("\n--- Concurrency Limiter ---");
    let limiter = db6::msgq::ConcurrencyLimiter::new(10);
    println!("Initial permits: {}", limiter.available());
    println!("Limit: {}", limiter.limit());

    // 使用者定義結構 + Arc
    #[derive(Debug)]
    struct User {
        name: String,
    }
    let user = std::sync::Arc::new(User { name: "Alice".to_string() });
    let user_clone = user.clone();
    println!("Cloned user: {:?}", user_clone.name);

    println!("\n=== Done ===");
}