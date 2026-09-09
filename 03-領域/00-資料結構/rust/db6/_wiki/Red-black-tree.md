# Red Black Tree（紅黑樹）

## 概述

紅黑樹（Red-Black Tree）是一種自平衡的二元搜尋樹，由 Rudolf Bayer 在 1972 年提出。紅黑樹通過對每個節點著色（紅色或黑色）和一套維護規則，確保任何從根到葉子的最長路徑不會超過最短路徑的兩倍，從而保證搜尋、插入、刪除操作都在 O(log n) 時間內完成。

紅黑樹廣泛應用於作業系統的行程排程、語言執行環境的標準庫（如 C++ STL 的 map、Java 的 TreeMap）以及資料庫的索引結構中。

## 節點結構

```rust
pub enum Color {
    Red,
    Black,
}

pub struct Node<K, V> {
    key: K,
    value: V,
    color: Color,
    left: Option<Box<Node<K, V>>>,
    right: Option<Box<Node<K, V>>>,
    parent: Option<*mut Node<K, V>>,
}
```

每個節點附帶顏色資訊，用於維護平衡。

## 五大性質

紅黑樹必須滿足以下五個性質：

1. **節點是紅色或黑色**
2. **根節點是黑色**
3. **所有葉節點（NIL）是黑色**
4. **紅色節點的子節點必須是黑色**（不能有兩個連續的紅色節點）
5. **從任一節點到其每個葉子的所有路徑都包含相同數量的黑色節點**

```
    ┌─── 性質 4：紅色節點的子節點必須是黑色
    │
    ▼
    ┌─────────┐         ┌─────────┐
    │  Black  │◀────────│   Red   │
    │    │    │         │ (不能   │
    │    │    │         │  這樣)  │
    └────┴────┘         └────┬────┘
         │                   │
         ▼                   ▼
    ┌─────────┐         ┌─────────┐
    │   Red   │         │   Red   │  ← 錯誤！兩個連續紅色
    └─────────┘         └─────────┘
```

## 旋轉操作

紅黑樹通過旋轉來維持平衡：

### 左旋（Left Rotate）

```
      x                y
     / \     ───▶     / \
    α   y             x   γ
       / \          / \
      β   γ        α   β
```

```rust
fn rotate_left(&mut self, x: *mut Node<K, V>) {
    let y = x.right.take().unwrap();
    x.right = y.left.take();
    
    if let Some(ref mut y_left) = y.left {
        y_left.parent = Some(x);
    }
    
    y.parent = x.parent;
    
    match x.parent {
        None => self.root = Some(y),
        Some(p) => {
            if p.left.as_ptr() == x {
                p.left = Some(y);
            } else {
                p.right = Some(y);
            }
        }
    }
    
    y.left = Some(x);
    x.parent = Some(y);
}
```

### 右旋（Right Rotate）

```
      x                y
     / \     ◀────     / \
        y             x   γ
       / \          / \
      β   γ        α   β
```

右旋是左旋的鏡像操作。

## 插入

插入新節點的步驟：

### 步驟 1：標準 BST 插入

```rust
fn insert(&mut self, key: K, value: V) {
    let new_node = Box::new(Node {
        key,
        value,
        color: Color::Red,  // 新節點預設為紅色
        left: None,
        right: None,
        parent: None,
    });
    
    let mut current = self.root.take();
    let mut parent: *mut Node<K, V> = null_mut();
    
    while !current.is_null() {
        parent = current;
        if new_node.key < current.key {
            current = current.left;
        } else {
            current = current.right;
        }
    }
    
    new_node.parent = Some(parent);
    if parent.is_null() {
        self.root = Some(new_node);
    } else if new_node.key < unsafe { &*parent }.key {
        unsafe { &mut *parent }.left = Some(new_node);
    } else {
        unsafe { &mut *parent }.right = Some(new_node);
    }
    
    self.insert_fixup(new_node);  // 修復紅黑性質
}
```

