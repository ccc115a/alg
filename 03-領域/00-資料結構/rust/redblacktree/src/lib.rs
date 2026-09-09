use std::cmp::Ordering;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Color {
    Red,
    Black,
}

#[derive(Clone)]
pub struct Node<K, V> {
    pub key: K,
    pub value: V,
    pub color: Color,
    pub left: Option<Box<Node<K, V>>>,
    pub right: Option<Box<Node<K, V>>>,
}

impl<K: fmt::Debug, V: fmt::Debug> fmt::Debug for Node<K, V> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Node {{ key: {:?}, value: {:?}, color: {:?} }}",
            self.key, self.value, self.color
        )
    }
}

pub struct RedBlackTree<K, V> {
    root: Option<Box<Node<K, V>>>,
    size: usize,
}

impl<K: Ord + Clone, V: Clone> Default for RedBlackTree<K, V> {
    fn default() -> Self {
        Self::new()
    }
}

impl<K: fmt::Debug, V: fmt::Debug> fmt::Debug for RedBlackTree<K, V> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "RedBlackTree {{ size: {}, root: ", self.size)?;
        if let Some(ref root) = self.root {
            fmt::Debug::fmt(root, f)?;
        } else {
            write!(f, "None")?;
        }
        write!(f, " }}")
    }
}

impl<K: Ord + Clone, V: Clone> RedBlackTree<K, V> {
    pub fn new() -> Self {
        RedBlackTree { root: None, size: 0 }
    }

