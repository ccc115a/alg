use std::collections::BTreeMap;
use std::fmt::Debug;

/// A Patricia Trie (Radix Tree) — a compressed trie where nodes with only one
/// child are merged with their parent, resulting in more compact storage.
#[derive(Debug, Clone)]
pub struct PatriciaTrie<V> {
    root: Node<V>,
    size: usize,
}

#[derive(Debug, Clone)]
struct Node<V> {
    key: String,
    value: Option<V>,
    children: BTreeMap<String, Box<Node<V>>>,
}

impl<V> Node<V> {
    fn new(key: &str) -> Self {
        Node {
            key: key.to_string(),
            value: None,
            children: BTreeMap::new(),
        }
    }
}

fn first_char(s: &str) -> String {
    s.chars().next().unwrap().to_string()
}

fn longest_common_prefix_length(key: &str, child_key: &str) -> usize {
    let bytes = key.as_bytes()
        .iter()
        .zip(child_key.as_bytes())
        .take_while(|(x, y)| x == y)
        .count();
    let mut lcp = bytes;
    while lcp > 0 && !key.is_char_boundary(lcp) {
        lcp -= 1;
    }
    lcp
}

impl<V: Clone + Debug> PatriciaTrie<V> {
    pub fn new() -> Self {
        PatriciaTrie {
            root: Node::new(""),
            size: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    pub fn len(&self) -> usize {
        self.size
    }

    pub fn insert(&mut self, key: &str, value: V) -> Option<V> {
        let old = Self::insert_recursive(&mut self.root, key, value);
        if old.is_none() {
            self.size += 1;
        }
        old
    }

    fn insert_recursive(node: &mut Node<V>, key: &str, value: V) -> Option<V> {
        if key.is_empty() {
            let old = node.value.take();
            node.value = Some(value);
            return old;
        }

        let fc = first_char(key);

        if !node.children.contains_key(&fc) {
            let mut child = Node::new(key);
            child.value = Some(value);
            node.children.insert(fc, Box::new(child));
            return None;
        }

        let child_key = node.children[&fc].key.clone();
        let lcp = longest_common_prefix_length(key, &child_key);

        if lcp == child_key.len() {
            let child = node.children.get_mut(&fc).unwrap();
            return Self::insert_recursive(child, &key[lcp..], value);
        }

        let mut child = node.children.remove(&fc).unwrap();

        let mut rest = Node::new(&child.key[lcp..]);
        rest.value = child.value.take();
        rest.children = std::mem::take(&mut child.children);

        child.key = child.key[..lcp].to_string();
        child.value = None;

        let rest_fc = first_char(&rest.key);
        child.children.insert(rest_fc, Box::new(rest));

        let old = Self::insert_recursive(&mut child, &key[lcp..], value);
        node.children.insert(fc, child);
        old
    }

    pub fn get(&self, key: &str) -> Option<&V> {
        Self::get_recursive(&self.root, key)
    }

    fn get_recursive<'a>(node: &'a Node<V>, key: &str) -> Option<&'a V> {
        if key.is_empty() {
            return node.value.as_ref();
        }

        let fc = first_char(key);
        match node.children.get(&fc) {
            None => None,
            Some(child) => {
                if key.starts_with(&child.key) {
                    Self::get_recursive(child, &key[child.key.len()..])
                } else {
                    None
                }
            }
        }
    }

    pub fn contains(&self, key: &str) -> bool {
        self.get(key).is_some()
    }

    pub fn delete(&mut self, key: &str) -> Option<V> {
        let (old, _) = Self::delete_internal(&mut self.root, key);
        if old.is_some() {
            self.size -= 1;
        }
        old
    }

    fn delete_internal(node: &mut Node<V>, key: &str) -> (Option<V>, bool) {
        if key.is_empty() {
            let old = node.value.take();
            let should_remove = old.is_some()
                && node.value.is_none()
                && node.children.is_empty()
                && !node.key.is_empty();
            return (old, should_remove);
        }

        let fc = first_char(key);

        let child_key = match node.children.get(&fc) {
            None => return (None, false),
            Some(c) => c.key.clone(),
        };

        if !key.starts_with(&child_key) {
            return (None, false);
        }

        let child = node.children.get_mut(&fc).unwrap();
        let (old, should_remove_child) = Self::delete_internal(child, &key[child_key.len()..]);

        if old.is_none() {
            return (None, false);
        }

        if should_remove_child {
            node.children.remove(&fc);
        }

        if node.value.is_none() && node.children.len() == 1 && !node.key.is_empty() {
            let only_key = node.children.keys().next().unwrap().clone();
            let mut only_child = node.children.remove(&only_key).unwrap();
            node.key.push_str(&only_child.key);
            node.value = only_child.value.take();
            node.children = std::mem::take(&mut only_child.children);
        }

        let should_remove = node.value.is_none()
            && node.children.is_empty()
            && !node.key.is_empty();
        (old, should_remove)
    }

