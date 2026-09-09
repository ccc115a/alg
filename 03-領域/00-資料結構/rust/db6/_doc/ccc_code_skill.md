# 陳鍾誠的寫程式專屬 skill

1. 必須要寫詳細的單元測試，還有系統測試
    * 如果是網站，必須對 server api 測試，還要使用 Playwright 對網站進行 e2e 測試。
2. 測試框架
    * python 使用 pytest
    * rust 使用 cargo test
    * 必須寫一個 test.sh 做專案測試
3. 程式規範
    * 必須經過 lint 格式檢查與自動格式化（python 使用 ruff）
    * 程式超過 1000 行，就要分成兩個檔案模組。
4. 規劃寫在 _doc/ 下，每一個版本都要寫出 vx.y.md 
    * 例如： v0.1.md v0.2.md ....v 1.1.md
    * 每次進版基本上都前進 0.1 版
5. 語法必須修改到沒有 warning 
    * 如果是 rust ，可以用 #![allow(dead_code, unused)]
    * 如果是 C 必須改到沒 warning.
6. 所有路徑都應該使用相對路徑，要跨平台能運作的 
    * 不能使用 /xxx/.... 這樣的路徑，應該使用 ../ ./ 這樣的路徑

## 工具呼叫穩定性協議（防止生成中斷）
- 當你透過類似 `<invoke name="edit">` 的方法進行大規模的程式碼修改時，如果預估程式碼內容可能會接近你的單次最大輸出 Token 限制（max output token limit），**請絕對不要嘗試一次發送整塊龐大的程式碼**。
- 相反地，請執行**「分段與心跳（Split-and-Heartbeat）」模式**：將你的修改拆分成多個較小的 `<invoke>` 區塊分批執行。
- 當使用者或終端機介面輸入 `go` 之後，請立刻從剛才在中斷處 `<parameter name="newString">` 內留下的最後一個字元，完全無縫地繼續往下生成。