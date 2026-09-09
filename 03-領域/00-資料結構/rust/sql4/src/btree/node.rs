/// B+Tree 節點類型
#[derive(Debug, Clone, PartialEq)]
pub enum NodeType {
    /// 內部節點：存放 key 與子節點指標
    Internal,
    /// 葉節點：存放實際資料，並以鏈結串列相連
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
    /// 節點中的 key 列表
    pub keys: Vec<Key>,
    /// 僅內部節點使用：子節點索引（長度 = keys.len() + 1）
    pub children: Vec<usize>,
    /// 僅葉節點使用：對應 key 的 record 資料
    pub records: Vec<Record>,
    /// 葉節點鏈結：指向下一個葉節點的索引（None 表示最後一個）
    pub next_leaf: Option<usize>,
}

impl Node {
    /// 建立空白內部節點
    pub fn new_internal() -> Self {
        Node {
            node_type: NodeType::Internal,
            keys: Vec::new(),
            children: Vec::new(),
            records: Vec::new(),
            next_leaf: None,
        }
    }

    /// 建立空白葉節點
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
