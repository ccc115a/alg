# 日誌

## [2026-04] migrate | 建立資料結構故事目錄

- 由 `story/_wiki/algorithms/` 遷入 5 個資料結構故事頁（連結串列、B-Tree、Bloom Filter、紅黑樹、跳過表）
- 建立本目錄 index.md
- 故事頁內部連結已依新位置重寫

## [2026-09] add | 補齊技術解說主題

- 依 `03-領域/00-資料結構/rust/` 專案涵蓋的主題，新增技術解說頁（純原理、不引用程式）：
  - [inode](inode.md)、[patricia-trie](Patricia樹.md)、[swisstable](swiss表.md)、[lsm-tree](LSM樹.md)、[inverted-index](反向索引.md)、[database-engine](資料庫引擎.md)
- 更新 index.md 加入「技術解說」區

## [2026-09] rename | 檔名中文化（不過度翻譯）

- 英文檔名改為中文，保留專有名詞：
  - `b-tree.md` → `B樹.md`、`red-black-tree.md` → `紅黑樹.md`、`skip-list.md` → `跳過表.md`
  - `linked-list.md` → `鏈結串列.md`、`bloom-filter.md` → `布隆濾波器.md`
  - `lsm-tree.md` → `LSM樹.md`、`patricia-trie.md` → `Patricia樹.md`、`swisstable.md` → `swiss表.md`
  - `inverted-index.md` → `反向索引.md`、`database-engine.md` → `資料庫引擎.md`
  - `inode.md` 保留原名（專有名詞）
- 目錄內所有連結同步更新