    pub fn keys(&self) -> Vec<String> {
        let mut result = Vec::new();
        Self::collect_keys(&self.root, "", &mut result);
        result
    }

    fn collect_keys(node: &Node<V>, prefix: &str, result: &mut Vec<String>) {
        let full_key = format!("{}{}", prefix, node.key);
        if node.value.is_some() {
            result.push(full_key.clone());
        }
        for child in node.children.values() {
            Self::collect_keys(child, &full_key, result);
        }
    }

    pub fn values(&self) -> Vec<&V> {
        let mut result = Vec::new();
        Self::collect_values(&self.root, &mut result);
        result
    }

    fn collect_values<'a>(node: &'a Node<V>, result: &mut Vec<&'a V>) {
        if let Some(v) = &node.value {
            result.push(v);
        }
        for child in node.children.values() {
            Self::collect_values(child, result);
        }
    }

    pub fn iter(&self) -> Vec<(String, &V)> {
        let mut result = Vec::new();
        Self::collect_entries(&self.root, "", &mut result);
        result
    }

    fn collect_entries<'a>(
        node: &'a Node<V>,
        prefix: &str,
        result: &mut Vec<(String, &'a V)>,
    ) {
        let full_key = format!("{}{}", prefix, node.key);
        if let Some(v) = &node.value {
            result.push((full_key.clone(), v));
        }
        for child in node.children.values() {
            Self::collect_entries(child, &full_key, result);
        }
    }

    pub fn prefix_search(&self, prefix: &str) -> Vec<(String, &V)> {
        let mut result = Vec::new();
        let mut node = &self.root;
        let mut consumed = 0;

        while consumed < prefix.len() {
            let remaining = &prefix[consumed..];
            let fc = first_char(remaining);
            match node.children.get(&fc) {
                None => return result,
                Some(child) => {
                    if remaining.starts_with(&child.key) {
                        consumed += child.key.len();
                        node = child;
                    } else {
                        return result;
                    }
                }
            }
        }

        if let Some(v) = &node.value {
            result.push((prefix.to_string(), v));
        }
        for child in node.children.values() {
            Self::collect_entries(child, prefix, &mut result);
        }
        result
    }

    pub fn longest_prefix(&self, key: &str) -> Option<(String, &V)> {
        let mut node = &self.root;
        let mut remaining = key;
        let mut longest: Option<(String, &V)> = None;

        if let Some(v) = &node.value {
            longest = Some(("".to_string(), v));
        }

        while !remaining.is_empty() {
            let fc = first_char(remaining);
            match node.children.get(&fc) {
                None => break,
                Some(child) => {
                    if remaining.starts_with(&child.key) {
                        remaining = &remaining[child.key.len()..];
                        node = child;
                        if let Some(v) = &node.value {
                            let matched = &key[..key.len() - remaining.len()];
                            longest = Some((matched.to_string(), v));
                        }
                    } else {
                        break;
                    }
                }
            }
        }

        longest
    }
}

impl<V: Clone + Debug> Default for PatriciaTrie<V> {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_trie() {
        let trie: PatriciaTrie<i32> = PatriciaTrie::new();
        assert!(trie.is_empty());
        assert_eq!(trie.len(), 0);
        assert_eq!(trie.get("anything"), None);
        assert!(!trie.contains("anything"));
    }

