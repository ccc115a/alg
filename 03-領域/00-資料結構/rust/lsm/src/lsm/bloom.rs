use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct BloomFilter {
    bits: Vec<u64>,
    capacity: usize,
    hashes: usize,
}

impl BloomFilter {
    pub fn new(capacity: usize) -> Self {
        let bits = (capacity + 63) / 64;
        Self {
            bits: vec![0; bits],
            capacity,
            hashes: 3,
        }
    }

    fn hash(&self, key: &[u8], seed: usize) -> usize {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        seed.hash(&mut hasher);
        (hasher.finish() as usize) % self.capacity
    }

    pub fn insert(&mut self, key: &[u8]) {
        for i in 0..self.hashes {
            let h = self.hash(key, i);
            let idx = h / 64;
            let bit = h % 64;
            if idx < self.bits.len() {
                self.bits[idx] |= 1 << bit;
            }
        }
    }

    pub fn might_contain(&self, key: &[u8]) -> bool {
        for i in 0..self.hashes {
            let h = self.hash(key, i);
            let idx = h / 64;
            let bit = h % 64;
            if idx >= self.bits.len() {
                return false;
            }
            if self.bits[idx] & (1 << bit) == 0 {
                return false;
            }
        }
        true
    }
}

impl Default for BloomFilter {
    fn default() -> Self {
        Self::new(1024)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bloom_insert_and_check() {
        let mut bloom = BloomFilter::new(100);
        bloom.insert(b"hello");
        bloom.insert(b"world");

        assert!(bloom.might_contain(b"hello"));
        assert!(bloom.might_contain(b"world"));
    }

    #[test]
    fn test_bloom_not_contain() {
        let mut bloom = BloomFilter::new(100);
        bloom.insert(b"hello");

        assert!(!bloom.might_contain(b"missing"));
    }

    #[test]
    fn test_bloom_false_positive_rate() {
        let mut bloom = BloomFilter::new(10000);
        for i in 0..1000 {
            bloom.insert(format!("key{}", i).as_bytes());
        }

        let mut false_positives = 0;
        for i in 1000..2000 {
            if bloom.might_contain(format!("missing{}", i).as_bytes()) {
                false_positives += 1;
            }
        }

        let fpr = false_positives as f64 / 1000.0;
        assert!(fpr < 0.1, "False positive rate too high: {}", fpr);
    }

    #[test]
    fn test_bloom_empty() {
        let bloom = BloomFilter::new(100);
        assert!(!bloom.might_contain(b"anything"));
    }
}