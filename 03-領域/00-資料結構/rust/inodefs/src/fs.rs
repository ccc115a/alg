use std::collections::HashMap;
use std::path::Path;

use crate::bitmaps::{BlockBitmap, InodeBitmap};
use crate::dir::{DirEntry, Directory};
use crate::disk::{BLOCK_SIZE, Disk};
use crate::error::{Error, Result};
use crate::inode::{make_mode, FileType, Inode, INODE_SIZE};
use crate::superblock::{
    INODE_TABLE_BLOCKS, INODE_TABLE_START, DATA_BLOCKS_START, Superblock,
    SUPERBLOCK_BLOCK, ROOT_INODE, INODES_PER_BLOCK,
};

pub struct InodeFs {
    disk: Disk,
    sb: Superblock,
    inode_bitmap: InodeBitmap,
    block_bitmap: BlockBitmap,
    inode_cache: HashMap<u32, Inode>,
    dir_cache: HashMap<u32, Directory>,
    modified: bool,
}

impl InodeFs {
    pub fn format(path: &Path) -> Result<Self> {
        let mut disk = Disk::create(path)?;

        let sb = Superblock::default();
        disk.write_block(SUPERBLOCK_BLOCK, &sb.to_bytes())?;

        let inode_bitmap = InodeBitmap::new();
        let block_bitmap = BlockBitmap::new();

        disk.write_block(1, &inode_bitmap.to_bytes())?;
        disk.write_block(2, &block_bitmap.to_bytes())?;

        for i in 0..INODE_TABLE_BLOCKS {
            disk.write_block(INODE_TABLE_START + i, &vec![0u8; BLOCK_SIZE as usize])?;
        }

        let mut fs = Self {
            disk,
            sb,
            inode_bitmap,
            block_bitmap,
            inode_cache: HashMap::new(),
            dir_cache: HashMap::new(),
            modified: true,
        };

        fs.init_root()?;

        Ok(fs)
    }

    fn init_root(&mut self) -> Result<()> {
        let root_inode = Inode::new(make_mode(FileType::Dir, 0o755), 0, 0);
        let ino = self.allocate_inode(root_inode)?;

        if ino != ROOT_INODE {
            return Err(Error::Corrupted(format!(
                "Root inode should be {}, got {}",
                ROOT_INODE, ino
            )));
        }

        let mut dir = Directory::new();
        dir.add_entry(DirEntry::new(ROOT_INODE, ".", FileType::Dir));
        dir.add_entry(DirEntry::new(ROOT_INODE, "..", FileType::Dir));
        self.write_directory(ROOT_INODE, &dir)?;

        self.sync()?;

        Ok(())
    }

    pub fn mount(path: &Path) -> Result<Self> {
        let mut disk = Disk::open(path)?;

        let sb_data = disk.read_block(SUPERBLOCK_BLOCK)?;
        let sb = Superblock::from_bytes(&sb_data);

        if sb.magic != 0xDF5C {
            return Err(Error::Corrupted("Invalid superblock magic".into()));
        }

        let inode_bitmap_data = disk.read_block(1)?;
        let inode_bitmap = InodeBitmap::from_bytes(inode_bitmap_data);

        let block_bitmap_data = disk.read_block(2)?;
        let block_bitmap = BlockBitmap::from_bytes(block_bitmap_data);

        let mut fs = Self {
            disk,
            sb,
            inode_bitmap,
            block_bitmap,
            inode_cache: HashMap::new(),
            dir_cache: HashMap::new(),
            modified: false,
        };

        fs.load_root_dir()?;

        Ok(fs)
    }

    fn load_root_dir(&mut self) -> Result<()> {
        let root_inode = self.read_inode(ROOT_INODE)?;
        if !root_inode.is_dir() {
            return Err(Error::Corrupted("Root is not a directory".into()));
        }
        Ok(())
    }

    fn allocate_inode(&mut self, inode: Inode) -> Result<u32> {
        let ino = self
            .inode_bitmap
            .allocate()
            .ok_or(Error::OutOfSpace)?;

        self.write_inode(ino, &inode)?;
        self.inode_cache.insert(ino, inode);
        self.sb.free_inodes -= 1;
        self.modified = true;

        Ok(ino)
    }

