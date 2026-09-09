# db6 待辦事項

msgq/ Message Queye (redis)

redis 的功能，有什麼 db6/kv 沒做的呢？


## KV 適用功能（ LSM / Hash / BTreeMemory ）

### v3.7 - JSON 過濾支援 (已完成)
- [x] JSON 路徑過濾 ($.field > 25)
- [x] 支援 =, !=, >, <, >=, <=, LIKE
- [x] 支援巢狀路徑 ($.address.city)
- [x] filter() 和 where_() 兩者皆可使用

### v3.8 - 效能優化
- [ ] 查詢緩存
- [ ] 批次操作優化

### v3.9 - 索引加速
- [x] create_index / drop_index
- [ ] 索引掃描

### v3.10 - 資料庫管理
- [ ] VACUUM
- [ ] ANALYZE
- [ ] BACKUP

### v3.11 - 效能監控
- [ ] 引擎統計 (stats)
- [ ] 查詢規劃 (.explain)

### v3.12 - CLI 強化
- [ ] .db stats
- [ ] .indexes

### v3.13 - 緩存改進
- [ ] 可設定緩存大小
- [ ] WAL 支援

---

## SQL 適用功能（BTree / 需要復雜查詢規劃）

這些適合 SQL 的功能只要針對 BTree 版本（LSM tree 和 Hash 不用支援  JOIN ORDER BY）

如果有錯很難解決，你嘗試幾次卻無法解決，不用硬做，直接留著錯誤 (test.sh) 告訴我現況，我讓 gemini 來解

### v3.14 - JOIN 支援
- [x] JoinQuery 結構
- [x] INNER JOIN / LEFT JOIN

### v3.15 - SQL Executor 完整實作
- [x] INSERT executor
- [x] SELECT executor
- [x] UPDATE executor
- [x] DELETE executor

### v3.16 - 子查詢 (Subquery)
- [x] IN subquery
- [x] EXISTS subquery

### v3.17 - 視圖 (View)
- [ ] create_view / drop_view
- [ ] 視圖查詢

### v3.18 - 事務隔離級別
- [ ] Read Committed
- [ ] Serializable

### v3.19 - 進階聚合
- [ ] COUNT(DISTINCT)
- [ ] STRING_AGG
- [ ] PERCENTILE

### v3.20 - 窗口函數
- [ ] ROW_NUMBER
- [ ] RANK
- [ ] AVG OVER

### v3.21 - CTE
- [ ] WITH clause
- [ ] RECURSIVE CTE

### v3.22 - 儲存過程
- [ ] create_function
- [ ] 函數註冊

### v3.23 - 分區表 (Partitioning)
- [ ] RANGE partition
- [ ] LIST partition

### v3.24 - 介面統一化
- [ ] SQLite 相容
- [ ] PostgreSQL 相容

---

## 持續改進
- [ ] 效能微調
- [ ] Bug 修復
- [ ] 文檔完善