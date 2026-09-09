//! Node ↔ 位元組序列化（codec）
//!
//! 頁面格式（固定 PAGE_SIZE = 4096 bytes）：

use crate::node::{Key, Node, NodeType, Record};

pub const PAGE_SIZE: usize = 4096;
const NONE_PAGE: u32 = 0xFFFF_FFFF;

pub fn encode_node(node: &Node) -> Vec<u8> {
    let mut buf = Vec::with_capacity(PAGE_SIZE);

    buf.push(match node.node_type {
        NodeType::Internal => 0u8,
        NodeType::Leaf => 1u8,
    });

    let key_count = node.keys.len() as u32;
    buf.extend_from_slice(&key_count.to_le_bytes());

    let next = node.next_leaf.map(|v| v as u32).unwrap_or(NONE_PAGE);
    buf.extend_from_slice(&next.to_le_bytes());

    for key in &node.keys {
        encode_key(&mut buf, key);
    }

    if node.is_leaf() {
        for record in &node.records {
            encode_bytes(&mut buf, &record.value);
        }
    } else {
        for child in &node.children {
            buf.extend_from_slice(&(*child as u32).to_le_bytes());
        }
    }

    buf.resize(PAGE_SIZE, 0);
    buf
}

fn encode_key(buf: &mut Vec<u8>, key: &Key) {
    match key {
        Key::Integer(v) => {
            buf.push(0u8);
            buf.extend_from_slice(&v.to_le_bytes());
        }
        Key::Text(s) => {
            buf.push(1u8);
            let bytes = s.as_bytes();
            buf.extend_from_slice(&(bytes.len() as u32).to_le_bytes());
            buf.extend_from_slice(bytes);
        }
    }
}

fn encode_bytes(buf: &mut Vec<u8>, data: &[u8]) {
    buf.extend_from_slice(&(data.len() as u32).to_le_bytes());
    buf.extend_from_slice(data);
}

pub fn decode_node(page: &[u8]) -> Node {
    let mut cur = 0usize;

    let node_type = match page[cur] {
        0 => NodeType::Internal,
        _ => NodeType::Leaf,
    };
    cur += 1;

    let key_count = u32::from_le_bytes(page[cur..cur + 4].try_into().unwrap()) as usize;
    cur += 4;

    let next_raw = u32::from_le_bytes(page[cur..cur + 4].try_into().unwrap());
    let next_leaf = if next_raw == NONE_PAGE {
        None
    } else {
        Some(next_raw as usize)
    };
    cur += 4;

    let mut keys = Vec::with_capacity(key_count);
    for _ in 0..key_count {
        let (key, consumed) = decode_key(&page[cur..]);
        keys.push(key);
        cur += consumed;
    }

    let mut records = Vec::new();
    let mut children = Vec::new();

    if node_type == NodeType::Leaf {
        for i in 0..key_count {
            let (value, consumed) = decode_bytes(&page[cur..]);
            records.push(Record {
                key: keys[i].clone(),
                value,
            });
            cur += consumed;
        }
    } else {
        let child_count = key_count + 1;
        for _ in 0..child_count {
            let child = u32::from_le_bytes(page[cur..cur + 4].try_into().unwrap()) as usize;
            children.push(child);
            cur += 4;
        }
    }

    Node {
        node_type,
        keys,
        children,
        records,
        next_leaf,
    }
}

fn decode_key(buf: &[u8]) -> (Key, usize) {
    match buf[0] {
        0 => {
            let v = i64::from_le_bytes(buf[1..9].try_into().unwrap());
            (Key::Integer(v), 9)
        }
        _ => {
            let len = u32::from_le_bytes(buf[1..5].try_into().unwrap()) as usize;
            let s = std::str::from_utf8(&buf[5..5 + len]).unwrap().to_string();
            (Key::Text(s), 5 + len)
        }
    }
}

fn decode_bytes(buf: &[u8]) -> (Vec<u8>, usize) {
    let len = u32::from_le_bytes(buf[0..4].try_into().unwrap()) as usize;
    (buf[4..4 + len].to_vec(), 4 + len)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_leaf(pairs: &[(&str, &str)]) -> Node {
        let mut node = Node::new_leaf();
        for (k, v) in pairs {
            node.keys.push(Key::Text(k.to_string()));
            node.records.push(Record {
                key: Key::Text(k.to_string()),
                value: v.as_bytes().to_vec(),
            });
        }
        node
    }

    fn make_internal(keys: &[i64], children: &[usize]) -> Node {
        let mut node = Node::new_internal();
        node.keys = keys.iter().map(|&k| Key::Integer(k)).collect();
        node.children = children.to_vec();
        node
    }

    #[test]
    fn roundtrip_leaf_text() {
        let original = make_leaf(&[("apple", "fruit"), ("banana", "also fruit")]);
        let page = encode_node(&original);
        assert_eq!(page.len(), PAGE_SIZE);
        let decoded = decode_node(&page);
        assert!(decoded.is_leaf());
        assert_eq!(decoded.keys, original.keys);
        assert_eq!(decoded.records[0].value, b"fruit");
        assert_eq!(decoded.records[1].value, b"also fruit");
    }

    #[test]
    fn roundtrip_leaf_integer() {
        let mut node = Node::new_leaf();
        node.keys = vec![Key::Integer(1), Key::Integer(2)];
        node.records = vec![
            Record { key: Key::Integer(1), value: b"one".to_vec() },
            Record { key: Key::Integer(2), value: b"two".to_vec() },
        ];
        node.next_leaf = Some(7);

        let page = encode_node(&node);
        let decoded = decode_node(&page);
        assert_eq!(decoded.next_leaf, Some(7));
        assert_eq!(decoded.keys, node.keys);
    }

    #[test]
    fn roundtrip_internal() {
        let original = make_internal(&[10, 20], &[0, 1, 2]);
        let page = encode_node(&original);
        let decoded = decode_node(&page);
        assert!(!decoded.is_leaf());
        assert_eq!(decoded.keys, original.keys);
        assert_eq!(decoded.children, original.children);
    }
}