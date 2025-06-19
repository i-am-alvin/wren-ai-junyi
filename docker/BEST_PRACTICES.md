# WrenAI 資料匯入最佳實踐

## 🚨 重要經驗教訓

### 2025-06-19 學到的重要教訓

我們在匯入過程中犯了一個重要錯誤，這個經驗教訓必須被記錄下來避免重複：

#### ❌ 錯誤做法：直接操作 Qdrant
```bash
# 這些做法都是錯誤的！
docker exec container python import_instructions.py          # ❌
docker exec container python simple_import.py               # ❌
python -c "import requests; requests.post('http://qdrant:6333/...')"  # ❌
```

**問題**：
1. **資料不一致**：直接寫入 Qdrant 的資料不會出現在 UI 中
2. **無法管理**：UI 無法查看、編輯或刪除這些資料
3. **同步問題**：UI 資料庫 (SQLite) 和向量資料庫 (Qdrant) 不同步
4. **配置錯誤**：手動創建 Qdrant 集合可能使用錯誤的向量維度

#### ✅ 正確做法：透過 UI API
```bash
# 這些是正確的做法！
python3 scripts/import_instructions_via_ui.py               # ✅
python3 scripts/import_csv_sql_pairs.py                     # ✅
curl -X POST http://localhost:3000/api/graphql ...          # ✅
```

**優點**：
1. **自動同步**：UI 和 Qdrant 自動保持一致
2. **完整管理**：可在 UI 中查看、編輯、刪除
3. **正確配置**：WrenAI 自動處理向量維度和集合配置
4. **事務安全**：支援回滾和錯誤處理

## 🏗️ 系統架構理解

### WrenAI 雙層架構
```
┌─────────────────┐    GraphQL API    ┌──────────────────┐
│   UI Frontend   │ ◄─────────────────► │   UI Backend     │
│  (React/Next)   │                    │   (SQLite)       │
└─────────────────┘                    └──────────────────┘
                                                │
                                                │ HTTP API
                                                ▼
                                       ┌──────────────────┐
                                       │  WrenAI Service  │
                                       │   (Qdrant)       │
                                       └──────────────────┘
```

### 資料流程
1. **UI GraphQL API** ← 正確的入口點
2. **UI SQLite Database** ← 儲存 metadata
3. **WrenAI Service** ← 自動處理向量化
4. **Qdrant Vector DB** ← 自動同步

## 📋 標準操作程序 (SOP)

### Instructions 匯入
```bash
# 1. 準備 CSV 檔案
vim docker/data/instructions.csv

# 2. 執行匯入 (正確方法)
cd docker
python3 scripts/import_instructions_via_ui.py

# 3. 驗證結果
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id instruction isDefault } }"}' \
  | python -m json.tool
```

### SQL Pairs 匯入
```bash
# 1. 準備 CSV 檔案
vim docker/data/sql_pairs.csv

# 2. 執行匯入 (正確方法)
python3 scripts/import_csv_sql_pairs.py

# 3. 驗證結果
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { sqlPairs { id question sql } }"}' \
  | python -m json.tool
```

## 🔍 驗證清單

每次匯入後必須檢查：

- [ ] **UI 可見性**：在 `http://localhost:3000` 可以看到資料
- [ ] **Qdrant 同步**：向量資料庫中有對應的向量
- [ ] **AI 功能**：AI 查詢時能正確套用新的 instructions
- [ ] **管理功能**：可在 UI 中編輯和刪除

### 驗證指令
```bash
# 檢查 UI 中的資料數量
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id } sqlPairs { id } }"}' \
  | jq '.data | {instructions: (.instructions | length), sqlPairs: (.sqlPairs | length)}'

# 檢查 Qdrant 中的向量數量
docker exec wrenai-wren-ai-service-1 python -c "
import requests
instructions = requests.post('http://qdrant:6333/collections/instructions/points/scroll', json={'limit': 1}).json()
sql_pairs = requests.post('http://qdrant:6333/collections/sql_pairs/points/scroll', json={'limit': 1}).json()
print(f'Qdrant: instructions={len(instructions[\"result\"][\"points\"])}, sql_pairs={len(sql_pairs[\"result\"][\"points\"])}')
"
```

## 🚫 禁止的操作

### 永遠不要做的事情
1. **直接操作 Qdrant**：不要使用 `requests.post('http://qdrant:6333/...')`
2. **手動創建集合**：不要使用 `requests.put('http://qdrant:6333/collections/...')`
3. **繞過 UI API**：不要直接寫入 SQLite 資料庫
4. **混合方法**：不要同時使用直接和 API 方法

### 廢棄的檔案 (不要使用)
- `scripts/import_instructions.py` ❌
- `scripts/simple_import.py` ❌
- `scripts/run_import.sh` ❌ (如果使用直接方法)

## 🆘 故障恢復

### 如果誤用了直接方法
```bash
# 1. 清理錯誤的 Qdrant 資料
docker exec wrenai-wren-ai-service-1 python -c "
import requests
requests.delete('http://qdrant:6333/collections/instructions')
requests.delete('http://qdrant:6333/collections/sql_pairs')
"

# 2. 重新啟動 WrenAI 服務讓系統重新初始化
docker restart wrenai-wren-ai-service-1

# 3. 使用正確方法重新匯入
python3 scripts/import_instructions_via_ui.py
python3 scripts/import_csv_sql_pairs.py
```

## 📚 參考資料

- [詳細匯入指南](docs/import.md)
- [儲存架構說明](docs/storage.md)
- [WrenAI GraphQL API](../wren-ui/src/apollo/client/graphql/)

## 🎯 記住這個教訓

> **永遠透過 UI API 匯入資料，讓 WrenAI 自動處理向量化和同步！**

這個教訓來自實際的錯誤經驗，必須被團隊所有成員記住。 