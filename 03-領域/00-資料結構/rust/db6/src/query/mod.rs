//! High-level query module — Fluent Method Chaining API
//!
//! Provides a jQuery/Linq-style method chaining query interface.
//! Users can chain method calls to build queries without writing SQL directly.
//!
//! ## Usage
//!
//! ```no_run
//! # fn main() -> Result<(), Box<dyn std::error::Error>> {
//! let mut db = db6::Db::new("memory")?;
//!
//! let rows = db.select("name, email")
//!     .from("users")
//!     .filter("age > 18")
//!     .execute()?;
//! # Ok(())
//! # }
//! ```

use std::collections::HashMap;
use std::path::Path;
use crate::engine::StorageEngine;
use crate::error::{Error, Result};
use crate::kv::KvEngine;
use crate::sql::ResultSet;

const INDEX_TABLE_ID: u32 = u32::MAX - 1;

#[derive(Clone)]
struct IndexDef {
    table_id: u32,
    json_path: String,
}

/// Db main entry point
pub struct Db {
    engine: KvEngine,
    table_map: HashMap<String, u32>,
    next_table_id: u32,
    index_defs: HashMap<String, IndexDef>,
}

impl Db {
    /// Create an in-memory database
    pub fn new(engine_type: &str) -> Result<Self> {
        Ok(Db {
            engine: KvEngine::new(engine_type)?,
            table_map: HashMap::new(),
            next_table_id: 1,
            index_defs: HashMap::new(),
        })
    }

    /// Create a persistent database
    pub fn open(engine_type: &str, path: &Path) -> Result<Self> {
        Ok(Db {
            engine: KvEngine::open(engine_type, path)?,
            table_map: HashMap::new(),
            next_table_id: 1,
            index_defs: HashMap::new(),
        })
    }

    fn get_table_id(&mut self, table_name: &str) -> u32 {
        if let Some(id) = self.table_map.get(table_name) {
            return *id;
        }
        let id = self.next_table_id;
        self.next_table_id += 1;
        self.table_map.insert(table_name.to_string(), id);
        id
    }

    /// Table fluent interface
    pub fn table(&mut self, table_name: &str) -> TableQuery<'_> {
        let table_id = self.get_table_id(table_name);
        TableQuery {
            db: self,
            table_name: table_name.to_string(),
            table_id,
        }
    }

    /// SELECT fluent interface
    pub fn select(&mut self, columns: &str) -> SelectQuery<'_> {
        SelectQuery {
            db: Some(self),
            columns: columns.to_string(),
            from: None,
            where_clause: None,
            order_by: None,
            group_by: None,
            having: None,
            limit: None,
            offset: None,
        }
    }

    /// INSERT fluent interface
    pub fn insert(&mut self) -> InsertQuery<'_> {
        InsertQuery {
            db: self,
            into: None,
            columns: None,
            values: vec![],
        }
    }

    /// DELETE fluent interface
    pub fn delete(&mut self) -> DeleteQuery<'_> {
        DeleteQuery {
            db: self,
            from: None,
            where_clause: None,
        }
    }

    /// UPDATE fluent interface
    pub fn update(&mut self, table: &str) -> UpdateQuery<'_> {
        UpdateQuery {
            db: self,
            table: table.to_string(),
            set_value: None,
            where_clause: None,
        }
    }

    /// Transaction fluent interface
    pub fn begin_tx(&mut self) -> TransactionQuery<'_> {
        self.engine.begin_transaction().ok();
        TransactionQuery { db: self }
    }

    /// MapReduce fluent interface
    pub fn map_reduce(&mut self, table_name: &str) -> MapReduceQuery<'_> {
        let table_id = self.get_table_id(table_name);
        MapReduceQuery {
            db: self,
            table_name: table_name.to_string(),
            table_id,
            data: Vec::new(),
            reducer: None,
        }
    }

    pub fn engine_type(&self) -> &'static str {
        self.engine.engine_type()
    }

    pub fn create_index(&mut self, table: &str, json_path: &str) -> Result<()> {
        let table_id = self.get_table_id(table);
        let index_key = format!("{}:{}", table, json_path);

        if self.index_defs.contains_key(&index_key) {
            return Err(Error::Sql(format!("Index on {}.{} already exists", table, json_path)));
        }

        self.index_defs.insert(index_key.clone(), IndexDef {
            table_id,
            json_path: json_path.to_string(),
        });

        let rows = self.engine.scan(table_id, b"", b"")?;
        for (key, value) in rows {
            self.update_index_put(table_id, json_path, &key, &value)?;
        }

        Ok(())
    }

    pub fn drop_index(&mut self, table: &str, json_path: &str) -> Result<()> {
        let index_key = format!("{}:{}", table, json_path);
        let index_def = self.index_defs.remove(&index_key)
            .ok_or_else(|| Error::Sql(format!("Index on {}.{} does not exist", table, json_path)))?;

        let prefix = format!("idx:{}:{}:", index_def.table_id, json_path);
        let prefix_bytes = prefix.as_bytes();
        let mut end = prefix_bytes.to_vec();
        end.push(b'\xFF');

        self.engine.range_delete(INDEX_TABLE_ID, prefix_bytes, &end)?;

        Ok(())
    }

    pub fn indexes(&mut self, table: &str) -> Result<Vec<String>> {
        let table_id = self.get_table_id(table);
        let mut result = Vec::new();
        for (key, def) in &self.index_defs {
            if def.table_id == table_id {
                if let Some(path) = key.strip_prefix(&format!("{}:", table)) {
                    result.push(path.to_string());
                }
            }
        }
        Ok(result)
    }

    fn find_index(&mut self, table_id: u32, json_path: &str) -> Option<&IndexDef> {
        for def in self.index_defs.values() {
            if def.table_id == table_id && def.json_path == json_path {
                return Some(def);
            }
        }
        None
    }

    fn update_index_put(&mut self, table_id: u32, json_path: &str, key: &[u8], value: &[u8]) -> Result<()> {
        let json_str = String::from_utf8_lossy(value);
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&json_str) {
            let path = json_path.trim_start_matches("$.");
            if let Some(field_value) = json_path_get(&json, &format!("$.{}", path)) {
                let field_str = field_value.to_string();
                let index_key = format!("idx:{}:{}:{}:{}", table_id, json_path, field_str, String::from_utf8_lossy(key));
                self.engine.put(INDEX_TABLE_ID, index_key.as_bytes(), b"")?;
            }
        }
        Ok(())
    }

    fn update_index_delete(&mut self, table_id: u32, json_path: &str, key: &[u8], value: &[u8]) -> Result<()> {
        let json_str = String::from_utf8_lossy(value);
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&json_str) {
            let path = json_path.trim_start_matches("$.");
            if let Some(field_value) = json_path_get(&json, &format!("$.{}", path)) {
                let field_str = field_value.to_string();
                let index_key = format!("idx:{}:{}:{}:{}", table_id, json_path, field_str, String::from_utf8_lossy(key));
                self.engine.delete(INDEX_TABLE_ID, index_key.as_bytes())?;
            }
        }
        Ok(())
    }

    fn get_index_keys_for_range(&mut self, table_id: u32, json_path: &str, op: &str, value: &str) -> Result<Vec<Vec<u8>>> {
        let prefix = format!("idx:{}:{}:", table_id, json_path);
        let prefix_bytes = prefix.as_bytes();

        let start: Vec<u8> = if op == ">" || op == ">=" {
            let full_start = if op == ">=" {
                format!("{}{}", prefix, value)
            } else {
                format!("{}{}", prefix, value)
            };
            full_start.into_bytes()
        } else {
            prefix_bytes.to_vec()
        };

        let end: Vec<u8> = if op == "<" || op == "<=" {
            let full_end = format!("{}{}", prefix, value);
            let mut e = full_end.into_bytes();
            e.push(b'\xff');
            e
        } else {
            let mut e = prefix_bytes.to_vec();
            e.push(b'\xff');
            e
        };

        let entries = self.engine.scan(INDEX_TABLE_ID, &start, &end)?;
        let keys: Vec<Vec<u8>> = entries.iter().filter_map(|e| {
            let full_key = String::from_utf8_lossy(&e.0);
            full_key.rsplit(':').next().map(|k| k.as_bytes().to_vec())
        }).collect();

        Ok(keys)
    }
}

