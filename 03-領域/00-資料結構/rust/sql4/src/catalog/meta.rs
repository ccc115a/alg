//! TableMeta：記錄單張資料表的定義與儲存位置

use crate::table::schema::{Column, DataType, Schema};

/// 資料庫中一張表的完整描述
#[derive(Debug, Clone)]
pub struct TableMeta {
    pub name:      String,
    pub schema:    Schema,
    pub root_page: usize,  // B+Tree 根節點的頁號
    pub row_count: usize,  // 目前的資料筆數
}

impl TableMeta {
    pub fn new(name: &str, schema: Schema, root_page: usize) -> Self {
        TableMeta { name: name.to_string(), schema, root_page, row_count: 0 }
    }
}

// ------------------------------------------------------------------ //
//  TableMeta 序列化（存進系統表）                                      //
// ------------------------------------------------------------------ //
//
// 格式：
//   [0..4]   name_len  : u32
//   [4..]    name      : UTF-8
//   [+0..+4] col_count : u32
//   per column:
//     [0..4]   col_name_len : u32
//     [4..]    col_name     : UTF-8
//     [+0]     data_type    : u8  (0=Int,1=Text,2=Bool,3=Float)
//     [+1]     nullable     : u8  (0/1)
//   [+0..+4]  root_page : u32
//   [+4..+8]  row_count : u32

pub fn encode_meta(meta: &TableMeta) -> Vec<u8> {
    let mut buf = Vec::new();

    // name
    encode_str(&mut buf, &meta.name);

    // columns
    buf.extend_from_slice(&(meta.schema.columns.len() as u32).to_le_bytes());
    for col in &meta.schema.columns {
        encode_str(&mut buf, &col.name);
        buf.push(datatype_tag(&col.data_type));
        buf.push(col.nullable as u8);
    }

    // root_page + row_count
    buf.extend_from_slice(&(meta.root_page as u32).to_le_bytes());
    buf.extend_from_slice(&(meta.row_count  as u32).to_le_bytes());
    buf
}

pub fn decode_meta(bytes: &[u8]) -> TableMeta {
    let mut cur = 0;

    let (name, n) = decode_str(&bytes[cur..]);
    cur += n;

    let col_count = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()) as usize;
    cur += 4;

    let mut columns = Vec::with_capacity(col_count);
    for _ in 0..col_count {
        let (col_name, n) = decode_str(&bytes[cur..]);
        cur += n;
        let dt = tag_datatype(bytes[cur]);
        cur += 1;
        let nullable = bytes[cur] != 0;
        cur += 1;
        let mut col = Column::new(&col_name, dt);
        col.nullable = nullable;
        columns.push(col);
    }

    let root_page = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()) as usize;
    cur += 4;
    let row_count  = u32::from_le_bytes(bytes[cur..cur+4].try_into().unwrap()) as usize;

    TableMeta { name, schema: Schema::new(columns), root_page, row_count }
}

// ---- helpers ----

fn encode_str(buf: &mut Vec<u8>, s: &str) {
    let b = s.as_bytes();
    buf.extend_from_slice(&(b.len() as u32).to_le_bytes());
    buf.extend_from_slice(b);
}

fn decode_str(buf: &[u8]) -> (String, usize) {
    let len = u32::from_le_bytes(buf[0..4].try_into().unwrap()) as usize;
    let s = std::str::from_utf8(&buf[4..4+len]).unwrap().to_string();
    (s, 4 + len)
}

fn datatype_tag(dt: &DataType) -> u8 {
    match dt {
        DataType::Integer => 0,
        DataType::Text    => 1,
        DataType::Boolean => 2,
        DataType::Float   => 3,
    }
}

fn tag_datatype(tag: u8) -> DataType {
    match tag {
        0 => DataType::Integer,
        1 => DataType::Text,
        2 => DataType::Boolean,
        3 => DataType::Float,
        t => panic!("unknown datatype tag: {}", t),
    }
}

// ------------------------------------------------------------------ //
//  測試                                                                //
// ------------------------------------------------------------------ //

#[cfg(test)]
mod tests {
    use super::*;
    use crate::table::schema::{Column, DataType, Schema};

    fn sample_meta() -> TableMeta {
        let schema = Schema::new(vec![
            Column::new("id",   DataType::Integer).not_null(),
            Column::new("name", DataType::Text),
            Column::new("ok",   DataType::Boolean),
        ]);
        let mut meta = TableMeta::new("users", schema, 3);
        meta.row_count = 42;
        meta
    }

    #[test]
    fn roundtrip_meta() {
        let original = sample_meta();
        let bytes = encode_meta(&original);
        let decoded = decode_meta(&bytes);

        assert_eq!(decoded.name, "users");
        assert_eq!(decoded.root_page, 3);
        assert_eq!(decoded.row_count, 42);
        assert_eq!(decoded.schema.columns.len(), 3);
        assert_eq!(decoded.schema.columns[0].name, "id");
        assert_eq!(decoded.schema.columns[0].data_type, DataType::Integer);
        assert!(!decoded.schema.columns[0].nullable);
        assert_eq!(decoded.schema.columns[1].name, "name");
        assert_eq!(decoded.schema.columns[2].data_type, DataType::Boolean);
    }
}
