# AGENTS.md — 演算法教材 (alg)

Course textbook repo for 金門大學資訊工程系《演算法》(115 學年下學期). All prose is in Traditional Chinese.

## Structure

| Dir | Content |
|-----|---------|
| `01-複雜度/` | Big-O, recursion relations |
| `02-方法/` | Algorithm methods (brute-force, DP, greedy, divide & conquer, etc.) |
| `03-領域/` | Application domains (strings, images, crypto, graph, EDA, etc.) |
| `04-理論/` | Theory (computational theory + mathematics: calculus, linear algebra, Fourier, geometry, etc.) |
| `_more/_wiki/` | Supplementary wiki (concept pages + history stories: `數學/`, `演算法/`, `計算理論/`, `資料結構/`, `歷史故事/`) |

## Sub-projects with their own tests

Several directories are standalone Python packages. Each has its own `AGENTS.md`, `pyproject.toml`/`setup.py`, `test.sh`, and `tests/`.

- `04-理論/02-數學/_ai/lean4py/` — logic/prover library. `pip install -e . && pytest tests/`
- `04-理論/02-數學/05-機率統計/statr/` — R-style stats library. `pip install -e ".[dev]" && pytest`
- `04-理論/02-數學/04-微積分/_ccc/02-梯度優化/05-torchdiy/_more/v*/` — progressive dtorch implementations (v2loss → v7torch0). `PYTHONPATH=. pytest -v` from the project root.

When editing a sub-project, check its own `AGENTS.md` first. Do not mix sub-project rules into this root file.

## Conventions

- Content is Traditional Chinese (繁體中文). Match the language of surrounding files.
- Markdown files are the primary content; Python files are examples/demos, not production code.
- Most Python scripts are standalone (run directly with `python script.py`), not imported as a package.
- Directory numbering (`01-`, `02-`, …) controls display/topic order.
- `_bak/` and `_more/` are scratch/supplementary; `_chat/` holds AI conversation logs.
- `_ccc/` marks instructor-authored code; `_ai/` marks AI-assisted code.

## Link rules (for `_wiki/`)

No Obsidian `[[wiki-links]]` — GitHub cannot render them. Use relative markdown links. `歷史故事/` holds only the 45 algorithm/computer-history stories (all Chinese filenames, e.g. `比特幣.md`); the `categories/` + `concepts/` indexers were removed. Each story file links to sibling stories and topic pages (`演算法/`, `數學/`, `計算理論/`, `資料結構/`) via relative paths. Run the relative-link validator (pattern: regex `\[[^\]]*\]\(([^)]+)\)` over `_wiki/**/*.md`) after adding pages. Note: many pre-existing `數學/` concept pages contain broken cross-links to files not in this repo — do not assume those are regression.

## Gotchas

- No root-level `pyproject.toml` or `package.json`. There is no single test/lint command for the whole repo. Tests are per-sub-project.
- `.DS_Store` files exist but are not tracked in a meaningful way.
- Some test files have `._bak` suffix (e.g., `test_rnn.py._bak`) — these are disabled/incomplete, not runnable.
- File and directory names use Chinese characters. Be careful with quoting in shell commands: always quote paths.