/// Transaction fluent interface
pub struct TransactionQuery<'a> {
    db: &'a mut Db,
}

impl<'a> TransactionQuery<'a> {
    pub fn commit(mut self) -> Result<()> {
        self.db.engine.commit_transaction()
    }

    pub fn rollback(mut self) -> Result<()> {
        self.db.engine.rollback_transaction()
    }
}

/// Table fluent interface
pub struct TableQuery<'a> {
    db: &'a mut Db,
    table_name: String,
    table_id: u32,
}

impl<'a> TableQuery<'a> {
    pub fn put(&mut self, key: &[u8], value: &[u8]) -> Result<&mut Self> {
        self.db.engine.put(self.table_id, key, value)?;
        let index_paths: Vec<String> = self.db.index_defs.values()
            .filter(|def| def.table_id == self.table_id)
            .map(|def| def.json_path.clone())
            .collect();
        for json_path in index_paths {
            self.db.update_index_put(self.table_id, &json_path, key, value)?;
        }
        Ok(self)
    }

    pub fn get(&self, key: &[u8]) -> Result<Option<Vec<u8>>> {
        self.db.engine.get(self.table_id, key)
    }

    pub fn scan(&self, start: &[u8], end: &[u8]) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        self.db.engine.scan(self.table_id, start, end)
    }

    pub fn delete(&mut self, key: &[u8]) -> Result<&mut Self> {
        if let Ok(Some(value)) = self.db.engine.get(self.table_id, key) {
            let index_paths: Vec<String> = self.db.index_defs.values()
                .filter(|def| def.table_id == self.table_id)
                .map(|def| def.json_path.clone())
                .collect();
            for json_path in index_paths {
                self.db.update_index_delete(self.table_id, &json_path, key, &value)?;
            }
        }
        self.db.engine.delete(self.table_id, key)?;
        Ok(self)
    }

    pub fn batch_put(&mut self, pairs: Vec<(Vec<u8>, Vec<u8>)>) -> Result<&mut Self> {
        self.db.engine.batch_put(self.table_id, pairs.clone())?;
        let index_paths: Vec<String> = self.db.index_defs.values()
            .filter(|def| def.table_id == self.table_id)
            .map(|def| def.json_path.clone())
            .collect();
        for (key, value) in pairs {
            for json_path in &index_paths {
                self.db.update_index_put(self.table_id, json_path, &key, &value)?;
            }
        }
        Ok(self)
    }

    pub fn range_delete(&mut self, start: &[u8], end: &[u8]) -> Result<&mut Self> {
        self.db.engine.range_delete(self.table_id, start, end)?;
        Ok(self)
    }

    pub fn flush(&mut self) -> Result<()> {
        self.db.engine.flush()
    }

    pub fn table_name(&self) -> &str {
        &self.table_name
    }

    /// Map transformation: apply function to each key-value pair
    /// Returns a MapReduceQuery with the transformed data
    pub fn map<F>(mut self, f: F) -> Result<MapReduceQuery<'a>>
    where
        F: Fn(&[u8], &[u8]) -> (Vec<u8>, Vec<u8>) + Send + Sync + 'static,
    {
        let rows = self.db.engine.scan(self.table_id, b"", b"")?;
        let mapped: Vec<(Vec<u8>, Vec<u8>)> = rows.iter()
            .map(|(k, v)| f(k, v))
            .collect();

        Ok(MapReduceQuery {
            db: self.db,
            table_name: self.table_name,
            table_id: self.table_id,
            data: mapped,
            reducer: None,
        })
    }
}