    pub fn size(&self) -> usize {
        self.size
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    fn is_red(node: &Option<Box<Node<K, V>>>) -> bool {
        node.as_ref().map_or(false, |n| n.color == Color::Red)
    }


    fn rotate_left(mut node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        let mut right = node.right.take().unwrap();
        node.right = right.left.take();
        let old_color = node.color;
        node.color = Color::Red;
        right.color = old_color;
        right.left = Some(node);
        right
    }

    fn rotate_right(mut node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        let mut left = node.left.take().unwrap();
        node.left = left.right.take();
        let old_color = node.color;
        node.color = Color::Red;
        left.color = old_color;
        left.right = Some(node);
        left
    }

    fn fix_insert(node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        let mut node = node;

        if Self::is_red(&node.right) && !Self::is_red(&node.left) {
            node = Self::rotate_left(node);
        }

        if Self::is_red(&node.left)
            && node.left.as_ref().map_or(false, |l| Self::is_red(&l.left))
        {
            node = Self::rotate_right(node);
        }

        if Self::is_red(&node.left) && Self::is_red(&node.right) {
            node.color = Color::Red;
            if let Some(ref mut l) = node.left {
                l.color = Color::Black;
            }
            if let Some(ref mut r) = node.right {
                r.color = Color::Black;
            }
        }

        node
    }

    pub fn insert(&mut self, key: K, value: V) {
        if !self.contains(&key) {
            self.size += 1;
        }
        let new_node = Box::new(Node {
            key,
            value,
            color: Color::Red,
            left: None,
            right: None,
        });

        self.root = Self::insert_recursive(self.root.take(), new_node);
        if let Some(ref mut root) = self.root {
            root.color = Color::Black;
        }
    }

    fn insert_recursive(node: Option<Box<Node<K, V>>>, new_node: Box<Node<K, V>>) -> Option<Box<Node<K, V>>> {
        match node {
            None => Some(new_node),
            Some(mut n) => {
                match new_node.key.cmp(&n.key) {
                    Ordering::Equal => {
                        n.value = new_node.value;
                        Some(n)
                    }
                    Ordering::Less => {
                        n.left = Self::insert_recursive(n.left.take(), new_node);
                        Some(Self::fix_insert(n))
                    }
                    Ordering::Greater => {
                        n.right = Self::insert_recursive(n.right.take(), new_node);
                        Some(Self::fix_insert(n))
                    }
                }
            }
        }
    }

    pub fn get(&self, key: &K) -> Option<&V> {
        let mut current = &self.root;
        while let Some(node) = current {
            match key.cmp(&node.key) {
                Ordering::Equal => return Some(&node.value),
                Ordering::Less => current = &node.left,
                Ordering::Greater => current = &node.right,
            }
        }
        None
    }

    pub fn contains(&self, key: &K) -> bool {
        self.get(key).is_some()
    }

    fn minimum(node: &Node<K, V>) -> &Node<K, V> {
        let mut current = node;
        while let Some(ref left) = current.left {
            current = left.as_ref();
        }
        current
    }

    fn maximum(node: &Node<K, V>) -> &Node<K, V> {
        let mut current = node;
        while let Some(ref right) = current.right {
            current = right.as_ref();
        }
        current
    }

    pub fn min_key(&self) -> Option<K> {
        self.root.as_ref().map(|root| Self::minimum(root).key.clone())
    }

    pub fn max_key(&self) -> Option<K> {
        self.root.as_ref().map(|root| Self::maximum(root).key.clone())
    }

    fn flip_colors(node: &mut Box<Node<K, V>>) {
        node.color = match node.color {
            Color::Red => Color::Black,
            Color::Black => Color::Red,
        };
        if let Some(ref mut l) = node.left {
            l.color = match l.color {
                Color::Red => Color::Black,
                Color::Black => Color::Red,
            };
        }
        if let Some(ref mut r) = node.right {
            r.color = match r.color {
                Color::Red => Color::Black,
                Color::Black => Color::Red,
            };
        }
    }

    fn fix_up(node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        let mut node = node;

        if Self::is_red(&node.right) {
            node = Self::rotate_left(node);
        }

        if Self::is_red(&node.left)
            && node.left.as_ref().map_or(false, |l| Self::is_red(&l.left))
        {
            node = Self::rotate_right(node);
        }

        if Self::is_red(&node.left) && Self::is_red(&node.right) {
            Self::flip_colors(&mut node);
        }

        node
    }

    fn move_red_left(mut node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        Self::flip_colors(&mut node);
        if node.right.as_ref().map_or(false, |r| Self::is_red(&r.left)) {
            node.right = Some(Self::rotate_right(node.right.take().unwrap()));
            node = Self::rotate_left(node);
            Self::flip_colors(&mut node);
        }
        node
    }

    fn move_red_right(mut node: Box<Node<K, V>>) -> Box<Node<K, V>> {
        Self::flip_colors(&mut node);
        if node.left.as_ref().map_or(false, |l| Self::is_red(&l.left)) {
            node = Self::rotate_right(node);
            Self::flip_colors(&mut node);
        }
        node
    }

    fn delete_min(node: Box<Node<K, V>>) -> Option<Box<Node<K, V>>> {
        if node.left.is_none() {
            return None;
        }
        let mut node = node;
        if !Self::is_red(&node.left)
            && node.left.as_ref().map_or(false, |l| !Self::is_red(&l.left))
        {
            node = Self::move_red_left(node);
        }
        node.left = Self::delete_min(node.left.take().unwrap());
        Some(Self::fix_up(node))
    }

    pub fn remove(&mut self, key: &K) -> bool {
        if !self.contains(key) {
            return false;
        }
        self.root = Self::remove_recursive(self.root.take(), key);
        if let Some(ref mut root) = self.root {
            root.color = Color::Black;
        }
        self.size -= 1;
        true
    }

    fn remove_recursive(
        node: Option<Box<Node<K, V>>>,
        key: &K,
    ) -> Option<Box<Node<K, V>>> {
        let mut node = match node {
            None => return None,
            Some(n) => n,
        };

        match key.cmp(&node.key) {
            Ordering::Less => {
                if !Self::is_red(&node.left)
                    && node.left.as_ref().map_or(false, |l| !Self::is_red(&l.left))
                {
                    node = Self::move_red_left(node);
                }
                node.left = Self::remove_recursive(node.left, key);
            }
            Ordering::Equal | Ordering::Greater => {
                if Self::is_red(&node.left) {
                    node = Self::rotate_right(node);
                }
                if key == &node.key && node.right.is_none() {
                    return None;
                }
                if !Self::is_red(&node.right)
                    && node.right.as_ref().map_or(false, |r| !Self::is_red(&r.left))
                {
                    node = Self::move_red_right(node);
                }
                if key == &node.key {
                    let min_key = {
                        let mut curr = node.right.as_ref().unwrap();
                        while curr.left.is_some() {
                            curr = curr.left.as_ref().unwrap();
                        }
                        curr.key.clone()
                    };
                    node.key = min_key.clone();
                    node.value = {
                        let mut curr = node.right.as_mut().unwrap();
                        while curr.left.is_some() {
                            curr = curr.left.as_mut().unwrap();
                        }
                        curr.value.clone()
                    };
                    node.right = Self::delete_min(node.right.take().unwrap());
                } else {
                    node.right = Self::remove_recursive(node.right, key);
                }
            }
        }

        Some(Self::fix_up(node))
    }

    pub fn clear(&mut self) {
        self.root = None;
        self.size = 0;
    }

    fn height_of(node: &Option<Box<Node<K, V>>>) -> usize {
        match node {
            None => 0,
            Some(n) => {
                1 + Self::height_of(&n.left).max(Self::height_of(&n.right))
            }
        }
    }

    pub fn height(&self) -> usize {
        Self::height_of(&self.root)
    }

    fn inorder_traversal(node: &Option<Box<Node<K, V>>>, result: &mut Vec<(K, V)>) {
        if let Some(n) = node {
            Self::inorder_traversal(&n.left, result);
            result.push((n.key.clone(), n.value.clone()));
            Self::inorder_traversal(&n.right, result);
        }
    }

    pub fn inorder(&self) -> Vec<(K, V)> {
        let mut result = Vec::new();
        Self::inorder_traversal(&self.root, &mut result);
        result
    }

    fn preorder_traversal(node: &Option<Box<Node<K, V>>>, result: &mut Vec<(K, V)>) {
        if let Some(n) = node {
            result.push((n.key.clone(), n.value.clone()));
            Self::preorder_traversal(&n.left, result);
            Self::preorder_traversal(&n.right, result);
        }
    }

    pub fn preorder(&self) -> Vec<(K, V)> {
        let mut result = Vec::new();
        Self::preorder_traversal(&self.root, &mut result);
        result
    }

    fn postorder_traversal(node: &Option<Box<Node<K, V>>>, result: &mut Vec<(K, V)>) {
        if let Some(n) = node {
            Self::postorder_traversal(&n.left, result);
            Self::postorder_traversal(&n.right, result);
            result.push((n.key.clone(), n.value.clone()));
        }
    }

    pub fn postorder(&self) -> Vec<(K, V)> {
        let mut result = Vec::new();
        Self::postorder_traversal(&self.root, &mut result);
        result
    }

    fn is_valid_rb_tree(node: &Option<Box<Node<K, V>>>, black_count: &mut usize) -> bool {
        match node {
            None => {
                *black_count += 1;
                true
            }
            Some(n) => {
                if n.color == Color::Red {
                    if Self::is_red(&n.left) || Self::is_red(&n.right) {
                        return false;
                    }
                }

                let mut left_black = 0;
                let mut right_black = 0;

                if !Self::is_valid_rb_tree(&n.left, &mut left_black) {
                    return false;
                }
                if !Self::is_valid_rb_tree(&n.right, &mut right_black) {
                    return false;
                }

                if left_black != right_black {
                    return false;
                }

                if n.color == Color::Black {
                    left_black += 1;
                }

                *black_count = left_black;
                true
            }
        }
    }

    pub fn is_valid(&self) -> bool {
        if self.root.is_none() {
            return true;
        }

        if Self::is_red(&self.root) {
            return false;
        }

        let mut black_count = 0;
        if !Self::is_valid_rb_tree(&self.root, &mut black_count) {
            return false;
        }

        true
    }

    pub fn iter(&self) -> Iter<'_, K, V> {
        let mut stack = Vec::new();
        let mut current = self.root.as_deref();

        while let Some(node) = current {
            stack.push(node);
            current = node.left.as_deref();
        }

        Iter { stack }
    }

