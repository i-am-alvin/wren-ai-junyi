# WrenAI Docker 部署與資料匯入指南

## 🚨 重要提醒：正確的資料匯入方法

### ❌ 錯誤做法 - 直接寫入 Qdrant
```bash
# 這是錯誤的做法！不要直接操作 Qdrant
docker exec container python direct_qdrant_import.py  # ❌ 錯誤
```

**問題**：
- 直接寫入 Qdrant 的資料不會出現在 UI 中
- 資料不一致，無法在介面中管理
- 向量大小配置錯誤會導致匯入失敗

### ✅ 正確做法 - 透過 UI API
```bash
# 這是正確的做法！
python3 scripts/import_instructions_via_ui.py     # ✅ 正確
python3 scripts/import_csv_sql_pairs.py           # ✅ 正確
```

**優點**：
- UI 和 Qdrant 自動同步
- 可在介面中查看和管理
- WrenAI 自動處理向量化

## 📋 快速開始

### 1. 啟動 WrenAI
```bash
docker-compose up -d
```

### 2. 匯入 Instructions
```bash
cd docker
python3 scripts/import_instructions_via_ui.py
```

### 3. 匯入 SQL Pairs
```bash
python3 scripts/import_csv_sql_pairs.py
```

### 4. 驗證匯入結果
```bash
# 檢查 UI 中的資料
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id instruction isDefault } sqlPairs { id question } }"}' \
  | python -m json.tool
```

## 🏗️ 系統架構理解

WrenAI 使用**雙層資料架構**：

```
UI GraphQL API ──→ UI Database (SQLite) ──→ WrenAI Service ──→ Qdrant (向量庫)
     ↑                    ↑                       ↑                ↑
   正確入口          儲存 metadata           自動處理          自動向量化
```

## 📁 檔案結構

```
docker/
├── README.md                              # 本文件
├── docs/
│   ├── import.md                         # 詳細匯入指南
│   └── storage.md                        # 儲存架構說明
├── scripts/
│   ├── import_instructions_via_ui.py     # ✅ 正確的 Instructions 匯入
│   ├── import_csv_sql_pairs.py           # ✅ 正確的 SQL Pairs 匯入
│   ├── verify_import.py                  # 驗證匯入結果
│   └── [deprecated]
│       ├── import_instructions.py        # ❌ 已廢棄 - 直接寫 Qdrant
│       └── simple_import.py              # ❌ 已廢棄 - 直接寫 Qdrant
└── data/
    ├── instructions.csv                   # Instructions 資料
    └── sql_pairs.csv                      # SQL Pairs 資料
```

## 🔍 驗證清單

匯入完成後，請確認：

- [ ] UI 中可以看到 Instructions (`http://localhost:3000`)
- [ ] UI 中可以看到 SQL Pairs
- [ ] Qdrant 中有對應的向量資料
- [ ] AI 查詢時能正確套用 Instructions

## 📚 相關文檔

- [詳細匯入指南](docs/import.md)
- [儲存架構說明](docs/storage.md)
- [WrenAI 官方文檔](https://docs.getwren.ai)

## 🆘 故障排除

### 問題：UI 中看不到匯入的資料
**解決**：確認使用正確的 UI API 匯入方法，不要直接操作 Qdrant

### 問題：向量大小錯誤
**解決**：WrenAI 使用 3072 維向量，讓系統自動處理，不要手動創建集合

### 問題：GraphQL API 錯誤
**解決**：檢查 WrenAI UI 服務是否正常運行：
```bash
docker ps | grep wren-ui
curl http://localhost:3000/api/graphql
```

---

⚠️ **記住**：永遠透過 UI API 匯入資料，讓 WrenAI 自動處理向量化！
