/// B+Tree 節點類型
#[derive(Debug, Clone, PartialEq)]
pub enum NodeType {
    Internal,
    Leaf,
}

/// 通用 key 類型（支援整數與字串）
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub enum Key {
    Integer(i64),
    Text(String),
}

impl std::fmt::Display for Key {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Key::Integer(v) => write!(f, "{}", v),
            Key::Text(s) => write!(f, "{}", s),
        }
    }
}

/// 資料列（Row）：以 key-value bytes 儲存
#[derive(Debug, Clone)]
pub struct Record {
    pub key: Key,
    pub value: Vec<u8>,
}

/// B+Tree 節點
#[derive(Debug, Clone)]
pub struct Node {
    pub node_type: NodeType,
    pub keys: Vec<Key>,
    pub children: Vec<usize>,
    pub records: Vec<Record>,
    pub next_leaf: Option<usize>,
}

impl Node {
    pub fn new_internal() -> Self {
        Node {
            node_type: NodeType::Internal,
            keys: Vec::new(),
            children: Vec::new(),
            records: Vec::new(),
            next_leaf: None,
        }
    }

    pub fn new_leaf() -> Self {
        Node {
            node_type: NodeType::Leaf,
            keys: Vec::new(),
            children: Vec::new(),
            records: Vec::new(),
            next_leaf: None,
        }
    }

    pub fn is_leaf(&self) -> bool {
        self.node_type == NodeType::Leaf
    }

    pub fn is_full(&self, order: usize) -> bool {
        self.keys.len() >= order - 1
    }
}