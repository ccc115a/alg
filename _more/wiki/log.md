# 日誌

## [2026-09-09] init | 建立全域骨架

- 建立根目錄 `AGENTS.md`（LLM Wiki 操作手冊）
- 建立全域 `index.md` 與 `log.md`
- 建立 `source/` 結構（`目錄說明.md` + 五個分類子目錄）
- 各分類 `index.md` / `log.md` 已齊備

## [2026-09-09] rename | 檔名中文化

### 歷史故事/（只留歷史故事）
- 移除非故事內容：`categories/`、`concepts/`、`lispEval*`、README、5 篇中文補充專題
- 45 篇英文 slug 故事全改為中文檔名（如 `bitcoin.md` → `比特幣.md`）
- 同步修正全 wiki 中指向已刪除 categories/concepts 的 95 個失效連結

### 資料結構/
- 英文檔名改為中文（保留專有名詞）：
  - `linked-list.md` → `鏈結串列.md`、`b-tree.md` → `B樹.md`、`red-black-tree.md` → `紅黑樹.md`
  - `skip-list.md` → `跳過表.md`、`bloom-filter.md` → `布隆濾波器.md`
  - `lsm-tree.md` → `LSM樹.md`、`patricia-trie.md` → `Patricia樹.md`、`swisstable.md` → `swiss表.md`
  - `inverted-index.md` → `反向索引.md`、`database-engine.md` → `資料庫引擎.md`
- `inode.md` 保留原名（專有名詞）

## [2026-09-09] add | 補齊資料結構技術主題

- 依 `03-領域/00-資料結構/rust/` 涵蓋的主題，新增技術解說頁（純原理、不引用程式）：
  - inode、Patricia樹、swiss表、LSM樹、反向索引、資料庫引擎
- 更新 資料結構/index.md 加入「技術解說」區

## migrate | 整合故事入 _wiki/

- 由 `story/_wiki/` 遷入演算法/數學/計算理論/資料結構故事頁，由 `故事/` 遷入歷史故事
- 移除 `_more/故事/` 與 `_more/story/`，`_more/` 只保留 `_wiki/`
- 依主題分發：歷史(45)→歷史故事、資料結構(5)→資料結構、數值/幾何(7)→數學、np-completeness→計算理論、其餘(34)→演算法
