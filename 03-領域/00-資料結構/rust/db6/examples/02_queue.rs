//! Example 02: Queue Operations
//!
//! 展示訊息佇列操作：入隊、出隊、確認、拒絕

use db6::msgq::Msgq;

fn main() {
    println!("=== Example 02: Queue Operations ===\n");

    // 建立 msgq（使用 memory 引擎）
    let msgq = Msgq::new("memory").unwrap();

    // 建立同步佇列
    let mut queue = msgq.queue("orders");

    // 入隊（Enqueue）
    println!("Enqueue messages...");
    let order1 = r#"{"order_id": 1, "item": "Apple", "qty": 5}"#.as_bytes().to_vec();
    let order2 = r#"{"order_id": 2, "item": "Banana", "qty": 3}"#.as_bytes().to_vec();
    let order3 = r#"{"order_id": 3, "item": "Orange", "qty": 2}"#.as_bytes().to_vec();

    let id1 = queue.enqueue(order1, 30).unwrap();
    let id2 = queue.enqueue(order2, 30).unwrap();
    let id3 = queue.enqueue(order3, 30).unwrap();

    println!("  Added 3 orders: {}, {}, {}", id1, id2, id3);
    println!("  Queue length: {}", queue.length().unwrap());

    // 出隊（Dequeue）
    println!("\nDequeue messages...");
    if let Some(msg) = queue.dequeue(0).unwrap() {
        println!("  Processing: {} (delivery: {})", 
            String::from_utf8_lossy(&msg.payload), 
            msg.delivery_count);
        
        // 確認處理完成
        queue.ack(&msg.id).unwrap();
        println!("  Acknowledged: {}", msg.id);
    }

    // 再次出隊
    if let Some(msg) = queue.dequeue(0).unwrap() {
        println!("  Processing: {}", String::from_utf8_lossy(&msg.payload));
        
        // 拒絕（Nack）- 訊息會重新入隊
        queue.nack(&msg.id).unwrap();
        println!("  Nacked: {}", msg.id);
    }

    // 再次出隊（應該是 Nack 的訊息）
    if let Some(msg) = queue.dequeue(0).unwrap() {
        println!("  Re-delivered: {}", String::from_utf8_lossy(&msg.payload));
        queue.ack(&msg.id).unwrap();
    }

    // 查看剩餘
    println!("\nRemaining in queue: {}", queue.length().unwrap());

    // 偷看（Peek）
    if let Some(msg) = queue.peek().unwrap() {
        println!("Next message (peek): {}", String::from_utf8_lossy(&msg.payload));
    }

    // 清空佇列
    queue.purge().unwrap();
    println!("Queue purged. Length: {}", queue.length().unwrap());

    println!("\n=== Done ===");
}