### 步驟 2：修復（Fixup）

當新節點插入後，可能破壞紅黑性質。需要根據三種情況修復：

**情況 1：叔節點是紅色**

```
    ┌───────────────────────────────────────┐
    │         ┌─P(Black)─┐                  │
    │         │          │                   │
    │       (U:Red)    (N:Red) ← 新節點     │
    │                                     │
    └── 將 P 和 U 變為黑色，G 變為紅色 ────┘
    
    ┌─G(Red)─┐
    │        │
    ▼        ▼
  P(Black)  U(Black)
    │
    ▼
  N(Red) ← 新節點
```

**情況 2 & 3：叔節點是黑色，需要旋轉**

```
   情況 2：N 是 P 的右子樹               情況 3：N 是 P 的左子樹
   ┌────────────────────────┐          ┌────────────────────────┐
   │    ┌──G(Black)──┐     │          │    ┌──G(Black)──┐     │  │
   │    │     │      │     │          │    │     │      │     │  │
   │    │   P(Red)   U     │          │    │   P(Red)   U     │  │
   │    │      │     │     │          │    │      │     │     │  │
   │    │    (N:Red)│     │          │    │    (N:Red)│     │  │
   │    └────────────┘     │          │    └────────────┘     │  │
   │  左旋 P              │          │  右旋 P，變成情況 3   │  │
   └────────────────────────┘          └────────────────────────┘
```

## 刪除

刪除比插入更複雜，因為要刪除的節點可能是黑色。

### 基本步驟

1. 找到要刪除的節點
2. 如果節點有兩個子樹，用後繼節點替換
3. 刪除節點
4. 修復紅黑性質

### Fixup

刪除黑色節點會破壞「每條路徑黑色節點數相同」的性質，需要通過「雙黑」修復。

## 與 AVL 樹的比較

| 特性 | 紅黑樹 | AVL 樹 |
|------|--------|--------|
| 平衡程度 | 近似平衡（最多 2:1） | 嚴格平衡（嚴格等高） |
| 插入/刪除代價 | 較低（少旋轉） | 較高（多旋轉） |
| 搜尋效能 | 稍低 | 稍高 |
| 實作複雜度 | 簡單 | 較複雜 |
| 記憶體開銷 | 只需 1 bit 顏色 | 需要高度欄位 |
| 典型應用 | C++ STL map, Java TreeMap | 嚴格平衡需求的場景 |

## 優點

1. **效能穩定**：最壞情況仍是 O(log n)
2. **插入/刪除代價適中**：不需要像 AVL 那樣嚴格平衡
3. **實作相對簡單**：只需要處理旋轉和著色
4. **記憶體效率高**：每節點只需 1 bit 額外空間

## 缺點

1. **搜尋效能不如 AVL**：平衡程度較低
2. **最長路徑可能是最短路徑的 2 倍**：不如 AVL 嚴格

## 應用場景

1. **C++ STL 的 map 和 set**：紅黑樹實現
2. **Java 的 TreeMap 和 TreeSet**：紅黑樹實現
3. **Linux 核心的排程器**：行程管理
4. **epoll**：I/O 多路復用
5. **MongoDB 的 MMAPv1 儲存引擎**：記憶體映射管理

## 在 db6 中的應用

db6 的 MemoryEngine 使用 Rust 的 BTreeMap（基於 B-Tree），而非紅黑樹。但紅黑樹的設計思想影響了 LSM Tree 的實現：

- LSM Tree 的 MemTable 可以使用紅黑樹或跳表
- 紅黑樹的自平衡思想被應用於 LSM 的 Compaction 策略

## 延伸閱讀

- Cormen, T. H., et al. (2009). Introduction to Algorithms (3rd Edition). MIT Press.
- Sedgewick, R. (2013). Algorithms (4th Edition). Addison-Wesley.