    pub fn keys(&self) -> Vec<K> {
        let mut keys = Vec::new();
        Self::inorder_keys(&self.root, &mut keys);
        keys
    }

    fn inorder_keys(node: &Option<Box<Node<K, V>>>, result: &mut Vec<K>) {
        if let Some(n) = node {
            Self::inorder_keys(&n.left, result);
            result.push(n.key.clone());
            Self::inorder_keys(&n.right, result);
        }
    }

    pub fn values(&self) -> Vec<V> {
        let mut values = Vec::new();
        Self::inorder_values(&self.root, &mut values);
        values
    }

    fn inorder_values(node: &Option<Box<Node<K, V>>>, result: &mut Vec<V>) {
        if let Some(n) = node {
            Self::inorder_values(&n.left, result);
            result.push(n.value.clone());
            Self::inorder_values(&n.right, result);
        }
    }
}

pub struct Iter<'a, K, V> {
    stack: Vec<&'a Node<K, V>>,
}

impl<'a, K, V> Iterator for Iter<'a, K, V> {
    type Item = (&'a K, &'a V);

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(node) = self.stack.pop() {
            let result = Some((&node.key, &node.value));

            if node.right.is_some() {
                let mut right_node = node.right.as_ref().unwrap();
                loop {
                    self.stack.push(right_node);
                    if right_node.left.is_some() {
                        right_node = right_node.left.as_ref().unwrap();
                    } else {
                        break;
                    }
                }
            }

            return result;
        }
        None
    }
}