    pub fn create(
        &mut self,
        parent: u32,
        name: &str,
        mode: u16,
        uid: u16,
        gid: u16,
    ) -> Result<u32> {
        if self.lookup_inode(parent, name)?.is_some() {
            return Err(Error::AlreadyExists(name.into()));
        }

        let parent_inode = self.read_inode(parent)?;
        if !parent_inode.is_dir() {
            return Err(Error::NotDirectory(format!("inode {}", parent)));
        }

        let file_type = match mode & 0xF000 {
            0x4000 => FileType::Dir,
            0x8000 => FileType::Reg,
            0xA000 => FileType::Lnk,
            _ => FileType::Reg,
        };

        let inode = Inode::new(make_mode(file_type, mode & 0xFFF), uid, gid);
        let ino = self.allocate_inode(inode)?;

        self.add_dir_entry(parent, ino, name, file_type)?;

        if file_type == FileType::Dir {
            self.create_dir_entries(ino, parent)?;
        }

        self.sync()?;
        Ok(ino)
    }

    fn create_dir_entries(&mut self, ino: u32, parent: u32) -> Result<()> {
        let mut dir = Directory::new();
        dir.add_entry(DirEntry::new(ino, ".", FileType::Dir));
        dir.add_entry(DirEntry::new(parent, "..", FileType::Dir));
        self.write_directory(ino, &dir)?;

        let mut parent_dir = self.read_directory(parent)?;
        parent_dir.add_entry(DirEntry::new(ino, ".", FileType::Dir));
        parent_dir.add_entry(DirEntry::new(parent, "..", FileType::Dir));
        self.write_directory(parent, &parent_dir)?;

        Ok(())
    }

    fn add_dir_entry(
        &mut self,
        parent: u32,
        ino: u32,
        name: &str,
        file_type: FileType,
    ) -> Result<()> {
        let mut dir = self.read_directory(parent)?;
        dir.add_entry(DirEntry::new(ino, name, file_type));
        self.write_directory(parent, &dir)?;
        Ok(())
    }

    pub fn mkdir(&mut self, parent: u32, name: &str, mode: u16) -> Result<u32> {
        self.create(parent, name, 0o40755 | (mode & 0xFFF), 0, 0)
    }

    pub fn rmdir(&mut self, parent: u32, name: &str) -> Result<()> {
        let ino = self.lookup_inode(parent, name)?;
        let ino = ino.ok_or_else(|| Error::NotFound(name.into()))?;

        let dir = self.read_directory(ino)?;
        if dir.len() > 2 {
            return Err(Error::DirectoryNotEmpty);
        }

        self.remove_dir_entry(parent, name)?;
        self.free_inode(ino)?;
        self.sync()?;

        Ok(())
    }

    fn remove_dir_entry(&mut self, parent: u32, name: &str) -> Result<()> {
        let mut dir = self.read_directory(parent)?;
        dir.remove_entry(name);
        self.write_directory(parent, &dir)?;
        Ok(())
    }

    pub fn link(&mut self, old_inode: u32, parent: u32, name: &str) -> Result<u32> {
        if self.lookup_inode(parent, name)?.is_some() {
            return Err(Error::AlreadyExists(name.into()));
        }

        let mut inode = self.read_inode(old_inode)?;
        if inode.is_dir() {
            return Err(Error::IsDirectory("Cannot link directory".into()));
        }

        inode.links += 1;
        self.write_inode(old_inode, &inode)?;

        let file_type = inode.file_type().unwrap_or(FileType::Reg);
        self.add_dir_entry(parent, old_inode, name, file_type)?;

        self.sync()?;
        Ok(old_inode)
    }

    pub fn unlink(&mut self, parent: u32, name: &str) -> Result<()> {
        let ino = self.lookup_inode(parent, name)?;
        let ino = ino.ok_or_else(|| Error::NotFound(name.into()))?;

        let inode = self.read_inode(ino)?;
        if inode.is_dir() {
            return Err(Error::IsDirectory("Cannot unlink directory".into()));
        }

        let mut inode = self.read_inode(ino)?;
        inode.links -= 1;
        if inode.links == 0 {
            self.free_inode(ino)?;
        } else {
            self.write_inode(ino, &inode)?;
        }

        self.remove_dir_entry(parent, name)?;
        self.sync()?;

        Ok(())
    }