/// INSERT fluent interface
pub struct InsertQuery<'a> {
    db: &'a mut Db,
    into: Option<String>,
    columns: Option<Vec<String>>,
    values: Vec<(String, String)>,
}

impl<'a> InsertQuery<'a> {
    /// INTO table_name
    pub fn into_table(&mut self, table: &str) -> &mut Self {
        self.into = Some(table.to_string());
        self
    }

    /// Batch values - [(key, value), ...]
    pub fn values(&mut self, values: Vec<(impl Into<String>, impl Into<String>)>) -> &mut Self {
        for (k, v) in values {
            self.values.push((k.into(), v.into()));
        }
        self
    }

    /// Execute INSERT (uses batch_put for efficiency)
    pub fn execute(&mut self) -> Result<usize> {
        let table = self.into.as_ref()
            .ok_or_else(|| Error::Sql("No table specified for INSERT".into()))?;

        let table_id = self.db.get_table_id(table);
        let count = self.values.len();

        let pairs: Vec<(Vec<u8>, Vec<u8>)> = self.values.iter()
            .map(|(k, v)| (k.as_bytes().to_vec(), v.as_bytes().to_vec()))
            .collect();
        self.db.engine.batch_put(table_id, pairs)?;

        Ok(count)
    }
}

/// DELETE fluent interface
pub struct DeleteQuery<'a> {
    db: &'a mut Db,
    from: Option<String>,
    where_clause: Option<String>,
}

impl<'a> DeleteQuery<'a> {
    pub fn from(&mut self, table: &str) -> &mut Self {
        self.from = Some(table.to_string());
        self
    }

    pub fn filter(&mut self, condition: &str) -> &mut Self {
        self.where_clause = Some(condition.to_string());
        self
    }

    pub fn execute(&mut self) -> Result<usize> {
        let table = self.from.as_ref()
            .ok_or_else(|| Error::Sql("No table specified for DELETE".into()))?;

        let table_id = self.db.get_table_id(table);

        let rows = self.db.engine.scan(table_id, b"", b"")?;
        let filtered = match &self.where_clause {
            Some(cond) => filter_rows(self.db, table_id, rows, cond),
            None => rows,
        };

        let count = filtered.len();
        for (key, _) in filtered {
            self.db.engine.delete(table_id, &key)?;
        }

        Ok(count)
    }
}

/// UPDATE fluent interface
pub struct UpdateQuery<'a> {
    db: &'a mut Db,
    table: String,
    set_value: Option<String>,
    where_clause: Option<String>,
}

impl<'a> UpdateQuery<'a> {
    pub fn set_value(&mut self, value: &str) -> &mut Self {
        self.set_value = Some(value.to_string());
        self
    }

    pub fn filter(&mut self, condition: &str) -> &mut Self {
        self.where_clause = Some(condition.to_string());
        self
    }

    pub fn execute(&mut self) -> Result<usize> {
        let table_id = self.db.get_table_id(&self.table);

        let set_value = self.set_value.as_ref()
            .ok_or_else(|| Error::Sql("No SET clause specified for UPDATE".into()))?;

        let rows = self.db.engine.scan(table_id, b"", b"")?;
        let filtered = match &self.where_clause {
            Some(cond) => filter_rows(self.db, table_id, rows, cond),
            None => rows,
        };

        let count = filtered.len();
        for (ref key, _) in filtered {
            self.db.engine.put(table_id, key, set_value.as_bytes())?;
        }

        Ok(count)
    }
}

/// MapReduce fluent interface
/// Design: table("users").map(...).reduce(...).execute()
pub struct MapReduceQuery<'a> {
    db: &'a mut Db,
    table_name: String,
    table_id: u32,
    data: Vec<(Vec<u8>, Vec<u8>)>,
    reducer: Option<Box<dyn FnMut(Vec<u8>, &[u8], &[u8]) -> Vec<u8> + Send + Sync>>,
}

impl<'a> MapReduceQuery<'a> {
    /// Set the reducer function: (accumulator, key, value) -> new_accumulator
    /// The reducer is called for each key-value pair and updates the accumulator
    pub fn reduce<F>(mut self, f: F) -> Self
    where
        F: FnMut(Vec<u8>, &[u8], &[u8]) -> Vec<u8> + Send + Sync + 'static,
    {
        self.reducer = Some(Box::new(f));
        self
    }

    /// Execute the reduce phase and return results
    /// If no reducer is set, returns the mapped data as-is
    pub fn execute(mut self) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
        if let Some(mut reducer) = self.reducer {
            let mut acc: Vec<u8> = Vec::new();
            for (k, v) in &self.data {
                acc = reducer(acc, k, v);
            }
            if !acc.is_empty() {
                return Ok(vec![(b"result".to_vec(), acc)]);
            }
        }

        Ok(self.data)
    }

    /// Execute and return the accumulator value as a string
    pub fn execute_scalar(self) -> Result<String> {
        let result = self.execute()?;
        if result.is_empty() {
            return Ok(String::new());
        }
        Ok(String::from_utf8_lossy(&result[0].1).to_string())
    }
}

/// SELECT fluent interface
pub struct SelectQuery<'a> {
    db: Option<&'a mut Db>,
    columns: String,
    from: Option<String>,
    where_clause: Option<String>,
    order_by: Option<String>,
    group_by: Option<String>,
    having: Option<String>,
    limit: Option<usize>,
    offset: Option<usize>,
}

