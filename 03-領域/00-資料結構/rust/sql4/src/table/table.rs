//! Table：把 Schema + BPlusTree 組合成一個完整的資料表
//!
//! 使用範例：
//! ```rust
//! use sql4::table::schema::{Column, DataType, Schema};
//! use sql4::table::row::{Row, Value};
//! use sql4::table::table::Table;
//! use sql4::pager::storage::MemoryStorage;
//!
//! let schema = Schema::new(vec![
//!     Column::new("id",   DataType::Integer),
//!     Column::new("name", DataType::Text),
//! ]);
//! let mut table = Table::new("users", schema, MemoryStorage::new());
//! table.insert(Row::new(vec![Value::Integer(1), Value::Text("Alice".into())]));
//! ```

use crate::btree::node::Key;
use crate::btree::tree::BPlusTree;
use crate::pager::storage::Storage;
use super::row::{Row, Value};
use super::schema::Schema;
use super::serialize;

pub struct Table<S: Storage> {
    pub name:   String,
    pub schema: Schema,
    tree:       BPlusTree<S>,
}

impl<S: Storage> Table<S> {
    /// 建立全新的資料表
    pub fn new(name: &str, schema: Schema, storage: S) -> Self {
        Table {
            name: name.to_string(),
            schema,
            tree: BPlusTree::new(64, storage), // order=64 適合磁碟頁面
        }
    }

    /// 開啟已有資料表（磁碟後端）
    pub fn open(name: &str, schema: Schema, storage: S, root: usize, size: usize) -> Self {
        Table {
            name: name.to_string(),
            schema,
            tree: BPlusTree::open(64, storage, root, size),
        }
    }

    /// 插入一列；第一個欄位自動作為主鍵
    pub fn insert(&mut self, row: Row) -> Result<(), String> {
        let key = self.row_key(&row)?;
        let bytes = serialize::serialize(&self.schema, &row);
        self.tree.insert(key, bytes);
        Ok(())
    }

    /// 以主鍵查詢單筆資料
    pub fn get(&mut self, key: &Key) -> Option<Row> {
        self.tree
            .search(key)
            .map(|bytes| serialize::deserialize(&self.schema, &bytes))
    }

    /// 範圍查詢 [start, end]
    pub fn range(&mut self, start: &Key, end: &Key) -> Vec<Row> {
        self.tree
            .range_search(start, end)
            .into_iter()
            .map(|record| serialize::deserialize(&self.schema, &record.value))
            .collect()
    }

    /// 刪除一筆資料
    pub fn delete(&mut self, key: &Key) -> bool {
        self.tree.delete(key)
    }

    /// 全表掃描（從最小 key 到最大 key）
    pub fn scan(&mut self) -> Vec<Row> {
        let min_key = Key::Integer(i64::MIN);
        let max_key = Key::Integer(i64::MAX);
        // 對 Text key 的表需要不同範圍，先用 Integer 覆蓋數字主鍵
        self.tree
            .range_search(&min_key, &max_key)
            .into_iter()
            .map(|record| serialize::deserialize(&self.schema, &record.value))
            .collect()
    }

    pub fn len(&self) -> usize { self.tree.len() }
    pub fn is_empty(&self) -> bool { self.tree.is_empty() }
    pub fn root_page(&self) -> usize { self.tree.root_page() }

    pub fn flush(&mut self) { self.tree.flush(); }

    // ------------------------------------------------------------------ //
    //  內部輔助                                                            //
    // ------------------------------------------------------------------ //

    /// 取第一個欄位作為 B+Tree 的 key
    fn row_key(&self, row: &Row) -> Result<Key, String> {
        match row.values.first() {
            Some(Value::Integer(v)) => Ok(Key::Integer(*v)),
            Some(Value::Text(s))    => Ok(Key::Text(s.clone())),
            Some(Value::Null)       => Err("primary key cannot be NULL".to_string()),
            Some(other) => Err(format!("unsupported key type: {}", other)),
            None => Err("row has no values".to_string()),
        }
    }
}
