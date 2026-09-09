//! Row：一筆資料列，由多個 Value 組成

use super::schema::Schema;

/// 單一欄位的值
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Integer(i64),
    Text(String),
    Boolean(bool),
    Float(f64),
    Null,
}

impl std::fmt::Display for Value {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Value::Integer(v) => write!(f, "{}", v),
            Value::Text(s)    => write!(f, "{}", s),
            Value::Boolean(b) => write!(f, "{}", b),
            Value::Float(v)   => write!(f, "{}", v),
            Value::Null       => write!(f, "NULL"),
        }
    }
}

/// 一筆資料列
#[derive(Debug, Clone)]
pub struct Row {
    pub values: Vec<Value>,
}

impl Row {
    pub fn new(values: Vec<Value>) -> Self {
        Row { values }
    }

    /// 以欄位名稱取值（需要 schema 對應）
    pub fn get_by_name<'a>(&'a self, schema: &Schema, name: &str) -> Option<&'a Value> {
        schema.index_of(name).map(|i| &self.values[i])
    }

    /// 以欄位索引取值
    pub fn get(&self, idx: usize) -> Option<&Value> {
        self.values.get(idx)
    }

    /// 印出一列（以 | 分隔）
    pub fn display(&self, schema: &Schema) -> String {
        self.values
            .iter()
            .enumerate()
            .map(|(i, v)| format!("{}: {}", schema.columns[i].name, v))
            .collect::<Vec<_>>()
            .join(" | ")
    }
}
