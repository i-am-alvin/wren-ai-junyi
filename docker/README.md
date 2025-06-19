# WrenAI Docker 工具與文件

本目錄包含 WrenAI 的 Docker 相關工具、腳本和文件。

## 目錄結構

```
docker/
├── README.md                    # 本檔案
├── data/                        # 資料檔案
│   └── instructions.csv         # Instructions 匯入範例 CSV
├── docs/                        # 文件
│   ├── storage.md              # 儲存架構說明
│   └── import.md               # Instructions 匯入指南
├── scripts/                     # 工具腳本
│   ├── import_instructions.py   # 完整版匯入腳本（直接 Qdrant）
│   ├── simple_import.py        # 簡化版匯入腳本（直接 Qdrant）
│   ├── import_via_ui_api.py    # UI API 匯入腳本（Python）
│   ├── import_via_ui_api.sh    # UI API 匯入腳本（Shell）
│   ├── check_instructions.py   # 檢查 instructions 腳本
│   └── run_import.sh           # 執行匯入的 Shell 腳本
├── docker-compose-dev.yaml     # 開發環境 Docker Compose
└── config.example*.yaml        # 設定檔範例
```

## 主要功能

### 📋 Instructions 管理
- **匯入**: 透過 CSV 批次匯入 instructions
- **驗證**: 檢查匯入結果和資料一致性
- **查詢**: 檢視 UI 和 Qdrant 中的 instructions

### 🔄 SQL-Question Pairs 管理
- **匯入**: 透過 GraphQL API 批次匯入 SQL-question pairs
- **驗證**: 檢查 UI SQLite 和 Qdrant 向量資料庫同步
- **範例**: 包含 CTE 註解的 SQL 範例

### 📚 文件
- **storage.md**: 詳細說明 WrenAI 的儲存架構
- **import.md**: Instructions 匯入的完整指南

### 🛠️ 工具腳本
- **Instructions**: `import_via_ui_api.sh` - 透過正確的 UI API 匯入 instructions
- **SQL Pairs**: `import_sql_pairs_simple.sh` - 匯入 SQL-question pairs
- **除錯用**: `check_instructions.py` - 驗證匯入結果
- **歷史版本**: 其他直接操作 Qdrant 的腳本（不推薦）

## 快速開始

### 匯入 Instructions

1. **準備 CSV 檔案**:
   ```bash
   # 編輯或建立 CSV 檔案
   vim data/instructions.csv
   ```

2. **執行匯入**:
   ```bash
   # 使用 Shell 腳本（推薦）
   chmod +x scripts/import_via_ui_api.sh
   ./scripts/import_via_ui_api.sh
   ```

3. **驗證結果**:
   ```bash
   # 檢查 UI 中的 instructions
   curl -s http://localhost:3000/api/graphql \
     -H "Content-Type: application/json" \
     -d '{"query":"query { instructions { id instruction isDefault } }"}' \
     | python3 -m json.tool
   ```

### 檢查儲存狀態

```bash
# 檢查 Qdrant 容器
docker ps | grep qdrant

# 檢查 Instructions 集合
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
response = requests.get('http://qdrant:6333/collections/instructions')
print(response.json())
"
```

## 重要提醒

⚠️ **匯入方法選擇**:
- ✅ **正確**: 使用 `import_via_ui_api.sh` 透過 UI GraphQL API
- ❌ **錯誤**: 直接寫入 Qdrant（不會出現在 UI 中）

⚠️ **架構理解**:
- UI 讀取 SQLite 中的 instructions metadata
- AI Service 使用 Qdrant 中的向量化 instructions
- 兩者必須同步，透過正確的 API 可自動處理

## 故障排除

### 常見問題

1. **UI 中看不到匯入的 instructions**
   - 原因: 使用了錯誤的匯入方法
   - 解決: 使用 `import_via_ui_api.sh`

2. **GraphQL API 錯誤**
   - 檢查 WrenAI UI 服務是否正常運行
   - 確認 `http://localhost:3000` 可正常存取

3. **Qdrant 連接失敗**
   - 檢查 Qdrant 容器狀態: `docker ps | grep qdrant`
   - 檢查容器日誌: `docker logs wrenai-qdrant-1`

### 除錯工具

```bash
# 檢查所有 WrenAI 容器狀態
docker ps | grep wrenai

# 檢查 UI 服務日誌
docker logs -f wrenai-wren-ui-1

# 檢查 AI 服務日誌
docker logs -f wrenai-wren-ai-service-1

# 使用檢查腳本
python3 scripts/check_instructions.py
```

## 開發指南

### 新增匯入腳本

1. 參考現有的 `import_via_ui_api.sh`
2. 使用正確的 GraphQL API endpoint
3. 處理錯誤回應和重試邏輯
4. 加入適當的日誌和進度顯示

### 擴展 CSV Schema

如需修改 CSV 格式：

1. 更新 `data/instructions.csv` 範例
2. 修改匯入腳本的解析邏輯
3. 更新 `docs/import.md` 文件
4. 測試新格式的匯入和驗證

## 參考資料

- [WrenAI 官方文件](https://github.com/Canner/WrenAI)
- [Qdrant 文件](https://qdrant.tech/documentation/)
- [GraphQL 規範](https://graphql.org/)