impl<'a> SelectQuery<'a> {
    pub fn from(&mut self, table: &str) -> &mut Self {
        self.from = Some(table.to_string());
        self
    }

    pub fn filter(&mut self, condition: &str) -> &mut Self {
        self.where_clause = Some(condition.to_string());
        self
    }

    pub fn where_(&mut self, condition: &str) -> &mut Self {
        self.filter(condition)
    }

    pub fn order_by(&mut self, field: &str) -> &mut Self {
        self.order_by = Some(field.to_string());
        self
    }

    pub fn group_by(&mut self, field: &str) -> &mut Self {
        self.group_by = Some(field.to_string());
        self
    }

    pub fn having(&mut self, condition: &str) -> &mut Self {
        self.having = Some(condition.to_string());
        self
    }

    pub fn limit(&mut self, n: usize) -> &mut Self {
        self.limit = Some(n);
        self
    }

    pub fn offset(&mut self, n: usize) -> &mut Self {
        self.offset = Some(n);
        self
    }

    /// Check if engine supports GROUP BY
    fn requires_group_by_capability(&self) -> Result<()> {
        let engine_type = self.db.as_ref()
            .map(|db| db.engine.engine_type())
            .unwrap_or("unknown");

        match engine_type {
            "memory-btree" | "btree" => Ok(()),
            _ => Err(Error::NotSupported(format!(
                "GROUP BY is not supported for {} engine. Use btree or memory-btree engine.",
                engine_type
            ))),
        }
    }

    /// Execute query
    pub fn execute(&mut self) -> Result<ResultSet> {
        if let Some(ref group_field) = self.group_by {
            self.requires_group_by_capability()?;
        }

        let db = match &mut self.db {
            Some(db) => db,
            None => return Err(Error::Sql("DB not available".into())),
        };

        let table_name = self.from.as_ref()
            .ok_or_else(|| Error::Sql("No table specified".into()))?;

        let table_id = db.get_table_id(table_name);

        let mut rows = db.engine.scan(table_id, b"", b"")?;

        if let Some(ref where_cond) = self.where_clause {
            rows = filter_rows(db, table_id, rows, where_cond);
        }

        if let Some(ref group_field) = self.group_by {
            rows = apply_group_by(rows, group_field, &self.columns)?;
        }

        if let Some(ref having_cond) = self.having {
            rows = filter_rows(db, table_id, rows, having_cond);
        }

        if self.order_by.is_some() && db.engine.engine_type() != "memory-hash" {
            rows.sort_by(|a, b| a.0.cmp(&b.0));
        }

        // Apply OFFSET
        if let Some(offset) = self.offset {
            let len = rows.len();
            if offset < len {
                rows = rows[offset..].to_vec();
            } else {
                rows.clear();
            }
        }

        // Apply LIMIT
        if let Some(limit) = self.limit {
            rows.truncate(limit);
        }

        // Build result
        let columns: Vec<String> = if self.columns == "*" {
            vec!["key".to_string(), "value".to_string()]
        } else {
            self.columns.split(',')
                .map(|s| s.trim().to_string())
                .collect()
        };

        let result_rows: Vec<Vec<String>> = rows.iter()
            .map(|(k, v)| {
                if columns.len() == 1 && columns[0] == "key" {
                    vec![String::from_utf8_lossy(k).to_string()]
                } else if columns.len() == 1 && columns[0] == "value" {
                    vec![String::from_utf8_lossy(v).to_string()]
                } else {
                    vec![
                        String::from_utf8_lossy(k).to_string(),
                        String::from_utf8_lossy(v).to_string(),
                    ]
                }
            })
            .collect();

        Ok(ResultSet {
            columns,
            rows: result_rows,
            affected: 0,
        })
    }
}

/// Apply GROUP BY with aggregate functions
fn apply_group_by(rows: Vec<(Vec<u8>, Vec<u8>)>, group_field: &str, columns: &str) -> Result<Vec<(Vec<u8>, Vec<u8>)>> {
    use std::collections::HashMap;

    let mut groups: HashMap<String, Vec<(Vec<u8>, Vec<u8>)>> = HashMap::new();

    for (k, v) in rows {
        let group_key = if group_field == "key" {
            String::from_utf8_lossy(&k).to_string()
        } else {
            String::from_utf8_lossy(&v).to_string()
        };

        groups.entry(group_key).or_insert_with(Vec::new).push((k, v));
    }

    let mut result: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();

    for (group_key, group_rows) in groups {
        // Determine which aggregate function to use based on columns
        let value = if columns.contains("COUNT(*)") || columns.contains("count(*)") {
            group_rows.len().to_string()
        } else if columns.contains("SUM(") || columns.contains("sum(") {
            // Try to sum numeric values
            let sum: f64 = group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .sum();
            sum.to_string()
        } else if columns.contains("AVG(") || columns.contains("avg(") {
            let sum: f64 = group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .sum();
            let count = group_rows.len() as f64;
            if count > 0.0 {
                (sum / count).to_string()
            } else {
                "0".to_string()
            }
        } else if columns.contains("MIN(") || columns.contains("min(") {
            group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .fold(f64::INFINITY, f64::min)
                .to_string()
        } else if columns.contains("MAX(") || columns.contains("max(") {
            group_rows.iter()
                .filter_map(|(_, v)| String::from_utf8_lossy(v).parse::<f64>().ok())
                .fold(f64::NEG_INFINITY, f64::max)
                .to_string()
        } else {
            // Default: return first value in group
            String::from_utf8_lossy(&group_rows[0].1).to_string()
        };

        result.push((group_key.into_bytes(), value.into_bytes()));
    }

    Ok(result)
}

