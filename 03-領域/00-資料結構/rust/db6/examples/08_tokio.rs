//! Example 08: Tokio Integration
//!
//! 展示 Tokio 進階功能：select!, spawn, channels

use tokio::sync::{mpsc, broadcast, Notify};
use std::sync::Arc;

#[tokio::main]
async fn main() {
    println!("=== Example 08: Tokio Integration ===\n");

    // 1. tokio::select! - 多任務監聽
    println!("--- tokio::select! ---");
    let (tx1, mut rx1) = mpsc::channel(32);
    let (tx2, mut rx2) = mpsc::channel(32);

    tokio::spawn(async move {
        tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        tx1.send("from channel 1").await.unwrap();
    });

    tokio::spawn(async move {
        tx2.send("from channel 2").await.unwrap();
    });

    tokio::select! {
        msg = rx1.recv() => {
            println!("Received: {:?}", msg);
        }
        msg = rx2.recv() => {
            println!("Received: {:?}", msg);
        }
    }

    // 2. tokio::spawn - 並發執行
    println!("\n--- tokio::spawn ---");
    let handle1 = tokio::spawn(async {
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        "Task 1 done"
    });
    
    let handle2 = tokio::spawn(async {
        "Task 2 done"
    });

    let result1 = handle1.await.unwrap();
    let result2 = handle2.await.unwrap();
    println!("{} and {}", result1, result2);

    // 3. broadcast channel - PubSub
    println!("\n--- broadcast channel ---");
    let (tx, _rx) = broadcast::channel(16);
    let mut rx1 = tx.subscribe();
    let mut rx2 = tx.subscribe();

    tx.send("Broadcast message 1").unwrap();
    tx.send("Broadcast message 2").unwrap();

    tokio::select! {
        msg = rx1.recv() => println!("Subscriber 1: {:?}", msg),
        msg = rx2.recv() => println!("Subscriber 2: {:?}", msg),
    }

    // 4. Notify - 喚醒機制
    println!("\n--- Notify ---");
    let notify = Arc::new(Notify::new());
    let notify_clone = notify.clone();

    tokio::spawn(async move {
        notify_clone.notified().await;
        println!("Notified!");
    });

    notify.notify_one();

    // 5. RwLock - 並發讀寫
    println!("\n--- RwLock ---");
    let data = Arc::new(tokio::sync::RwLock::new(vec![1, 2, 3]));
    
    // 讀
    {
        let read = data.read().await;
        println!("Read: {:?}", read);
    }
    
    // 寫
    {
        let mut write = data.write().await;
        write.push(4);
        println!("After write: {:?}", write);
    }

    // 6. Semaphore - 並發限制
    println!("\n--- Semaphore ---");
    let semaphore = Arc::new(tokio::sync::Semaphore::new(2));
    
    let s1 = semaphore.clone();
    let s2 = semaphore.clone();
    let s3 = semaphore.clone();

    let h1 = tokio::spawn(async move {
        let _permit = s1.acquire().await.unwrap();
        println!("Task 1 acquired permit");
        tokio::time::sleep(std::time::Duration::from_millis(100)).await;
    });

    let h2 = tokio::spawn(async move {
        let _permit = s2.acquire().await.unwrap();
        println!("Task 2 acquired permit");
    });

    // 這個會等待，因為只有 2 個 permit
    let h3 = tokio::spawn(async move {
        let _permit = s3.acquire().await.unwrap();
        println!("Task 3 acquired permit");
    });

    h1.await.unwrap();
    h2.await.unwrap();
    h3.await.unwrap();

    println!("\n=== Done ===");
}