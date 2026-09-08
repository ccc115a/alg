# story/AGENTS.md

演算法故事 Wiki（陳鍾誠《演算法》課程的補充教材）。內容為繁體中文。源料位於 `chat.md`、`list.md`；成品位於 `wiki/`。

## 產物結構

- `wiki/algorithms/` — 故事頁（每個演算法/事故一頁）
- `wiki/concepts/` — 概念頁（圖論、密碼學、機器學習等）
- `wiki/categories/` — 主題分類頁（如 `history.md`），內含指向 algorithms 頁的連結表
- `wiki/index.md` — 主索引（分類表 + 全部分組故事清單）；新增頁面後必須同步更新
- `wiki/log.md` — 變更日誌，每次 ingest 一筆條目

## 最高原則：GitHub 相容連結

**禁止 Obsidian `[[wiki-links]]` 語法** — GitHub 上無法顯示。一律用相對 markdown 連結：

- `algorithms/` 內跨頁：`[文字](sibling.md)`
- 從 `algorithms/` 到概念/分類：`[文字](../concepts/xxx.md)`、`[文字](../categories/xxx.md)`
- 從 `categories/` 到故事：`[文字](../algorithms/xxx.md)`
- 目標必須存在；不要用指向目錄本身的 `](..)` 或 `](.)`

## 每頁格式

```
# 標題（含趣味點摘要）

**領域**：[數理邏輯與電腦史](../categories/history.md) | **年代**：yyyy | **主角**：（可選）

**趣味點**：一句話說出最有趣的地方（粗體強調笑點/反轉）

敘事正文 > 延伸閱讀：[其他頁](xxx.md)、[概念](../concepts/yyy.md)
```

## 驗證：新增/修改後必跑

`index.md` 檢查連結 + 全站相對連結檢查：

```bash
python3 - <<'EOF'
import os, re, glob
bad = []
for f in glob.glob("wiki/**/*.md", recursive=True):
    base = os.path.dirname(f)
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", open(f, encoding="utf-8").read()):
        t = m.group(1).strip()
        if t.startswith("http") or t.startswith("#"):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, t))):
            bad.append((f, t))
print("All relative links OK" if not bad else "\n".join(f"BROKEN: {f} -> {t}" for f, t in bad))
EOF
```

## 注意

- 故事要「趣味點」優先、像說故事，不要寫成教科書定義；跨頁以「延伸閱讀」互連。
- 新增故事頁同時更新 `wiki/index.md` 與 `wiki/log.md`（每次 ingest 一條）。
- 既有子專案（如 `04-理論/02-數學/_ai/*`）有自己的 `AGENTS.md`，勿混入本目錄。