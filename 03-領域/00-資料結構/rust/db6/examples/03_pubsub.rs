//! Example 03: Pub/Sub Operations
//!
//! 展示發布/訂閱模式：多訂閱者、頻道管理

use db6::msgq::Msgq;

fn main() {
    println!("=== Example 03: Pub/Sub Operations ===\n");

    let msgq = Msgq::new("memory").unwrap();
    let mut pubsub = msgq.pubsub();

    // 訂閱頻道
    println!("Subscribing to channels...");
    pubsub.subscribe("news", "reader1").unwrap();
    pubsub.subscribe("news", "reader2").unwrap();
    pubsub.subscribe("sports", "reader1").unwrap();

    // 發布訊息到 news
    println!("\nPublishing to 'news'...");
    let id1 = pubsub.publish("news", b"Breaking: AI advances!".to_vec()).unwrap();
    println!("  Published: {}", id1);

    // 發布訊息到 sports
    let id2 = pubsub.publish("sports", b"Game started!".to_vec()).unwrap();
    println!("Published to 'sports': {}", id2);

    // reader1 訂閱了 news 和 sports，會收到兩則訊息
    println!("\nReader1 consuming...");
    if let Some(msg) = pubsub.consume("news", "reader1").unwrap() {
        println!("  From news: {}", String::from_utf8_lossy(&msg.payload));
    }
    if let Some(msg) = pubsub.consume("sports", "reader1").unwrap() {
        println!("  From sports: {}", String::from_utf8_lossy(&msg.payload));
    }

    // reader2 只訂閱 news，只會收到 news 訊息
    println!("\nReader2 consuming...");
    if let Some(msg) = pubsub.consume("news", "reader2").unwrap() {
        println!("  From news: {}", String::from_utf8_lossy(&msg.payload));
    }

    // 列出所有頻道
    let channels = pubsub.list_channels().unwrap();
    println!("\nActive channels: {:?}", channels);

    // 取得頻道訊息數
    let count = pubsub.message_count("news").unwrap();
    println!("Messages in 'news': {}", count);

    // 取消訂閱
    println!("\nUnsubscribing reader1 from sports...");
    pubsub.unsubscribe("sports", "reader1").unwrap();

    // 再次發布 sports，reader1 不會收到了
    pubsub.publish("sports", b"Final score: 3-1".to_vec()).unwrap();
    if pubsub.consume("sports", "reader1").unwrap().is_some() {
        println!("  Should not happen!");
    } else {
        println!("  reader1 correctly unsubscribed from sports");
    }

    println!("\n=== Done ===");
}