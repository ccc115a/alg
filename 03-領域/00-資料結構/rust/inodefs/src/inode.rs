use super::disk::BLOCK_SIZE;

pub const INODE_SIZE: u32 = 128;
pub const DIRECT_BLOCKS: usize = 10;
pub const MAX_FILE_SIZE: u32 = DIRECT_BLOCKS as u32 * BLOCK_SIZE;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FileType {
    Fifo = 0x1,
    Chr = 0x2,
    Dir = 0x4,
    Blk = 0x6,
    Reg = 0x8,
    Lnk = 0xA,
    Sock = 0xC,
}

impl FileType {
    pub fn from_u16(v: u16) -> Option<Self> {
        match v {
            0x1 => Some(FileType::Fifo),
            0x2 => Some(FileType::Chr),
            0x4 => Some(FileType::Dir),
            0x6 => Some(FileType::Blk),
            0x8 => Some(FileType::Reg),
            0xA => Some(FileType::Lnk),
            0xC => Some(FileType::Sock),
            _ => None,
        }
    }

    pub fn to_u16(&self) -> u16 {
        *self as u16
    }
}

#[derive(Debug, Clone)]
pub struct Inode {
    pub mode: u16,
    pub uid: u16,
    pub gid: u16,
    pub size: u32,
    pub atime: u32,
    pub mtime: u32,
    pub ctime: u32,
    pub links: u16,
    pub blocks: u32,
    pub direct: [u32; DIRECT_BLOCKS],
    pub indirect: u32,
    pub double_indirect: u32,
    pub padding: u32,
}

impl Default for Inode {
    fn default() -> Self {
        Self {
            mode: 0,
            uid: 0,
            gid: 0,
            size: 0,
            atime: 0,
            mtime: 0,
            ctime: 0,
            links: 0,
            blocks: 0,
            direct: [0u32; DIRECT_BLOCKS],
            indirect: 0,
            double_indirect: 0,
            padding: 0,
        }
    }
}

impl Inode {
    pub fn new(mode: u16, uid: u16, gid: u16) -> Self {
        let now = current_time();
        Self {
            mode,
            uid,
            gid,
            size: 0,
            atime: now,
            mtime: now,
            ctime: now,
            links: 1,
            blocks: 0,
            direct: [0u32; DIRECT_BLOCKS],
            indirect: 0,
            double_indirect: 0,
            padding: 0,
        }
    }

    pub fn file_type(&self) -> Option<FileType> {
        FileType::from_u16((self.mode >> 12) & 0xF)
    }

    pub fn is_dir(&self) -> bool {
        self.file_type() == Some(FileType::Dir)
    }

    pub fn is_reg(&self) -> bool {
        self.file_type() == Some(FileType::Reg)
    }

    pub fn is_lnk(&self) -> bool {
        self.file_type() == Some(FileType::Lnk)
    }

    pub fn to_bytes(&self) -> [u8; INODE_SIZE as usize] {
        let mut buf = [0u8; INODE_SIZE as usize];
        let mut pos = 0usize;

        buf[pos..pos + 2].copy_from_slice(&self.mode.to_le_bytes());
        pos += 2;
        buf[pos..pos + 2].copy_from_slice(&self.uid.to_le_bytes());
        pos += 2;
        buf[pos..pos + 2].copy_from_slice(&self.gid.to_le_bytes());
        pos += 2;
        buf[pos..pos + 4].copy_from_slice(&self.size.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.atime.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.mtime.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.ctime.to_le_bytes());
        pos += 4;
        buf[pos..pos + 2].copy_from_slice(&self.links.to_le_bytes());
        pos += 2;
        buf[pos..pos + 4].copy_from_slice(&self.blocks.to_le_bytes());
        pos += 4;

        for &d in &self.direct {
            buf[pos..pos + 4].copy_from_slice(&d.to_le_bytes());
            pos += 4;
        }

        buf[pos..pos + 4].copy_from_slice(&self.indirect.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.double_indirect.to_le_bytes());
        pos += 4;
        buf[pos..pos + 4].copy_from_slice(&self.padding.to_le_bytes());

        buf
    }

    pub fn from_bytes(data: &[u8]) -> Self {
        let mut pos = 0usize;

        let mode = u16::from_le_bytes([data[pos], data[pos + 1]]);
        pos += 2;
        let uid = u16::from_le_bytes([data[pos], data[pos + 1]]);
        pos += 2;
        let gid = u16::from_le_bytes([data[pos], data[pos + 1]]);
        pos += 2;
        let size = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;
        let atime = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;
        let mtime = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;
        let ctime = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;
        let links = u16::from_le_bytes([data[pos], data[pos + 1]]);
        pos += 2;
        let blocks = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;

        let mut direct = [0u32; DIRECT_BLOCKS];
        for i in 0..DIRECT_BLOCKS {
            direct[i] = u32::from_le_bytes([
                data[pos],
                data[pos + 1],
                data[pos + 2],
                data[pos + 3],
            ]);
            pos += 4;
        }

        let indirect = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);
        pos += 4;
        let double_indirect = u32::from_le_bytes([
            data[pos],
            data[pos + 1],
            data[pos + 2],
            data[pos + 3],
        ]);
        pos += 4;
        let padding = u32::from_le_bytes([data[pos], data[pos + 1], data[pos + 2], data[pos + 3]]);

        Self {
            mode,
            uid,
            gid,
            size,
            atime,
            mtime,
            ctime,
            links,
            blocks,
            direct,
            indirect,
            double_indirect,
            padding,
        }
    }

    pub fn allocated_blocks(&self) -> u32 {
        self.blocks
    }

    pub fn touch(&mut self) {
        let now = current_time();
        self.atime = now;
        self.mtime = now;
    }
}

fn current_time() -> u32 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs() as u32
}

pub fn make_mode(file_type: FileType, permissions: u16) -> u16 {
    (file_type.to_u16() << 12) | (permissions & 0x1FF)
}

pub fn file_permissions(mode: u16) -> u16 {
    mode & 0x1FF
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_inode_creation() {
        let inode = Inode::new(0o100644, 1000, 1000);

        assert_eq!(inode.uid, 1000);
        assert_eq!(inode.gid, 1000);
        assert_eq!(inode.links, 1);
        assert_eq!(inode.size, 0);
        assert!(inode.is_reg());
    }

    #[test]
    fn test_inode_serialization() {
        let mut inode = Inode::new(0o40755, 1000, 1000);
        inode.direct[0] = 100;
        inode.indirect = 200;
        inode.size = 4096;

        let bytes = inode.to_bytes();
        let inode2 = Inode::from_bytes(&bytes);

        assert_eq!(inode.mode, inode2.mode);
        assert_eq!(inode.uid, inode2.uid);
        assert_eq!(inode.gid, inode2.gid);
        assert_eq!(inode.size, inode2.size);
        assert_eq!(inode.direct, inode2.direct);
        assert_eq!(inode.indirect, inode2.indirect);
    }

    #[test]
    fn test_file_type() {
        let reg_inode = Inode::new(make_mode(FileType::Reg, 0o644), 0, 0);
        let dir_inode = Inode::new(make_mode(FileType::Dir, 0o755), 0, 0);

        assert!(reg_inode.is_reg());
        assert!(!reg_inode.is_dir());
        assert!(dir_inode.is_dir());
        assert!(!dir_inode.is_reg());
    }
}