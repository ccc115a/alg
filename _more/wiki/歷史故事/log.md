# 日誌

## [2026-04] migrate | 歷史故事重組

- 由 `story/_wiki/` 遷入 45 個電腦史故事頁
- 由 `故事/` 遷入 6 篇深入專題（Lambda 演算、LISP 誕生、eval、拜占庭、雷神之鎚）+ 45 故事清單 README
- 遷入 lispEval 的 C/Python 實作與編譯/執行說明
- 遷入 `categories/`（12 個分類頁）與 `concepts/`（14 個概念頁）作為跨主題索引
- 建立本目錄 index.md
- 各故事頁內部連結已依新位置重寫

## [2026-09] cleanup | 只留歷史故事、檔名中文化

- 移除非故事內容：`categories/`、`concepts/`、`lispEval*` 程式與說明、README、5 篇中文補充專題（LISP 誕生、eval、Lambda、拜占庭、雷神之鎚）
- 45 篇英文 slug 故事檔案全改為中文檔名（如 `bitcoin.md` → `比特幣.md`）
- 各故事頁內部連結同步改為中文檔名；失效的 categories/concepts 連結已剝除為純文字
- 重寫 index.md

