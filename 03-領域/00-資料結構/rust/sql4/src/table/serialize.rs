//! Row ↔ Vec<u8> 序列化
//!
//! 每個欄位的二進位格式：
//!
//! ```text
//! [0]     tag : u8
//!           0 = Null
//!           1 = Integer  → [1..9]  i64 le
//!           2 = Text     → [1..5]  len: u32, [5..] UTF-8
//!           3 = Boolean  → [1]     0/1
//!           4 = Float    → [1..9]  f64 le (IEEE 754)
//! ```

use super::row::{Row, Value};
use super::schema::Schema;

// ------------------------------------------------------------------ //
//  序列化                                                              //
// ------------------------------------------------------------------ //

pub fn serialize(schema: &Schema, row: &Row) -> Vec<u8> {
    assert_eq!(
        schema.len(), row.values.len(),
        "column count mismatch: schema has {}, row has {}",
        schema.len(), row.values.len()
    );

    let mut buf = Vec::new();
    for value in &row.values {
        encode_value(&mut buf, value);
    }
    buf
}

fn encode_value(buf: &mut Vec<u8>, value: &Value) {
    match value {
        Value::Null => {
            buf.push(0u8);
        }
        Value::Integer(v) => {
            buf.push(1u8);
            buf.extend_from_slice(&v.to_le_bytes());
        }
        Value::Text(s) => {
            buf.push(2u8);
            let bytes = s.as_bytes();
            buf.extend_from_slice(&(bytes.len() as u32).to_le_bytes());
            buf.extend_from_slice(bytes);
        }
        Value::Boolean(b) => {
            buf.push(3u8);
            buf.push(if *b { 1u8 } else { 0u8 });
        }
        Value::Float(v) => {
            buf.push(4u8);
            buf.extend_from_slice(&v.to_le_bytes());
        }
    }
}

// ------------------------------------------------------------------ //
//  反序列化                                                            //
// ------------------------------------------------------------------ //

pub fn deserialize(schema: &Schema, bytes: &[u8]) -> Row {
    let mut cur = 0usize;
    let mut values = Vec::with_capacity(schema.len());

    for _ in &schema.columns {
        let (value, consumed) = decode_value(&bytes[cur..]);
        values.push(value);
        cur += consumed;
    }

    Row::new(values)
}

fn decode_value(buf: &[u8]) -> (Value, usize) {
    match buf[0] {
        0 => (Value::Null, 1),
        1 => {
            let v = i64::from_le_bytes(buf[1..9].try_into().unwrap());
            (Value::Integer(v), 9)
        }
        2 => {
            let len = u32::from_le_bytes(buf[1..5].try_into().unwrap()) as usize;
            let s = std::str::from_utf8(&buf[5..5 + len]).unwrap().to_string();
            (Value::Text(s), 5 + len)
        }
        3 => (Value::Boolean(buf[1] != 0), 2),
        4 => {
            let v = f64::from_le_bytes(buf[1..9].try_into().unwrap());
            (Value::Float(v), 9)
        }
        tag => panic!("unknown value tag: {}", tag),
    }
}

// ------------------------------------------------------------------ //
//  測試                                                                //
// ------------------------------------------------------------------ //

#[cfg(test)]
mod tests {
    use super::*;
    use crate::table::schema::{Column, DataType, Schema};

    fn make_schema() -> Schema {
        Schema::new(vec![
            Column::new("id",     DataType::Integer),
            Column::new("name",   DataType::Text),
            Column::new("active", DataType::Boolean),
            Column::new("score",  DataType::Float),
        ])
    }

    #[test]
    fn roundtrip_all_types() {
        let schema = make_schema();
        let row = Row::new(vec![
            Value::Integer(42),
            Value::Text("Alice".into()),
            Value::Boolean(true),
            Value::Float(3.14),
        ]);
        let bytes = serialize(&schema, &row);
        let back  = deserialize(&schema, &bytes);

        assert_eq!(back.values[0], Value::Integer(42));
        assert_eq!(back.values[1], Value::Text("Alice".into()));
        assert_eq!(back.values[2], Value::Boolean(true));
        assert_eq!(back.values[3], Value::Float(3.14));
    }

    #[test]
    fn roundtrip_null() {
        let schema = Schema::new(vec![
            Column::new("a", DataType::Integer),
            Column::new("b", DataType::Text),
        ]);
        let row = Row::new(vec![Value::Null, Value::Null]);
        let bytes = serialize(&schema, &row);
        let back  = deserialize(&schema, &bytes);
        assert_eq!(back.values[0], Value::Null);
        assert_eq!(back.values[1], Value::Null);
    }

    #[test]
    fn roundtrip_unicode_text() {
        let schema = Schema::new(vec![Column::new("s", DataType::Text)]);
        let row = Row::new(vec![Value::Text("你好世界 🌏".into())]);
        let bytes = serialize(&schema, &row);
        let back  = deserialize(&schema, &bytes);
        assert_eq!(back.values[0], Value::Text("你好世界 🌏".into()));
    }

    #[test]
    fn row_get_by_name() {
        let schema = make_schema();
        let row = Row::new(vec![
            Value::Integer(1),
            Value::Text("Bob".into()),
            Value::Boolean(false),
            Value::Float(9.9),
        ]);
        assert_eq!(row.get_by_name(&schema, "name"), Some(&Value::Text("Bob".into())));
        assert_eq!(row.get_by_name(&schema, "missing"), None);
    }
}