    fn free_inode(&mut self, ino: u32) -> Result<()> {
        let inode = self.read_inode(ino)?;

        for &block in &inode.direct {
            if block != 0 {
                self.block_bitmap.free(block, DATA_BLOCKS_START);
            }
        }

        self.inode_bitmap.free(ino);
        self.inode_cache.remove(&ino);
        self.dir_cache.remove(&ino);
        self.modified = true;

        Ok(())
    }

    pub fn lookup_inode(&mut self, parent: u32, name: &str) -> Result<Option<u32>> {
        if name.is_empty() {
            return Ok(Some(parent));
        }

        let dir = self.read_directory(parent)?;
        Ok(dir.find_inode(name))
    }

    pub fn read_inode(&mut self, ino: u32) -> Result<Inode> {
        if ino == 0 {
            return Err(Error::InvalidInode(ino));
        }

        if let Some(inode) = self.inode_cache.get(&ino).cloned() {
            return Ok(inode);
        }

        let block_offset = (ino - 1) / INODES_PER_BLOCK;
        let block_num = INODE_TABLE_START + block_offset;
        let block_data = self.disk.read_block(block_num)?;

        let offset = ((ino - 1) % INODES_PER_BLOCK) as usize * INODE_SIZE as usize;
        let inode_data = &block_data[offset..offset + INODE_SIZE as usize];
        let inode = Inode::from_bytes(inode_data);

        self.inode_cache.insert(ino, inode.clone());
        Ok(inode)
    }

    fn write_inode(&mut self, ino: u32, inode: &Inode) -> Result<()> {
        let block_offset = (ino - 1) / INODES_PER_BLOCK;
        let block_num = INODE_TABLE_START + block_offset;
        let mut block_data = self.disk.read_block(block_num)?;

        let offset = ((ino - 1) % INODES_PER_BLOCK) as usize * INODE_SIZE as usize;
        let inode_bytes = inode.to_bytes();
        block_data[offset..offset + INODE_SIZE as usize].copy_from_slice(&inode_bytes);

        self.disk.write_block(block_num, &block_data)?;
        self.inode_cache.insert(ino, inode.clone());
        self.modified = true;

        Ok(())
    }

    pub fn read_directory(&mut self, ino: u32) -> Result<Directory> {
        if let Some(dir) = self.dir_cache.get(&ino).cloned() {
            return Ok(dir);
        }

        let inode = self.read_inode(ino)?;
        if !inode.is_dir() {
            return Err(Error::NotDirectory(format!("inode {}", ino)));
        }

        let data = self.read_file_data(&inode)?;
        let dir = Directory::from_inode_content(&data);

        self.dir_cache.insert(ino, dir.clone());
        Ok(dir)
    }

    fn write_directory(&mut self, ino: u32, dir: &Directory) -> Result<()> {
        let data = dir.to_bytes();
        self.write_file_data(ino, &data)?;
        self.dir_cache.insert(ino, dir.clone());
        Ok(())
    }

    fn read_file_data(&mut self, inode: &Inode) -> Result<Vec<u8>> {
        let mut result = Vec::new();
        let mut remaining = inode.size as usize;

        for &block_num in &inode.direct {
            if block_num == 0 || remaining == 0 {
                break;
            }
            let data = self.disk.read_block(block_num)?;
            let to_read = remaining.min(BLOCK_SIZE as usize);
            result.extend(&data[..to_read]);
            remaining -= to_read;
        }

        Ok(result)
    }