/// Filter rows based on WHERE condition
/// Supports: key = value, key > value, key >= value, key < value, key <= value, key != value, key LIKE pattern
/// Supports AND/OR combinations: "value = Bob AND key > 1" or "value = Bob OR key < 3"
/// Supports JSON path: "$.field > 25" (filters JSON in value column)
fn filter_rows(db: &mut Db, table_id: u32, rows: Vec<(Vec<u8>, Vec<u8>)>, condition: &str) -> Vec<(Vec<u8>, Vec<u8>)> {
    let condition = condition.trim();

    if condition.starts_with("$.") || condition.starts_with("$[") {
        if condition.contains(" AND ") {
            let parts: Vec<&str> = condition.split(" AND ").collect();
            let mut result = rows;
            for part in parts {
                result = filter_json_path_with_index(db, table_id, result, part.trim());
            }
            return result;
        }
        return filter_json_path_with_index(db, table_id, rows, condition);
    }

    let has_and = condition.contains(" AND ");
    let has_or = condition.contains(" OR ");

    if has_and {
        let parts: Vec<&str> = condition.split(" AND ").collect();
        let mut result = rows;
        for part in parts {
            result = filter_single_condition(result, part.trim());
        }
        return result;
    }

    if has_or {
        let parts: Vec<&str> = condition.split(" OR ").collect();
        let mut result: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();
        let mut seen: std::collections::HashSet<Vec<u8>> = std::collections::HashSet::new();
        for part in parts {
            let filtered = filter_single_condition(rows.clone(), part.trim());
            for row in filtered {
                if seen.insert(row.0.clone()) {
                    result.push(row);
                }
            }
        }
        return result;
    }

    filter_single_condition(rows, condition)
}

fn filter_single_condition(rows: Vec<(Vec<u8>, Vec<u8>)>, condition: &str) -> Vec<(Vec<u8>, Vec<u8>)> {
    let condition = condition.trim();

    // Parse condition: "field op value"
    let parts: Vec<&str> = condition.split_whitespace().collect();
    if parts.len() < 3 {
        return rows;
    }

    let field = parts[0];
    let op = parts[1];
    let value_str = parts[2..].join(" ");

    rows.into_iter().filter(|(k, v)| {
        let field_val = if field == "key" {
            String::from_utf8_lossy(k).to_string()
        } else {
            String::from_utf8_lossy(v).to_string()
        };

        match op {
            "=" | "==" => field_val == value_str,
            "!=" => field_val != value_str,
            ">" => field_val > value_str,
            ">=" => field_val >= value_str,
            "<" => field_val < value_str,
            "<=" => field_val <= value_str,
            "LIKE" => {
                let pattern = value_str.trim_matches(|c| c == '\'' || c == '%');
                if pattern.starts_with('%') && pattern.ends_with('%') {
                    field_val.contains(&pattern[1..pattern.len()-1])
                } else if pattern.ends_with('%') {
                    field_val.starts_with(&pattern[..pattern.len()-1])
                } else if pattern.starts_with('%') {
                    field_val.ends_with(&pattern[1..])
                } else {
                    field_val == pattern
                }
            }
            _ => true,
        }
    }).collect()
}

/// Filter rows based on JSON path condition with index support
/// Syntax: "$.field op value" or "$.nested.field op value"
/// Example: "$.age > 25" filters rows where JSON value's age > 25
fn filter_json_path_with_index(db: &mut Db, table_id: u32, rows: Vec<(Vec<u8>, Vec<u8>)>, condition: &str) -> Vec<(Vec<u8>, Vec<u8>)> {
    let condition = condition.trim();

    let (path, op, value_str) = parse_json_condition(condition);
    let clean_value = value_str.trim_matches(|c| c == '\'' || c == '"');

    if let Some(_index_def) = db.find_index(table_id, &path) {
        if matches!(op.as_str(), "=" | ">" | ">=" | "<" | "<=") {
            if let Ok(index_keys) = db.get_index_keys_for_range(table_id, &path, &op, clean_value) {
                if !index_keys.is_empty() {
                    let key_set: std::collections::HashSet<Vec<u8>> = index_keys.iter().cloned().collect();
                    let filtered: Vec<(Vec<u8>, Vec<u8>)> = rows.iter()
                        .filter(|(k, _)| key_set.contains(k))
                        .cloned()
                        .collect();
                    if !filtered.is_empty() {
                        return filtered;
                    }
                }
            }
        }
    }

    rows.into_iter().filter(|(k, v)| {
        let json_str = String::from_utf8_lossy(v);

        let json: serde_json::Value = match serde_json::from_str(&json_str) {
            Ok(j) => j,
            Err(_) => return false,
        };

        let json_value = json_path_get(&json, &path);

        match json_value {
            Some(jv) => {
                let jv_str = jv.to_string();

                let compare_val = clean_value;
                let compare_with = jv_str.trim_matches('"');

                match op.as_str() {
                    "=" | "==" => compare_with == compare_val,
                    "!=" => compare_with != compare_val,
                    ">" => {
                        if let (Ok(a), Ok(b)) = (compare_with.parse::<f64>(), compare_val.parse::<f64>()) {
                            a > b
                        } else {
                            compare_with > compare_val
                        }
                    }
                    ">=" => {
                        if let (Ok(a), Ok(b)) = (compare_with.parse::<f64>(), compare_val.parse::<f64>()) {
                            a >= b
                        } else {
                            compare_with >= compare_val
                        }
                    }
                    "<" => {
                        if let (Ok(a), Ok(b)) = (compare_with.parse::<f64>(), compare_val.parse::<f64>()) {
                            a < b
                        } else {
                            compare_with < compare_val
                        }
                    }
                    "<=" => {
                        if let (Ok(a), Ok(b)) = (compare_with.parse::<f64>(), compare_val.parse::<f64>()) {
                            a <= b
                        } else {
                            compare_with <= compare_val
                        }
                    }
                    "LIKE" => {
                        if compare_val.starts_with('%') && compare_val.ends_with('%') {
                            compare_with.contains(&compare_val[1..compare_val.len()-1])
                        } else if compare_val.ends_with('%') {
                            compare_with.starts_with(&compare_val[..compare_val.len()-1])
                        } else if compare_val.starts_with('%') {
                            compare_with.ends_with(&compare_val[1..])
                        } else {
                            compare_with == compare_val
                        }
                    }
                    _ => false,
                }
            }
            None => false,
        }
    }).collect()
}