    #[test]
    fn test_insert_and_get() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("cat", 1), None);
        assert_eq!(trie.insert("car", 2), None);
        assert_eq!(trie.insert("dog", 3), None);

        assert_eq!(trie.len(), 3);
        assert!(!trie.is_empty());
        assert_eq!(trie.get("cat"), Some(&1));
        assert_eq!(trie.get("car"), Some(&2));
        assert_eq!(trie.get("dog"), Some(&3));
        assert_eq!(trie.get("c"), None);
        assert_eq!(trie.get("ca"), None);
        assert_eq!(trie.get("cats"), None);
    }

    #[test]
    fn test_update_existing_key() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("key", 1), None);
        assert_eq!(trie.insert("key", 2), Some(1));
        assert_eq!(trie.get("key"), Some(&2));
        assert_eq!(trie.len(), 1);
    }

    #[test]
    fn test_insert_empty_string() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("", 42), None);
        assert_eq!(trie.get(""), Some(&42));
        assert_eq!(trie.len(), 1);
    }

    #[test]
    fn test_prefix_extension() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("test", 1), None);
        assert_eq!(trie.insert("testing", 2), None);
        assert_eq!(trie.insert("tester", 3), None);

        assert_eq!(trie.get("test"), Some(&1));
        assert_eq!(trie.get("testing"), Some(&2));
        assert_eq!(trie.get("tester"), Some(&3));
    }

    #[test]
    fn test_node_splitting() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("cat", 1), None);
        assert_eq!(trie.insert("car", 2), None);
        assert_eq!(trie.insert("bat", 3), None);

        assert_eq!(trie.get("cat"), Some(&1));
        assert_eq!(trie.get("car"), Some(&2));
        assert_eq!(trie.get("bat"), Some(&3));
        assert_eq!(trie.len(), 3);
    }

    #[test]
    fn test_delete_leaf() {
        let mut trie = PatriciaTrie::new();
        trie.insert("cat", 1);
        trie.insert("car", 2);

        assert_eq!(trie.delete("cat"), Some(1));
        assert_eq!(trie.len(), 1);
        assert_eq!(trie.get("cat"), None);
        assert_eq!(trie.get("car"), Some(&2));
    }

    #[test]
    fn test_delete_nonexistent() {
        let mut trie: PatriciaTrie<i32> = PatriciaTrie::new();
        assert_eq!(trie.delete("nothing"), None);
    }

    #[test]
    fn test_delete_causes_merge() {
        let mut trie = PatriciaTrie::new();
        trie.insert("test", 1);
        trie.insert("testing", 2);

        assert_eq!(trie.delete("testing"), Some(2));
        assert_eq!(trie.len(), 1);
        assert_eq!(trie.get("test"), Some(&1));
    }

    #[test]
    fn test_delete_causes_cascading_merge() {
        let mut trie = PatriciaTrie::new();
        trie.insert("car", 1);
        trie.insert("cat", 2);

        assert_eq!(trie.delete("car"), Some(1));
        assert_eq!(trie.len(), 1);
        assert_eq!(trie.get("cat"), Some(&2));
    }

    #[test]
    fn test_delete_from_internal_node() {
        let mut trie = PatriciaTrie::new();
        trie.insert("test", 1);
        trie.insert("testing", 2);
        trie.insert("tester", 3);

        assert_eq!(trie.delete("test"), Some(1));
        assert_eq!(trie.len(), 2);
        assert_eq!(trie.get("test"), None);
        assert_eq!(trie.get("testing"), Some(&2));
        assert_eq!(trie.get("tester"), Some(&3));
    }

    #[test]
    fn test_delete_empty_key() {
        let mut trie = PatriciaTrie::new();
        trie.insert("", 1);
        trie.insert("a", 2);

        assert_eq!(trie.delete(""), Some(1));
        assert_eq!(trie.len(), 1);
        assert_eq!(trie.get("a"), Some(&2));
    }

    #[test]
    fn test_prefix_search() {
        let mut trie = PatriciaTrie::new();
        trie.insert("apple", 1);
        trie.insert("appetite", 2);
        trie.insert("app", 3);
        trie.insert("banana", 4);

        let results = trie.prefix_search("app");
        assert_eq!(results.len(), 3);

        let mut keys: Vec<String> = results.into_iter().map(|(k, _)| k).collect();
        keys.sort();
        assert_eq!(keys, vec!["app", "appetite", "apple"]);
    }

    #[test]
    fn test_prefix_search_no_matches() {
        let mut trie = PatriciaTrie::new();
        trie.insert("cat", 1);
        trie.insert("car", 2);

        let results = trie.prefix_search("dog");
        assert!(results.is_empty());
    }

    #[test]
    fn test_prefix_search_empty_prefix() {
        let mut trie = PatriciaTrie::new();
        trie.insert("a", 1);
        trie.insert("b", 2);

        let results = trie.prefix_search("");
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_longest_prefix() {
        let mut trie = PatriciaTrie::new();
        trie.insert("a", 1);
        trie.insert("ab", 2);
        trie.insert("abc", 3);

        assert_eq!(trie.longest_prefix("abcdef"), Some(("abc".to_string(), &3)));
        assert_eq!(trie.longest_prefix("abxyz"), Some(("ab".to_string(), &2)));
        assert_eq!(trie.longest_prefix("axyz"), Some(("a".to_string(), &1)));
        assert_eq!(trie.longest_prefix("xyz"), None);
    }

    #[test]
    fn test_longest_prefix_with_root() {
        let mut trie = PatriciaTrie::new();
        trie.insert("", 0);
        trie.insert("hello", 1);

        let result = trie.longest_prefix("world");
        assert_eq!(result, Some(("".to_string(), &0)));
    }

    #[test]
    fn test_keys_and_values() {
        let mut trie = PatriciaTrie::new();
        trie.insert("z", 3);
        trie.insert("a", 1);
        trie.insert("b", 2);

        let mut keys = trie.keys();
        keys.sort();
        assert_eq!(keys, vec!["a", "b", "z"]);

        let mut values: Vec<&i32> = trie.values();
        values.sort();
        assert_eq!(values, vec![&1, &2, &3]);
    }

    #[test]
    fn test_iter() {
        let mut trie = PatriciaTrie::new();
        trie.insert("one", 1);
        trie.insert("two", 2);

        let entries = trie.iter();
        assert_eq!(entries.len(), 2);
    }

    #[test]
    fn test_default() {
        let trie: PatriciaTrie<i32> = Default::default();
        assert!(trie.is_empty());
    }

    #[test]
    fn test_large_insert() {
        let mut trie = PatriciaTrie::new();
        for i in 0..1000 {
            trie.insert(&format!("key_{}", i), i);
        }
        assert_eq!(trie.len(), 1000);
        for i in 0..1000 {
            assert_eq!(trie.get(&format!("key_{}", i)), Some(&i));
        }
    }

    #[test]
    fn test_unicode() {
        let mut trie = PatriciaTrie::new();
        trie.insert("café", 1);
        trie.insert("cafeteria", 2);
        trie.insert("你好", 3);
        trie.insert("世界", 4);

        assert_eq!(trie.get("café"), Some(&1));
        assert_eq!(trie.get("你好"), Some(&3));
        assert_eq!(trie.len(), 4);
    }

    #[test]
    fn test_clone() {
        let mut trie = PatriciaTrie::new();
        trie.insert("key", 42);
        let cloned = trie.clone();
        assert_eq!(cloned.get("key"), Some(&42));
        assert_eq!(cloned.len(), 1);
    }

    #[test]
    fn test_insert_and_delete_many() {
        let mut trie = PatriciaTrie::new();
        let words = vec!["a", "ab", "abc", "abcd", "abcde"];

        for (i, w) in words.iter().enumerate() {
            trie.insert(w, i);
        }
        assert_eq!(trie.len(), 5);

        for w in words.iter().rev() {
            assert!(trie.contains(w));
            trie.delete(w);
        }
        assert!(trie.is_empty());
    }

    #[test]
    fn test_contains() {
        let mut trie = PatriciaTrie::new();
        trie.insert("hello", 1);
        assert!(trie.contains("hello"));
        assert!(!trie.contains("world"));
        assert!(!trie.contains("hel"));
    }

    #[test]
    fn test_duplicate_insert() {
        let mut trie = PatriciaTrie::new();
        assert_eq!(trie.insert("x", 10), None);
        assert_eq!(trie.insert("x", 20), Some(10));
        assert_eq!(trie.insert("x", 30), Some(20));
        assert_eq!(trie.len(), 1);
    }

    #[test]
    fn test_delete_all() {
        let mut trie = PatriciaTrie::new();
        trie.insert("a", 1);
        trie.insert("b", 2);
        trie.delete("a");
        trie.delete("b");
        assert!(trie.is_empty());
        assert_eq!(trie.len(), 0);
    }

    #[test]
    fn test_delete_with_shared_prefix() {
        let mut trie = PatriciaTrie::new();
        trie.insert("ab", 1);
        trie.insert("abc", 2);
        trie.insert("abcd", 3);

        trie.delete("abc");
        assert_eq!(trie.len(), 2);
        assert_eq!(trie.get("ab"), Some(&1));
        assert_eq!(trie.get("abcd"), Some(&3));
        assert_eq!(trie.get("abc"), None);
    }

    #[test]
    fn test_longest_prefix_no_root() {
        let trie: PatriciaTrie<i32> = PatriciaTrie::new();
        assert_eq!(trie.longest_prefix("anything"), None);
    }

    #[test]
    fn test_prefix_search_partial_match() {
        let mut trie = PatriciaTrie::new();
        trie.insert("abcde", 1);

        let results = trie.prefix_search("abcdef");
        assert!(results.is_empty());
    }
}
