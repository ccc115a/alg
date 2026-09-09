use super::disk::BLOCK_SIZE;

pub const BITS_PER_BLOCK: u32 = BLOCK_SIZE * 8;

pub struct Bitmap {
    data: Vec<u8>,
    pub block_num: u32,
}

impl Bitmap {
    pub fn new(block_num: u32) -> Self {
        Self {
            data: vec![0u8; BLOCK_SIZE as usize],
            block_num,
        }
    }

    pub fn from_bytes(block_num: u32, data: Vec<u8>) -> Self {
        Self { data, block_num }
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        self.data.clone()
    }

    pub fn get(&self, bit: u32) -> bool {
        let byte_idx = bit / 8;
        let bit_idx = bit % 8;
        if byte_idx >= self.data.len() as u32 {
            return false;
        }
        (self.data[byte_idx as usize] & (1 << bit_idx)) != 0
    }

    pub fn set(&mut self, bit: u32, value: bool) {
        let byte_idx = bit / 8;
        let bit_idx = bit % 8;
        if byte_idx >= self.data.len() as u32 {
            return;
        }
        if value {
            self.data[byte_idx as usize] |= 1 << bit_idx;
        } else {
            self.data[byte_idx as usize] &= !(1 << bit_idx);
        }
    }

    pub fn find_first_zero(&self) -> Option<u32> {
        for (byte_idx, &byte) in self.data.iter().enumerate() {
            if byte != 0xFF {
                for bit_idx in 0..8 {
                    if (byte & (1 << bit_idx)) == 0 {
                        return Some((byte_idx * 8 + bit_idx) as u32);
                    }
                }
            }
        }
        None
    }

    pub fn count_zeros(&self) -> u32 {
        let mut count = 0u32;
        for &byte in &self.data {
            count += (8 - byte.count_ones()) as u32;
        }
        count
    }
}

pub struct InodeBitmap {
    bitmap: Bitmap,
}

impl InodeBitmap {
    pub fn new() -> Self {
        Self {
            bitmap: Bitmap::new(1),
        }
    }

    pub fn from_bytes(data: Vec<u8>) -> Self {
        Self {
            bitmap: Bitmap::from_bytes(1, data),
        }
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        self.bitmap.to_bytes()
    }

    pub fn allocate(&mut self) -> Option<u32> {
        let bit = self.bitmap.find_first_zero()?;
        self.bitmap.set(bit, true);
        Some(bit + 1)
    }

    pub fn free(&mut self, ino: u32) {
        self.bitmap.set(ino - 1, false);
    }

    pub fn is_allocated(&self, ino: u32) -> bool {
        self.bitmap.get(ino - 1)
    }
}

impl Default for InodeBitmap {
    fn default() -> Self {
        Self::new()
    }
}

pub struct BlockBitmap {
    bitmap: Bitmap,
}

impl BlockBitmap {
    pub fn new() -> Self {
        Self {
            bitmap: Bitmap::new(2),
        }
    }

    pub fn from_bytes(data: Vec<u8>) -> Self {
        Self {
            bitmap: Bitmap::from_bytes(2, data),
        }
    }

    pub fn to_bytes(&self) -> Vec<u8> {
        self.bitmap.to_bytes()
    }

    pub fn allocate(&mut self, start_block: u32) -> Option<u32> {
        for bit in 0..self.bitmap.data.len() as u32 * 8 {
            if !self.bitmap.get(bit) {
                self.bitmap.set(bit, true);
                return Some(start_block + bit);
            }
        }
        None
    }

    pub fn free(&mut self, block: u32, start_block: u32) {
        if block >= start_block {
            self.bitmap.set(block - start_block, false);
        }
    }

    pub fn is_allocated(&self, block: u32, start_block: u32) -> bool {
        if block >= start_block {
            self.bitmap.get(block - start_block)
        } else {
            false
        }
    }

    pub fn count_free(&self) -> u32 {
        self.bitmap.count_zeros()
    }
}

impl Default for BlockBitmap {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bitmap_set_get() {
        let mut bitmap = Bitmap::new(0);

        bitmap.set(0, true);
        assert!(bitmap.get(0));
        assert!(!bitmap.get(1));

        bitmap.set(7, true);
        assert!(bitmap.get(7));

        bitmap.set(0, false);
        assert!(!bitmap.get(0));
    }

    #[test]
    fn test_bitmap_find_first_zero() {
        let mut bitmap = Bitmap::new(0);

        assert_eq!(bitmap.find_first_zero(), Some(0));

        bitmap.set(0, true);
        bitmap.set(1, true);
        assert_eq!(bitmap.find_first_zero(), Some(2));

        for i in 0..bitmap.data.len() as u32 * 8 {
            bitmap.set(i, true);
        }
        assert_eq!(bitmap.find_first_zero(), None);
    }

    #[test]
    fn test_inode_bitmap() {
        let mut ibitmap = InodeBitmap::new();

        let ino1 = ibitmap.allocate().unwrap();
        assert_eq!(ino1, 1);

        let ino2 = ibitmap.allocate().unwrap();
        assert_eq!(ino2, 2);

        assert!(ibitmap.is_allocated(1));
        assert!(ibitmap.is_allocated(2));
        assert!(!ibitmap.is_allocated(3));

        ibitmap.free(1);
        assert!(!ibitmap.is_allocated(1));

        let ino3 = ibitmap.allocate().unwrap();
        assert_eq!(ino3, 1);
    }
}