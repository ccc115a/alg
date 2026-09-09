//! Query Module Example - Fluent Interface
//! 
//! 展示如何使用 Db 進行 KV 和 SQL 操作

use db6::query::Db;

fn main() {
    println!("=== Query Module Example (Fluent Interface) ===\n");

    // 測試 1: Table operations (method chaining)
    println!("--- Table Operations (Method Chaining) ---");
    let mut db = Db::new("memory").unwrap();
    println!("Engine type: {}", db.engine_type());

    db.table("users")
        .put(b"k1", b"value1")
        .unwrap()
        .put(b"k2", b"value2")
        .unwrap()
        .put(b"k3", b"value3")
        .unwrap();

    let val = db.table("users").get(b"k1").unwrap();
    println!("get k1: {:?}", val);

    // Batch put
    db.table("users")
        .batch_put(vec![
            (b"k4".to_vec(), b"value4".to_vec()),
            (b"k5".to_vec(), b"value5".to_vec()),
        ])
        .unwrap();

    let rows = db.table("users").scan(b"", b"").unwrap();
    println!("scan all: {} rows", rows.len());

    // 測試 2: SELECT with method chaining
    println!("\n--- SELECT with Method Chaining ---");
    db.table("users").put(b"1", b"Alice").unwrap();
    db.table("users").put(b"2", b"Bob").unwrap();
    db.table("users").put(b"3", b"Charlie").unwrap();

    let result = db.select("*")
        .from("users")
        .limit(10)
        .execute()
        .unwrap();

    println!("SELECT * FROM users:");
    for row in &result.rows {
        println!("  {:?}", row);
    }

    // 測試 3: BTree with ORDER BY support
    println!("\n--- BTreeMemoryEngine with ORDER BY ---");
    let mut db = Db::new("btree").unwrap();
    
    db.table("users")
        .put(b"c", b"3")
        .unwrap()
        .put(b"a", b"1")
        .unwrap()
        .put(b"b", b"2")
        .unwrap();

    let result = db.select("*")
        .from("users")
        .order_by("key")
        .limit(10)
        .execute()
        .unwrap();

    println!("SELECT * FROM users ORDER BY key:");
    for row in &result.rows {
        println!("  {:?}", row);
    }

    // 測試 4: Persistence
    println!("\n--- Persistence Test ---");
    let temp_dir = std::env::temp_dir().join("db6_query_test");
    let _ = std::fs::remove_dir_all(&temp_dir);
    std::fs::create_dir_all(&temp_dir).unwrap();

    {
        let mut db = Db::open("btree", &temp_dir).unwrap();
        db.table("users").put(b"name", b"Alice").unwrap();
        db.table("users").flush().unwrap();
        println!("Wrote and flushed");
    }

    {
        let mut db = Db::open("btree", &temp_dir).unwrap();
        let name = db.table("users").get(b"name").unwrap();
        println!("After reopen: name={:?}", name);
    }

    let _ = std::fs::remove_dir_all(&temp_dir);

    // 測試 5: Delete operations
    println!("\n--- Delete Operations ---");
    let mut db = Db::new("memory").unwrap();
    db.table("users")
        .put(b"k1", b"v1")
        .unwrap()
        .put(b"k2", b"v2")
        .unwrap();

    println!("Before delete: {} keys", db.table("users").scan(b"", b"").unwrap().len());

    db.table("users").delete(b"k1").unwrap();

    println!("After delete: {} keys", db.table("users").scan(b"", b"").unwrap().len());

    println!("\n=== Done ===");

    // 測試 6: JSON Filter (map / reduce / filter - Functional Programming)
    println!("\n--- JSON Filter (Functional Programming: map / reduce / filter) ---");
    let mut db = Db::new("memory").unwrap();

    // 插入 JSON 資料
    db.table("users")
        .put(b"1", r#"{"name":"Alice","age":30,"city":"Taipei"}"#.as_bytes())
        .unwrap();
    db.table("users")
        .put(b"2", r#"{"name":"Bob","age":25,"city":"Kaohsiung"}"#.as_bytes())
        .unwrap();
    db.table("users")
        .put(b"3", r#"{"name":"Charlie","age":35,"city":"Taipei"}"#.as_bytes())
        .unwrap();
    db.table("users")
        .put(b"4", r#"{"name":"Diana","age":28,"city":"Taichung"}"#.as_bytes())
        .unwrap();

    // Filter: 過濾 JSON 欄位
    println!("\n// Filter: age > 27");
    let result = db.select("*")
        .from("users")
        .filter("$.age > 27")
        .execute()
        .unwrap();
    println!("Users with age > 27:");
    for row in &result.rows {
        println!("  {:?}", row[1]);
    }

    // Filter: 巢狀路徑
    println!("\n// Filter: nested path $.city = 'Taipei'");
    let result = db.select("*")
        .from("users")
        .filter("$.city = 'Taipei'")
        .execute()
        .unwrap();
    println!("Users in Taipei:");
    for row in &result.rows {
        println!("  {:?}", row[1]);
    }

    // Filter: LIKE 模糊匹配
    println!("\n// Filter: name LIKE 'C%'");
    let result = db.select("*")
        .from("users")
        .filter("$.name LIKE 'C%'")
        .execute()
        .unwrap();
    println!("Users with name starting with C:");
    for row in &result.rows {
        println!("  {:?}", row[1]);
    }

    // Filter: where_() 別名（與 filter() 行為相同）
    println!("\n// where_: age < 30 (same as filter)");
    let result = db.select("*")
        .from("users")
        .where_("$.age < 30")
        .execute()
        .unwrap();
    println!("Users with age < 30:");
    for row in &result.rows {
        println!("  {:?}", row[1]);
    }

    // Map: 轉換資料
    println!("\n// Map: transform all names to uppercase");
    let result = db.table("users")
        .map(|k, v| {
            let mut json: serde_json::Value = serde_json::from_slice(v).unwrap();
            if let Some(name) = json["name"].as_str() {
                json["name"] = serde_json::Value::String(name.to_uppercase());
            }
            (k.to_vec(), serde_json::to_string(&json).unwrap().into_bytes())
        })
        .unwrap()
        .execute()
        .unwrap();
    println!("Users with uppercase names:");
    for (k, v) in &result {
        println!("  {}: {:?}", String::from_utf8_lossy(k), String::from_utf8_lossy(v));
    }

    // Reduce: 聚合計數
    println!("\n// Reduce: count users");
    let result = db.table("users")
        .map(|k, v| (k.to_vec(), v.to_vec()))
        .unwrap()
        .reduce(|acc, _, _| {
            let count = if acc.is_empty() {
                0
            } else {
                String::from_utf8_lossy(&acc).parse::<usize>().unwrap_or(0)
            };
            (count + 1).to_string().into_bytes()
        })
        .execute()
        .unwrap();
    if !result.is_empty() {
        let count = String::from_utf8_lossy(&result[0].1).parse::<usize>().unwrap_or(0);
        println!("Total users: {}", count);
    }

    // Combine: Map + Filter + Reduce
    println!("\n// Combine: Filter with AND");
    println!("Count users in Taipei with age > 27:");
    let result = db.select("*")
        .from("users")
        .filter("$.city = 'Taipei' AND $.age > 27")
        .execute()
        .unwrap();
    println!("Filtered count: {}", result.rows.len());
    for row in &result.rows {
        println!("  {:?}", row[1]);
    }

    println!("\n=== Done ===");
}