impl<'a, K: Ord + Clone, V: Clone> IntoIterator for &'a RedBlackTree<K, V> {
    type Item = (&'a K, &'a V);
    type IntoIter = Iter<'a, K, V>;

    fn into_iter(self) -> Self::IntoIter {
        self.iter()
    }
}

pub struct IntoIter<K, V> {
    stack: Vec<Box<Node<K, V>>>,
}

impl<K: Ord + Clone, V: Clone> Iterator for IntoIter<K, V> {
    type Item = (K, V);

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(node) = self.stack.pop() {
            let result = Some((node.key.clone(), node.value.clone()));

            if node.right.is_some() {
                let mut right_node = node.right.unwrap();
                loop {
                    self.stack.push(right_node.clone());
                    if right_node.left.is_some() {
                        right_node = right_node.left.unwrap();
                    } else {
                        break;
                    }
                }
            }

            return result;
        }
        None
    }
}

impl<K: Ord + Clone, V: Clone> IntoIterator for RedBlackTree<K, V> {
    type Item = (K, V);
    type IntoIter = IntoIter<K, V>;

    fn into_iter(self) -> Self::IntoIter {
        let mut stack = Vec::new();
        let mut current = self.root;

        while let Some(node) = current {
            stack.push(node.clone());
            current = node.left;
        }

        IntoIter { stack }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_tree() {
        let tree: RedBlackTree<i32, &str> = RedBlackTree::new();
        assert_eq!(tree.size(), 0);
        assert!(tree.is_empty());
        assert!(tree.is_valid());
    }

    #[test]
    fn test_insert_single() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        assert_eq!(tree.size(), 1);
        assert_eq!(tree.get(&10), Some(&"ten"));
        assert!(tree.is_valid());
    }