/// Parse "$.path op value" into (path, op, value)
fn parse_json_condition(condition: &str) -> (String, String, String) {
    let condition = condition.trim();

    // Find the first whitespace which separates path from operator
    let mut path_end = condition.len();
    let mut in_string = false;
    let mut paren_depth = 0;

    for (i, c) in condition.char_indices() {
        match c {
            '\'' | '"' if !in_string => in_string = true,
            '\'' | '"' if in_string => in_string = false,
            '(' | '[' | '{' if !in_string => paren_depth += 1,
            ')' | ']' | '}' if !in_string && paren_depth > 0 => paren_depth -= 1,
            ' ' | '\t' if !in_string && paren_depth == 0 => {
                path_end = i;
                break;
            }
            _ => {}
        }
    }

    let path = condition[..path_end].to_string();
    let rest = condition[path_end..].trim();

    // Parse operator and value
    let parts: Vec<&str> = rest.split_whitespace().collect();
    if parts.len() < 2 {
        return (path, "=".to_string(), "".to_string());
    }

    let op = parts[0].to_string();
    let value = parts[1..].join(" ");

    (path, op, value)
}

/// Get JSON value at path (e.g., "$.name" or "$.address.city" or "$[0]")
fn json_path_get(json: &serde_json::Value, path: &str) -> Option<serde_json::Value> {
    let path = path.trim();
    let path = path.strip_prefix('$')?;
    let path = path.trim_start_matches('.');

    if path.is_empty() {
        return Some(json.clone());
    }

    let mut current = json;
    let segments: Vec<&str> = path.split('.').collect();

    for (i, segment) in segments.iter().enumerate() {
        let is_last = i == segments.len() - 1;

        // Check for array index like "[0]"
        if let Some(idx_start) = segment.find('[') {
            let field = &segment[..idx_start];
            let rest = &segment[idx_start..];

            if !field.is_empty() {
                if let Some(obj) = current.get(field) {
                    current = obj;
                } else {
                    return None;
                }
            }

            // Parse array index
            for arr_match in rest.match_indices('[') {
                let idx_str = &rest[arr_match.0 + 1..];
                if let Some(idx_end) = idx_str.find(']') {
                    let idx: usize = match idx_str[..idx_end].parse() {
                        Ok(i) => i,
                        Err(_) => return None,
                    };
                    if let Some(arr) = current.as_array() {
                        if idx >= arr.len() {
                            return None;
                        }
                        current = &arr[idx];
                    } else {
                        return None;
                    }
                }
            }
        } else if is_last {
            // Last segment - return the value
            return current.get(segment).cloned();
        } else {
            // Not last segment - descend
            if let Some(next) = current.get(segment) {
                current = next;
            } else {
                return None;
            }
        }
    }

    Some(current.clone())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_db_new() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"key", b"value").unwrap();
        assert_eq!(db.table("users").get(b"key").unwrap(), Some(b"value".to_vec()));
    }

    #[test]
    fn test_table_chaining() {
        let mut db = Db::new("memory").unwrap();
        db.table("users")
            .put(b"k1", b"v1")
            .unwrap()
            .put(b"k2", b"v2")
            .unwrap();
        
        let val = db.table("users").get(b"k1").unwrap();
        assert_eq!(val, Some(b"v1".to_vec()));
    }

    #[test]
    fn test_select() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        
        let result = db.select("*")
            .from("users")
            .limit(10)
            .execute()
            .unwrap();
        
        assert_eq!(result.rows.len(), 2);
    }

    #[test]
    fn test_insert() {
        let mut db = Db::new("memory").unwrap();
        
        let count = db.insert()
            .into_table("users")
            .values(vec![("1", "Alice"), ("2", "Bob")])
            .execute()
            .unwrap();
        
        assert_eq!(count, 2);
        assert_eq!(db.table("users").get(b"1").unwrap(), Some(b"Alice".to_vec()));
    }

    #[test]
    fn test_where() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // WHERE value = Bob
        let result = db.select("key, value")
            .from("users")
            .filter("value = Bob")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][1], "Bob");
    }

    #[test]
    fn test_delete() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // DELETE where value = Bob
        let count = db.delete()
            .from("users")
            .filter("value = Bob")
            .execute()
            .unwrap();

        assert_eq!(count, 1);
        assert_eq!(db.table("users").get(b"2").unwrap(), None);
        assert_eq!(db.table("users").get(b"1").unwrap(), Some(b"Alice".to_vec()));
    }

    #[test]
    fn test_update() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // UPDATE users SET value = "Robert" where value = "Bob"
        let count = db.update("users")
            .set_value("Robert")
            .filter("value = Bob")
            .execute()
            .unwrap();

        assert_eq!(count, 1);
        // Now row with key="2" has value="Robert"
        assert_eq!(db.table("users").get(b"2").unwrap(), Some(b"Robert".to_vec()));
    }

    #[test]
    fn test_transaction_commit() {
        let temp_dir = std::env::temp_dir().join("db6_tx_test");
        let _ = std::fs::remove_dir_all(&temp_dir);

        let mut db = Db::open("lsm", &temp_dir).unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();

        db.begin_tx()
            .commit()
            .unwrap();

        assert_eq!(db.table("users").get(b"1").unwrap(), Some(b"Alice".to_vec()));

        let _ = std::fs::remove_dir_all(&temp_dir);
    }

    #[test]
    fn test_transaction_rollback() {
        let temp_dir = std::env::temp_dir().join("db6_tx_test2");
        let _ = std::fs::remove_dir_all(&temp_dir);

        let mut db = Db::open("lsm", &temp_dir).unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();

        db.begin_tx()
            .rollback()
            .unwrap();

        // After rollback, all data should still exist
        assert_eq!(db.table("users").get(b"2").unwrap(), Some(b"Bob".to_vec()));

        let _ = std::fs::remove_dir_all(&temp_dir);
    }

    #[test]
    fn test_where_and() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // WHERE key = 2 AND value = Bob
        let result = db.select("key, value")
            .from("users")
            .filter("key = 2 AND value = Bob")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "2");
        assert_eq!(result.rows[0][1], "Bob");
    }

    #[test]
    fn test_where_or() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // WHERE key = 1 OR value = Charlie
        let result = db.select("key, value")
            .from("users")
            .filter("key = 1 OR value = Charlie")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 2);
        let keys: Vec<&str> = result.rows.iter().map(|r| r[0].as_str()).collect();
        assert!(keys.contains(&"1"));
        assert!(keys.contains(&"3"));
    }

    #[test]
    fn test_group_by_basic() {
        let mut db = Db::new("btree").unwrap();
        // Simulate grouped data - multiple rows with same "group" value stored as value
        db.table("users").put(b"1", b"10").unwrap();
        db.table("users").put(b"2", b"20").unwrap();
        db.table("users").put(b"3", b"10").unwrap();
        db.table("users").put(b"4", b"20").unwrap();
        db.table("users").put(b"5", b"10").unwrap();

        // GROUP BY value - count occurrences
        let result = db.select("COUNT(*), value")
            .from("users")
            .group_by("value")
            .execute()
            .unwrap();

        // Should have 2 groups: value=10 (count 3) and value=20 (count 2)
        assert_eq!(result.rows.len(), 2);
    }

    #[test]
    fn test_group_by_not_supported_on_memory() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();

        let result = db.select("COUNT(*), value")
            .from("users")
            .group_by("value")
            .execute();

        assert!(result.is_err());
        let err = result.unwrap_err();
        assert!(err.to_string().contains("GROUP BY is not supported"));
    }

    #[test]
    fn test_having() {
        let mut db = Db::new("btree").unwrap();
        db.table("users").put(b"1", b"10").unwrap();
        db.table("users").put(b"2", b"20").unwrap();
        db.table("users").put(b"3", b"10").unwrap();
        db.table("users").put(b"4", b"20").unwrap();
        db.table("users").put(b"5", b"10").unwrap();
        db.table("users").put(b"6", b"30").unwrap();

        // GROUP BY value with HAVING COUNT(*) > 2
        let result = db.select("COUNT(*), value")
            .from("users")
            .group_by("value")
            .having("COUNT(*) > 2")
            .execute()
            .unwrap();

        // Should only have value=10 (count 3 > 2), value=20 (count 2 not > 2), value=30 (count 1)
        assert_eq!(result.rows.len(), 1);
        // result.rows[0][0] is the grouped value (key)
        assert_eq!(result.rows[0][0], "10"); // only value=10 has count > 2
    }

    #[test]
    fn test_offset() {
        let mut db = Db::new("btree").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();
        db.table("users").put(b"4", b"David").unwrap();

        // Skip first 2 rows with OFFSET 2
        let result = db.select("key, value")
            .from("users")
            .order_by("key")
            .limit(10)
            .offset(2)
            .execute()
            .unwrap();

        // Should have 2 rows (key=3 and key=4)
        assert_eq!(result.rows.len(), 2);
        assert_eq!(result.rows[0][0], "3");
        assert_eq!(result.rows[1][0], "4");
    }

    #[test]
    fn test_limit_offset_pagination() {
        let mut db = Db::new("btree-mem").unwrap();
        for i in 1..=10 {
            db.table("users").put(format!("{:03}", i).as_bytes(), format!("User{}", i).as_bytes()).unwrap();
        }
        let page1 = db.select("key, value")
            .from("users")
            .order_by("key")
            .limit(3)
            .offset(0)
            .execute()
            .unwrap();
        assert_eq!(page1.rows.len(), 3);
        assert_eq!(page1.rows[0][0], "001");
        assert_eq!(page1.rows[1][0], "002");
        assert_eq!(page1.rows[2][0], "003");

        let page2 = db.select("key, value")
            .from("users")
            .order_by("key")
            .limit(3)
            .offset(3)
            .execute()
            .unwrap();
        assert_eq!(page2.rows.len(), 3);
        assert_eq!(page2.rows[0][0], "004");
        assert_eq!(page2.rows[1][0], "005");
        assert_eq!(page2.rows[2][0], "006");

        let page3 = db.select("key, value")
            .from("users")
            .order_by("key")
            .limit(3)
            .offset(6)
            .execute()
            .unwrap();
        assert_eq!(page3.rows.len(), 3);
        assert_eq!(page3.rows[0][0], "007");
        assert_eq!(page3.rows[1][0], "008");
        assert_eq!(page3.rows[2][0], "009");
    }

    #[test]
    fn test_map_reduce_basic() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // Map: transform all values to uppercase
        let result = db.table("users")
            .map(|k, v| (k.to_vec(), String::from_utf8_lossy(v).to_uppercase().into_bytes()))
            .unwrap()
            .reduce(|acc, k, v| {
                let mut r = acc;
                if !r.is_empty() { r.push(b','); }
                r.extend_from_slice(v);
                r
            })
            .execute()
            .unwrap();

        assert_eq!(result.len(), 1);
        let values = String::from_utf8_lossy(&result[0].1);
        assert!(values.contains("ALICE"));
        assert!(values.contains("BOB"));
        assert!(values.contains("CHARLIE"));
    }

    #[test]
    fn test_map_reduce_count() {
        let mut db = Db::new("memory").unwrap();
        for i in 1..=5 {
            db.table("users").put(format!("{}", i).as_bytes(), format!("User{}", i).as_bytes()).unwrap();
        }

        // Count the number of entries
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

        assert_eq!(result.len(), 1);
        let count = String::from_utf8_lossy(&result[0].1).parse::<usize>().unwrap();
        assert_eq!(count, 5);
    }

    #[test]
    fn test_map_reduce_sum() {
        let mut db = Db::new("memory").unwrap();
        db.table("numbers").put(b"a", b"10").unwrap();
        db.table("numbers").put(b"b", b"20").unwrap();
        db.table("numbers").put(b"c", b"30").unwrap();

        // Sum all values
        let result = db.table("numbers")
            .map(|k, v| (k.to_vec(), v.to_vec()))
            .unwrap()
            .reduce(|acc, _, v| {
                let sum: i32 = if acc.is_empty() {
                    0
                } else {
                    String::from_utf8_lossy(&acc).parse().unwrap_or(0)
                };
                let val: i32 = String::from_utf8_lossy(v).parse().unwrap_or(0);
                (sum + val).to_string().into_bytes()
            })
            .execute()
            .unwrap();

        assert_eq!(result.len(), 1);
        let sum = String::from_utf8_lossy(&result[0].1).parse::<i32>().unwrap();
        assert_eq!(sum, 60);
    }

    #[test]
    fn test_map_reduce_filter() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();
        db.table("users").put(b"3", b"Charlie").unwrap();

        // Filter: keep only names starting with 'A'
        let result = db.table("users")
            .map(|k, v| {
                let name = String::from_utf8_lossy(v);
                if name.starts_with('A') {
                    (k.to_vec(), v.to_vec())
                } else {
                    (b"".to_vec(), b"".to_vec())
                }
            })
            .unwrap()
            .reduce(|acc, k, v| {
                if k.is_empty() { return acc; }
                let mut r = acc;
                if !r.is_empty() { r.push(b','); }
                r.extend_from_slice(v);
                r
            })
            .execute()
            .unwrap();

        assert_eq!(result.len(), 1);
        assert_eq!(String::from_utf8_lossy(&result[0].1), "Alice");
    }

    #[test]
    fn test_map_reduce_identity() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", b"Alice").unwrap();
        db.table("users").put(b"2", b"Bob").unwrap();

        // Just map with identity function, no reduce
        let result = db.table("users")
            .map(|k, v| (k.to_vec(), v.to_vec()))
            .unwrap()
            .execute()
            .unwrap();

        assert_eq!(result.len(), 2);
    }

    #[test]
    fn test_json_path_numeric() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob","age":25}"#.as_bytes()).unwrap();
        db.table("users").put(b"3", r#"{"name":"Charlie","age":35}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.age > 25")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 2);
    }

    #[test]
    fn test_json_path_string() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice"}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob"}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.name = 'Alice'")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "1");
    }

    #[test]
    fn test_json_path_nested() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", r#"{"address":{"city":"Taipei"}}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"address":{"city":"Kaohsiung"}}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.address.city = 'Taipei'")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "1");
    }

    #[test]
    fn test_json_path_like() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice"}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Andrew"}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.name LIKE 'Ali%'")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "1");
    }

    #[test]
    fn test_json_path_not_equal() {
        let mut db = Db::new("memory").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice","active":true}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob","active":false}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.active != false")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "1");
    }

    #[test]
    fn test_index_basic() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();

        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob","age":25}"#.as_bytes()).unwrap();
        db.table("users").put(b"3", r#"{"name":"Charlie","age":35}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.age > 27")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 2);
    }

    #[test]
    fn test_index_on_drop() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();

        db.table("users").delete(b"1").unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.age > 25")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 0);
    }

    #[test]
    fn test_index_list() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();
        db.create_index("users", "city").unwrap();

        let indexes = db.indexes("users").unwrap();
        assert_eq!(indexes.len(), 2);
        assert!(indexes.contains(&"age".to_string()));
        assert!(indexes.contains(&"city".to_string()));
    }

    #[test]
    fn test_index_multiple() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();
        db.create_index("users", "name").unwrap();

        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob","age":25}"#.as_bytes()).unwrap();
        db.table("users").put(b"3", r#"{"name":"Charlie","age":35}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.name = 'Alice'")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 1);
        assert_eq!(result.rows[0][0], "1");
    }

    #[test]
    fn test_index_with_equal_condition() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();

        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();
        db.table("users").put(b"2", r#"{"name":"Bob","age":25}"#.as_bytes()).unwrap();
        db.table("users").put(b"3", r#"{"name":"Charlie","age":30}"#.as_bytes()).unwrap();

        let result = db.select("*")
            .from("users")
            .filter("$.age = 30")
            .execute()
            .unwrap();

        assert_eq!(result.rows.len(), 2);
    }

    #[test]
    fn test_drop_index() {
        let mut db = Db::new("btree").unwrap();

        db.create_index("users", "age").unwrap();
        db.table("users").put(b"1", r#"{"name":"Alice","age":30}"#.as_bytes()).unwrap();

        db.drop_index("users", "age").unwrap();

        let indexes = db.indexes("users").unwrap();
        assert!(indexes.is_empty());
    }
}