    fn write_file_data(&mut self, ino: u32, data: &[u8]) -> Result<()> {
        let mut inode = self.read_inode(ino)?;

        for &block_num in &inode.direct {
            if block_num != 0 {
                self.block_bitmap.free(block_num, DATA_BLOCKS_START);
            }
        }

        let blocks_needed = (data.len() as u32 + BLOCK_SIZE - 1) / BLOCK_SIZE;
        let mut blocks_allocated = 0u32;
        let mut block_nums = Vec::new();

        while blocks_allocated < blocks_needed && blocks_allocated < inode.direct.len() as u32 {
            if let Some(block) = self.block_bitmap.allocate(DATA_BLOCKS_START) {
                block_nums.push(block);
                blocks_allocated += 1;
            } else {
                break;
            }
        }

        for (i, &block) in block_nums.iter().enumerate() {
            inode.direct[i] = block;
        }

        for i in blocks_allocated as usize..inode.direct.len() {
            inode.direct[i] = 0;
        }

        inode.size = data.len() as u32;
        inode.blocks = blocks_allocated;
        inode.touch();

        let mut offset = 0;
        for &block_num in &block_nums {
            let start = offset;
            let end = (offset + BLOCK_SIZE as usize).min(data.len());
            let mut block_data = vec![0u8; BLOCK_SIZE as usize];
            block_data[..end - start].copy_from_slice(&data[start..end]);
            self.disk.write_block(block_num, &block_data)?;
            offset = end;
        }

        self.write_inode(ino, &inode)?;
        self.modified = true;

        Ok(())
    }

    pub fn read(&mut self, ino: u32, offset: u32, buf: &mut [u8]) -> Result<u32> {
        let inode = self.read_inode(ino)?;

        if offset >= inode.size {
            return Ok(0);
        }

        let data = self.read_file_data(&inode)?;
        let available = (inode.size - offset) as usize;
        let to_read = available.min(buf.len()).min(data.len() - offset as usize);

        buf[..to_read].copy_from_slice(&data[offset as usize..][..to_read]);
        Ok(to_read as u32)
    }

    pub fn write(&mut self, ino: u32, offset: u32, data: &[u8]) -> Result<u32> {
        let inode = self.read_inode(ino)?;

        if !inode.is_reg() {
            return Err(Error::NotSupported("Cannot write to non-regular file".into()));
        }

        let mut file_data = self.read_file_data(&inode)?;
        let required_size = offset as usize + data.len();

        if required_size > file_data.len() {
            file_data.resize(required_size, 0);
        }

        file_data[offset as usize..offset as usize + data.len()].copy_from_slice(data);
        self.write_file_data(ino, &file_data)?;

        self.sync()?;
        Ok(data.len() as u32)
    }

    pub fn truncate(&mut self, ino: u32, _size: u32) -> Result<()> {
        let _inode = self.read_inode(ino)?;
        self.write_file_data(ino, &[])?;
        self.sync()?;
        Ok(())
    }

    pub fn stat(&mut self, ino: u32) -> Result<FileStat> {
        let inode = self.read_inode(ino)?;
        Ok(FileStat {
            ino,
            mode: inode.mode,
            uid: inode.uid,
            gid: inode.gid,
            size: inode.size,
            atime: inode.atime,
            mtime: inode.mtime,
            ctime: inode.ctime,
            links: inode.links,
            blocks: inode.blocks,
        })
    }

    pub fn chmod(&mut self, ino: u32, mode: u16) -> Result<()> {
        let mut inode = self.read_inode(ino)?;
        inode.mode = (inode.mode & 0xF000) | (mode & 0xFFF);
        inode.ctime = current_time();
        self.write_inode(ino, &inode)?;
        self.sync()?;
        Ok(())
    }

    pub fn root(&self) -> u32 {
        ROOT_INODE
    }

    pub fn sync(&mut self) -> Result<()> {
        if self.modified {
            let mut block_inodes: HashMap<u32, Vec<(u32, Inode)>> = HashMap::new();

            for (&ino, inode) in &self.inode_cache {
                let block_num = INODE_TABLE_START + (ino - 1) / INODES_PER_BLOCK;
                block_inodes.entry(block_num).or_default().push((ino, inode.clone()));
            }

            for (block_num, inodes) in block_inodes {
                let mut buf = self.disk.read_block(block_num)?;
                for (ino, inode) in inodes {
                    let offset = ((ino - 1) % INODES_PER_BLOCK) as usize * INODE_SIZE as usize;
                    let inode_bytes = inode.to_bytes();
                    buf[offset..offset + INODE_SIZE as usize].copy_from_slice(&inode_bytes);
                }
                self.disk.write_block(block_num, &buf)?;
            }

            self.disk.write_block(1, &self.inode_bitmap.to_bytes())?;
            self.disk.write_block(2, &self.block_bitmap.to_bytes())?;
            self.modified = false;
        }
        self.disk.sync()?;
        Ok(())
    }
}