    #[test]
    fn test_insert_multiple() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        tree.insert(3, "three");
        tree.insert(7, "seven");
        assert_eq!(tree.size(), 5);
        assert!(tree.is_valid());
        assert_eq!(tree.get(&10), Some(&"ten"));
        assert_eq!(tree.get(&5), Some(&"five"));
        assert_eq!(tree.get(&15), Some(&"fifteen"));
    }

    #[test]
    fn test_insert_duplicate_updates() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(10, "TEN");
        assert_eq!(tree.size(), 1);
        assert_eq!(tree.get(&10), Some(&"TEN"));
    }

    #[test]
    fn test_contains() {
        let mut tree = RedBlackTree::new();
        tree.insert(1, "one");
        tree.insert(2, "two");
        tree.insert(3, "three");
        assert!(tree.contains(&1));
        assert!(tree.contains(&2));
        assert!(tree.contains(&3));
        assert!(!tree.contains(&4));
    }

    #[test]
    fn test_remove_leaf() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        tree.remove(&5);
        assert_eq!(tree.size(), 2);
        assert!(!tree.contains(&5));
        assert!(tree.is_valid());
    }

    #[test]
    fn test_remove_root() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.remove(&10);
        assert!(tree.is_empty());
        assert!(tree.is_valid());
    }

    #[test]
    fn test_remove_internal() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        tree.insert(3, "three");
        tree.insert(7, "seven");
        tree.insert(12, "twelve");
        tree.insert(17, "seventeen");
        tree.remove(&10);
        assert_eq!(tree.size(), 6);
        assert!(!tree.contains(&10));
        assert!(tree.is_valid());
    }

    #[test]
    fn test_remove_nonexistent() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        let result = tree.remove(&99);
        assert!(!result);
        assert_eq!(tree.size(), 1);
    }

    #[test]
    fn test_clear() {
        let mut tree = RedBlackTree::new();
        tree.insert(1, "one");
        tree.insert(2, "two");
        tree.insert(3, "three");
        tree.clear();
        assert!(tree.is_empty());
        assert!(tree.is_valid());
    }

    #[test]
    fn test_min_max() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        tree.insert(2, "two");
        tree.insert(20, "twenty");
        assert_eq!(tree.min_key(), Some(2));
        assert_eq!(tree.max_key(), Some(20));
    }

    #[test]
    fn test_inorder() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        tree.insert(2, "two");
        tree.insert(7, "seven");
        let inorder = tree.inorder();
        let keys: Vec<_> = inorder.iter().map(|(k, _)| k).collect();
        assert_eq!(keys, vec![&2, &5, &7, &10, &15]);
    }

    #[test]
    fn test_preorder() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        let preorder = tree.preorder();
        assert_eq!(preorder.len(), 3);
    }

    #[test]
    fn test_postorder() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        let postorder = tree.postorder();
        assert_eq!(postorder.len(), 3);
    }

    #[test]
    fn test_height() {
        let mut tree = RedBlackTree::new();
        assert_eq!(tree.height(), 0);
        tree.insert(10, "ten");
        assert_eq!(tree.height(), 1);
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        let h = tree.height();
        assert!(h >= 2 && h <= 4);
    }

    #[test]
    fn test_iter() {
        let mut tree = RedBlackTree::new();
        tree.insert(3, "three");
        tree.insert(1, "one");
        tree.insert(2, "two");
        tree.insert(5, "five");
        let items: Vec<_> = tree.iter().collect();
        assert_eq!(items.len(), 4);
    }

    #[test]
    fn test_keys_values() {
        let mut tree = RedBlackTree::new();
        tree.insert(10, "ten");
        tree.insert(5, "five");
        tree.insert(15, "fifteen");
        let keys = tree.keys();
        assert_eq!(keys, vec![5, 10, 15]);
        let values = tree.values();
        assert_eq!(values, vec!["five", "ten", "fifteen"]);
    }

    #[test]
    fn test_large_insertion() {
        let mut tree = RedBlackTree::new();
        for i in 0..1000 {
            tree.insert(i, i);
        }
        assert_eq!(tree.size(), 1000);
        assert!(tree.is_valid());
        for i in 0..1000 {
            assert_eq!(tree.get(&i), Some(&i));
        }
    }

    #[test]
    fn test_remove_many() {
        let mut tree = RedBlackTree::new();
        for i in 0..100 {
            tree.insert(i, i);
        }
        assert!(tree.is_valid());

        for i in 0..50 {
            tree.remove(&i);
        }
        assert!(tree.is_valid());
        assert_eq!(tree.size(), 50);

        for i in 50..100 {
            assert!(tree.contains(&i));
        }
    }

    #[test]
    fn test_string_keys() {
        let mut tree = RedBlackTree::new();
        tree.insert(String::from("apple"), 1);
        tree.insert(String::from("banana"), 2);
        tree.insert(String::from("cherry"), 3);
        assert_eq!(tree.get(&String::from("banana")), Some(&2));
        assert!(tree.is_valid());
    }

    #[test]
    fn test_complex_tree() {
        let mut tree = RedBlackTree::new();
        let data = vec![
            (50, "fifty"), (30, "thirty"), (70, "seventy"),
            (20, "twenty"), (40, "forty"), (60, "sixty"),
            (80, "eighty"), (10, "ten"), (25, "twenty-five"),
            (35, "thirty-five"), (45, "forty-five"), (55, "fifty-five"),
            (65, "sixty-five"), (75, "seventy-five"), (90, "ninety"),
        ];

        for (k, v) in data {
            tree.insert(k, v);
        }

        assert!(tree.is_valid());
        assert_eq!(tree.size(), 15);
        assert_eq!(tree.min_key(), Some(10));
        assert_eq!(tree.max_key(), Some(90));

        tree.remove(&20);
        assert!(tree.is_valid());
        tree.remove(&50);
        assert!(tree.is_valid());
        tree.remove(&80);
        assert!(tree.is_valid());
    }

    #[test]
    fn test_rb_properties() {
        let mut tree = RedBlackTree::new();
        for i in 0..50 {
            tree.insert(i, i);
        }
        assert!(tree.is_valid());

        if let Some(ref root) = tree.root {
            assert!(root.color == Color::Black);
        }
    }

    #[test]
    fn test_duplicate_insertion() {
        let mut tree = RedBlackTree::new();
        tree.insert(1, "one");
        tree.insert(1, "ONE");
        tree.insert(1, "ONE ONE");
        assert_eq!(tree.size(), 1);
        assert_eq!(tree.get(&1), Some(&"ONE ONE"));
    }

    #[test]
    fn test_into_iter() {
        let mut tree = RedBlackTree::new();
        tree.insert(3, "c");
        tree.insert(1, "a");
        tree.insert(2, "b");
        tree.insert(5, "d");

        let items: Vec<_> = tree.into_iter().collect();
        assert_eq!(items.len(), 4);
    }

    #[test]
    fn test_large_random() {
        let mut tree = RedBlackTree::new();
        let mut values: Vec<i32> = (0..500).collect();

        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        values.sort_by(|a, b| {
            let mut ha = DefaultHasher::new();
            let mut hb = DefaultHasher::new();
            a.hash(&mut ha);
            b.hash(&mut hb);
            ha.finish().cmp(&hb.finish())
        });

        for i in values {
            tree.insert(i, i * 2);
        }

        assert!(tree.is_valid());
        assert_eq!(tree.size(), 500);
    }

    #[test]
    fn test_remove_root_after_insert() {
        let mut tree = RedBlackTree::new();
        tree.insert(1, "one");
        tree.insert(2, "two");
        tree.insert(3, "three");
        tree.remove(&1);
        assert!(tree.is_valid());
        assert!(!tree.contains(&1));
        assert!(tree.contains(&2));
        assert!(tree.contains(&3));
    }
}