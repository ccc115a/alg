# InodeFS — 磁碟式虛擬檔案系統

## 概述

InodeFS 是一個基於 UNIX/Linux inode 結構的虛擬檔案系統，所有資料儲存在單一個磁碟映像檔案中。

## 核心概念

### Inode (Index Node)

每個檔案/目錄都有一個對應的 inode 結構：

```text
┌─────────────────────────────────────────────┐
│  Inode Structure                            │
├─────────────────────────────────────────────┤
│  mode        : 檔案類型與權限 (u16)         │
│  uid         : 擁有者 ID (u16)              │
│  gid         : 群組 ID (u16)                │
│  size        : 檔案大小 (u32)               │
│  atime       : 最後存取時間 (u32)           │
│  mtime       : 最後修改時間 (u32)           │
│  ctime       : inode 變更時間 (u32)         │
│  links       : 連結數 (u16)                  │
│  blocks      : 直接/間接區塊數 (u32)         │
│  direct[10]  : 10 個直接區塊指標            │
│  indirect    : 單間接區塊指標                │
│  double_ind  : 雙間接區塊指標                │
└─────────────────────────────────────────────┘
```

### 超區塊 (Superblock)

位於磁碟開頭，包含檔案系統元資料：

```text
┌─────────────────────────────────────────────┐
│  Superblock Structure                       │
├─────────────────────────────────────────────┤
│  magic     : 魔術數字 0xDF5C (u16)          │
│  version   : 版本號 (u16)                   │
│  block_size: 區塊大小位元組 (u32)            │
│  total_blocks: 總區塊數 (u32)               │
│  free_blocks: 剩餘區塊數 (u32)              │
│  inode_count: inode 總數 (u32)              │
│  free_inodes: 剩餘 inode 數 (u32)           │
│  root_inode: 根目錄 inode 編號 (u32)        │
│  first_bitmap: inode bitmap 區塊 (u32)      │
│  block_bitmap: 區塊 bitmap 區塊 (u32)       │
└─────────────────────────────────────────────┘
```

### 目錄結構

目錄是一種特殊檔案，其內容是目錄項目的線性列表：

```text
┌─────────────────────────────────────────────┐
│  Directory Entry                            │
├─────────────────────────────────────────────┤
│  inode    : inode 編號 (u32)               │
│  name_len : 名稱長度 (u8)                   │
│  file_type: 檔案類型 (u8)                   │
│  name     : 檔案名稱 (name_len bytes)       │
└─────────────────────────────────────────────┘
```

### 區塊分配策略

- **區塊Bitmap**: 追蹤每個資料區塊的使用狀態
- **InodeBitmap**: 追蹤每個 inode 的使用狀態
- **首次適應 (First Fit)**: 配置時從頭搜尋可用空間

## 磁碟配置

```
+------------------+
|   Superblock     |  Block 0
+------------------+
|   Inode Bitmap   |  Block 1
+------------------+
|   Block Bitmap   |  Block 2
+------------------+
|   Inode Table    |  Blocks 3 ~ 66
|   (64 inodes)    |
+------------------+
|   Data Blocks    |  Blocks 67 ~
+------------------+
```

預設配置：
- 區塊大小: 1024 bytes
- inode 數量: 64
- 總區塊數: 1024
- 總容量: 1 MB

## 檔案類型

| Type   | Value | Description |
|--------|-------|-------------|
| FIFO   | 0x1   | 命名管道    |
| CHR    | 0x2   | 字元設備    |
| DIR    | 0x4   | 目錄        |
| BLK    | 0x6   | 區塊設備    |
| REG    | 0x8   |  regular file|
| LNK    | 0xA   | 符號連結    |
| SOCK   | 0xC   | Socket      |

## 權限位元

```
rwxrwxrwx
└┬─┴─┬─┴─┬─┴─┬─┬─┬─┬─ Other
 │   │   │   │ │ │ └─ Write
 │   │   │   │ │ └─── Read
 │   │   │   │ └──── Execute
 │   │   │   └────── Group
 │   │   └────────── Write
 │   └────────────── Execute
 └────────────────── Owner
```

## API 設計

### 核心操作

```rust
// 檔案系統操作
pub fn format(disk: &Path) -> Result<()>
pub fn mount(disk: &Path) -> Result<InodeFs>

// inode 操作
pub fn create_inode(&mut self, mode: u16, uid: u16, gid: u16) -> Result<u32>
pub fn get_inode(&self, ino: u32) -> Result<Inode>
pub fn put_inode(&mut self, ino: u32, inode: &Inode) -> Result<()>

// 資料操作
pub fn read(&self, ino: u32, offset: u32, buf: &mut [u8]) -> Result<u32>
pub fn write(&mut self, ino: u32, offset: u32, data: &[u8]) -> Result<u32>
pub fn truncate(&mut self, ino: u32, size: u32) -> Result<()>

// 目錄操作
pub fn mkdir(&mut self, parent: u32, name: &str, mode: u16) -> Result<u32>
pub fn rmdir(&mut self, parent: u32, name: &str) -> Result<()>
pub fn link(&mut self, old_inode: u32, parent: u32, name: &str) -> Result<u32>
pub fn unlink(&mut self, parent: u32, name: &str) -> Result<()>

// 屬性操作
pub fn stat(&self, ino: u32) -> Result<FileStat>
pub fn chmod(&mut self, ino: u32, mode: u16) -> Result<()>
pub fn chown(&mut self, ino: u32, uid: u16, gid: u16) -> Result<()>
```

### 目錄讀取

```rust
pub fn readdir(&self, ino: u32) -> Result<Vec<DirEntry>>
```

## 使用範例

```rust
use inodefs::{InodeFs, FileType};

// 格式化新磁碟
InodeFs::format("/tmp/vdisk.img")?;

// 掛載檔案系統
let mut fs = InodeFs::mount("/tmp/vdisk.img")?;

// 建立目錄
let root = fs.root();
fs.mkdir(root, "home", 0o755)?;

// 建立檔案
let home = fs.lookup(root, "home")?;
let file_ino = fs.create(home, "readme.txt", 0o644)?;

// 寫入資料
fs.write(file_ino, 0, b"Hello, InodeFS!")?;

// 讀取資料
let mut buf = [0u8; 1024];
let n = fs.read(file_ino, 0, &mut buf)?;
println!("Read: {}", String::from_utf8_lossy(&buf[..n]));

// 創建子目錄
fs.mkdir(home, "user", 0o755)?;

// 建立符號連結
fs.symlink(home, "link_to_readme", file_ino)?;
```

## 限制與未來擴展

### 目前限制
- 固定磁碟大小（1MB）
- 無磨損層級 (wear leveling)
- 無 journaling
- 無權限檢查

### 未來擴展
- [ ] 動態磁碟大小
- [ ] 日誌功能
- [ ] 壓縮支援
- [ ] 加密支援
- [ ] 權限檢查
- [ ] 連結計數器管理
- [ ] 區塊回收機制