fn current_time() -> u32 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs() as u32
}

#[derive(Debug, Clone)]
pub struct FileStat {
    pub ino: u32,
    pub mode: u16,
    pub uid: u16,
    pub gid: u16,
    pub size: u32,
    pub atime: u32,
    pub mtime: u32,
    pub ctime: u32,
    pub links: u16,
    pub blocks: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_format_and_mount() {
        let path = std::env::temp_dir().join("test_inodefs.img");
        std::fs::remove_file(&path).ok();

        {
            let fs = InodeFs::format(&path).unwrap();
            assert_eq!(fs.root(), ROOT_INODE);
        }

        {
            let fs = InodeFs::mount(&path).unwrap();
            assert_eq!(fs.root(), ROOT_INODE);
        }

        std::fs::remove_file(&path).ok();
    }

    #[test]
    fn test_create_and_lookup() {
        let path = std::env::temp_dir().join("test_inodefs2.img");
        std::fs::remove_file(&path).ok();

        {
            let mut fs = InodeFs::format(&path).unwrap();
            let ino = fs.create(ROOT_INODE, "test.txt", 0o644, 0, 0).unwrap();
            assert_eq!(ino, 2);

            let found = fs.lookup_inode(ROOT_INODE, "test.txt").unwrap();
            assert_eq!(found, Some(ino));
        }

        std::fs::remove_file(&path).ok();
    }

    #[test]
    fn test_mkdir_and_rmdir() {
        let path = std::env::temp_dir().join("test_inodefs3.img");
        std::fs::remove_file(&path).ok();

        {
            let mut fs = InodeFs::format(&path).unwrap();
            let dir_ino = fs.mkdir(ROOT_INODE, "mydir", 0o755).unwrap();
            assert!(dir_ino > ROOT_INODE);

            let found = fs.lookup_inode(ROOT_INODE, "mydir").unwrap();
            assert_eq!(found, Some(dir_ino));

            fs.rmdir(ROOT_INODE, "mydir").unwrap();
            let found = fs.lookup_inode(ROOT_INODE, "mydir").unwrap();
            assert_eq!(found, None);
        }

        std::fs::remove_file(&path).ok();
    }

    #[test]
    fn test_write_and_read() {
        let path = std::env::temp_dir().join("test_inodefs4.img");
        std::fs::remove_file(&path).ok();

        {
            let mut fs = InodeFs::format(&path).unwrap();
            let ino = fs.create(ROOT_INODE, "data.txt", 0o644, 0, 0).unwrap();

            fs.write(ino, 0, b"Hello, InodeFS!").unwrap();

            let mut buf = [0u8; 1024];
            let n = fs.read(ino, 0, &mut buf).unwrap();
            assert_eq!(&buf[..n as usize], b"Hello, InodeFS!");
        }

        std::fs::remove_file(&path).ok();
    }

    #[test]
    fn test_link_and_unlink() {
        let path = std::env::temp_dir().join("test_inodefs5.img");
        std::fs::remove_file(&path).ok();

        {
            let mut fs = InodeFs::format(&path).unwrap();
            let ino = fs.create(ROOT_INODE, "original.txt", 0o644, 0, 0).unwrap();
            fs.write(ino, 0, b"content").unwrap();

            fs.link(ino, ROOT_INODE, "hardlink.txt").unwrap();

            let mut buf = [0u8; 1024];
            let n = fs.read(ino, 0, &mut buf).unwrap();
            assert_eq!(&buf[..n as usize], b"content");

            fs.unlink(ROOT_INODE, "hardlink.txt").unwrap();
            let found = fs.lookup_inode(ROOT_INODE, "hardlink.txt").unwrap();
            assert_eq!(found, None);
        }

        std::fs::remove_file(&path).ok();
    }
}