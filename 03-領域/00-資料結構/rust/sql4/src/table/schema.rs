//! Schema：定義表格的欄位結構

/// 支援的欄位型別
#[derive(Debug, Clone, PartialEq)]
pub enum DataType {
    Integer,  // i64
    Text,     // UTF-8 字串
    Boolean,  // bool
    Float,    // f64
}

impl std::fmt::Display for DataType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DataType::Integer => write!(f, "INTEGER"),
            DataType::Text    => write!(f, "TEXT"),
            DataType::Boolean => write!(f, "BOOLEAN"),
            DataType::Float   => write!(f, "FLOAT"),
        }
    }
}

/// 單一欄位定義
#[derive(Debug, Clone)]
pub struct Column {
    pub name:     String,
    pub data_type: DataType,
    pub nullable: bool,
}

impl Column {
    pub fn new(name: &str, data_type: DataType) -> Self {
        Column { name: name.to_string(), data_type, nullable: true }
    }

    pub fn not_null(mut self) -> Self {
        self.nullable = false;
        self
    }
}

/// 表格 Schema：由多個 Column 組成
#[derive(Debug, Clone)]
pub struct Schema {
    pub columns: Vec<Column>,
}

impl Schema {
    pub fn new(columns: Vec<Column>) -> Self {
        Schema { columns }
    }

    /// 根據欄位名稱找索引
    pub fn index_of(&self, name: &str) -> Option<usize> {
        self.columns.iter().position(|c| c.name == name)
    }

    pub fn len(&self) -> usize {
        self.columns.len()
    }
}
