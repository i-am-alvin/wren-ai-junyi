# WrenAI Data Export Guide

## 概述

本文件說明如何從 WrenAI 系統匯出 instructions 和 SQL pairs 資料。匯出的資料可用於備份、版本控制、或匯入到其他 WrenAI 實例。

## 匯出工具

我們提供了兩種匯出工具：

### 1. Shell 腳本（推薦）

```bash
# 給予執行權限
chmod +x docker/scripts/export_data.sh

# 執行匯出
./docker/scripts/export_data.sh
```

### 2. Python 腳本

```bash
# 在容器內執行
docker cp docker/scripts/export_data.py wrenai-wren-ai-service-1:/app/export_data.py
docker exec -it wrenai-wren-ai-service-1 /app/.venv/bin/python3 /app/export_data.py

# 複製結果到本地
docker cp wrenai-wren-ai-service-1:/app/data/instructions.csv docker/data/instructions.csv
docker cp wrenai-wren-ai-service-1:/app/data/sql_pairs.csv docker/data/sql_pairs.csv
```

## 匯出內容

### Instructions CSV 格式
```csv
instruction_id,instruction,questions,is_default,project_id,created_at,updated_at
exported_instruction_1,"指令內容","問題1;問題2",true,20,2025-06-19T23:01:26.000Z,2025-06-19T23:01:26.000Z
```

欄位說明：
- `instruction_id`: 匯出時生成的識別碼
- `instruction`: 指令內容
- `questions`: 相關問題（分號分隔）
- `is_default`: 是否為全域指令
- `project_id`: 專案 ID
- `created_at`: 建立時間
- `updated_at`: 更新時間

### SQL Pairs CSV 格式
```csv
question,sql,project_id,created_at,updated_at
"使用者角色統計","SELECT user_role, COUNT(*) FROM dim_user_data GROUP BY user_role",20,2025-06-19T23:01:26.000Z,2025-06-19T23:01:26.000Z
```

欄位說明：
- `question`: 自然語言問題
- `sql`: 對應的 SQL 查詢
- `project_id`: 專案 ID
- `created_at`: 建立時間
- `updated_at`: 更新時間

## 資料來源

匯出工具從以下來源取得資料：

1. **UI Backend (SQLite)**: 透過 GraphQL API 查詢
   - Instructions metadata
   - SQL pairs metadata
   
2. **向量資料庫 (Qdrant)**: 儲存向量化資料（僅供 AI 搜尋使用）

## 使用場景

### 1. 資料備份
```bash
# 定期備份
./docker/scripts/export_data.sh

# 加上時間戳
mkdir -p backups/$(date +%Y%m%d)
./docker/scripts/export_data.sh
cp docker/data/*.csv backups/$(date +%Y%m%d)/
```

### 2. 版本控制
```bash
# 匯出當前版本
./docker/scripts/export_data.sh

# 提交到 Git
git add docker/data/instructions.csv docker/data/sql_pairs.csv
git commit -m "Update instructions and SQL pairs export"
```

### 3. 環境遷移
```bash
# 從生產環境匯出
./docker/scripts/export_data.sh

# 複製檔案到新環境
scp docker/data/*.csv user@new-server:/path/to/wrenai/docker/data/

# 在新環境匯入
./docker/scripts/import_via_ui_api.sh
```

## 故障排除

### 問題：容器未運行
```
❌ Error: Container wrenai-wren-ai-service-1 is not running
```

**解決方案**:
```bash
# 啟動 WrenAI 服務
docker-compose up -d
```

### 問題：GraphQL 連接失敗
```
❌ Request Error: HTTPConnectionPool(host='wrenai-wren-ui-1', port=3000)
```

**解決方案**:
1. 確認 UI 容器正在運行
2. 檢查容器網路連接
3. 等待服務完全啟動

### 問題：匯出檔案為空
**可能原因**:
- 系統中沒有 instructions 或 SQL pairs
- 權限問題
- GraphQL API 錯誤

**檢查方法**:
```bash
# 檢查 UI 中的資料
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id } sqlPairs { id } }"}'
```

## 相關檔案

- `docker/scripts/export_data.sh`: Shell 匯出腳本
- `docker/scripts/export_data.py`: Python 匯出腳本
- `docker/data/instructions.csv`: 匯出的指令檔案
- `docker/data/sql_pairs.csv`: 匯出的 SQL 對檔案

## 與匯入工具整合

匯出的 CSV 檔案可以直接用於匯入工具：

```bash
# 匯出資料
./docker/scripts/export_data.sh

# 匯入到另一個環境
./docker/scripts/import_via_ui_api.sh
```

詳細匯入說明請參考 [Import Guide](import.md)。

## 開發知識與技術細節

### 系統架構理解

WrenAI 使用**雙層資料架構**：

```
┌─────────────────┐    GraphQL API    ┌──────────────────┐
│   UI Frontend   │ ◄─────────────────► │   UI Backend     │
│  (React/Next)   │                    │   (SQLite)       │
└─────────────────┘                    └──────────────────┘
                                                │
                                                │ 向量化同步
                                                ▼
                                       ┌──────────────────┐
                                       │  WrenAI Service  │
                                       │   (Qdrant)       │
                                       └──────────────────┘
```

**重要觀念**：
- **UI Backend (SQLite)**: 儲存實際的 metadata，供 UI 顯示和管理
- **AI Service (Qdrant)**: 儲存向量化資料，供 AI 語意搜尋使用
- **資料同步**: 透過 UI 的 GraphQL API 操作會同時更新兩層

### 容器網路架構

```bash
# 檢查容器網路
docker network ls | grep wren
# wrenai_wren - 主要服務網路

# 檢查容器在網路中的名稱
docker inspect wrenai_wren | grep -A 20 '"Containers"'
```

**容器間通訊**：
- 容器名稱：`wrenai-wren-ui-1`, `wrenai-wren-ai-service-1`, `wrenai-qdrant-1`
- 內部網路：容器間可透過容器名稱互相訪問
- 外部訪問：只有 UI (port 3000) 和 AI Service (port 5555) 對外開放

### GraphQL API 結構

#### Instructions Schema
```graphql
type Instruction {
  id: Int!
  projectId: Int!
  instruction: String!
  questions: [String!]!
  isDefault: Boolean!
  createdAt: String!
  updatedAt: String!
}

query Instructions {
  instructions {
    id projectId instruction questions isDefault createdAt updatedAt
  }
}
```

#### SQL Pairs Schema
```graphql
type SqlPair {
  id: Int!
  projectId: Int!
  sql: String!
  question: String!
  createdAt: String
  updatedAt: String
}

query SqlPairs {
  sqlPairs {
    id projectId sql question createdAt updatedAt
  }
}
```

### 開發過程中的技術挑戰

#### 1. 容器環境依賴問題
**問題**: 本地環境缺少 `requests` 模組
**解決方案**: 在有 Python 環境的容器內執行腳本

```bash
# 錯誤方式
python3 docker/scripts/export_data.py  # ModuleNotFoundError

# 正確方式
docker exec -it wrenai-wren-ai-service-1 /app/.venv/bin/python3 /app/export_data.py
```

#### 2. 容器間網路連接
**問題**: 容器內無法連接 `localhost:3000`
**解決方案**: 使用容器名稱作為 hostname

```python
# 錯誤配置
UI_GRAPHQL_ENDPOINT = "http://localhost:3000/api/graphql"

# 正確配置
UI_GRAPHQL_ENDPOINT = "http://wrenai-wren-ui-1:3000/api/graphql"
```

#### 3. 檔案路徑管理
**問題**: 容器內外路徑不一致
**解決方案**: 統一使用容器內路徑，再複製到本地

```python
# 統一使用容器內路徑
output_dir = "/app/data"

# 複製到本地
docker cp wrenai-wren-ai-service-1:/app/data/instructions.csv docker/data/
```

### 資料處理技巧

#### CSV 格式處理
```python
# Questions 陣列轉換為分號分隔字串
questions_str = ';'.join(instruction.get('questions', []))

# 布林值轉換為小寫字串
is_default = str(instruction.get('isDefault', False)).lower()

# 處理空值
instruction_text = instruction.get('instruction', '')
```

#### 錯誤處理策略
```python
try:
    response = requests.post(endpoint, json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print(f"❌ GraphQL Error: {result['errors']}")
            return None
        return result['data']['instructions']
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return None
except Exception as e:
    print(f"❌ Request Error: {e}")
    return None
```

### Shell 腳本設計模式

#### 錯誤處理與驗證
```bash
set -e  # 遇到錯誤立即退出

# 檢查容器狀態
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    exit 1
fi
```

#### 進度回饋設計
```bash
echo "📋 Copying export script to container..."
echo "🔄 Executing export script in container..."
echo "📥 Copying exported files to local..."
```

#### 統計資訊計算
```bash
# 計算記錄數（扣除標題行）
echo "Instructions: $(($(wc -l < "$LOCAL_DATA_DIR/instructions.csv") - 1)) records"
```

### 除錯技巧

#### 1. 檢查容器狀態
```bash
docker ps | grep wren                    # 檢查運行狀態
docker logs wrenai-wren-ui-1            # 檢查 UI 日誌
docker logs wrenai-wren-ai-service-1    # 檢查 AI Service 日誌
```

#### 2. 測試 GraphQL 連接
```bash
# 從本地測試
curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id } }"}'

# 從容器內測試
docker exec -it wrenai-wren-ai-service-1 \
  curl -X POST http://wrenai-wren-ui-1:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id } }"}'
```

#### 3. 檔案系統檢查
```bash
# 檢查容器內檔案
docker exec -it wrenai-wren-ai-service-1 ls -la /app/data/
docker exec -it wrenai-wren-ai-service-1 find /app -name "*.csv"

# 檢查檔案大小和內容
docker exec -it wrenai-wren-ai-service-1 wc -l /app/data/*.csv
docker exec -it wrenai-wren-ai-service-1 head -3 /app/data/instructions.csv
```

### 最佳實踐總結

#### 1. 容器化環境開發
- 優先在目標容器內執行腳本，避免環境差異
- 使用容器名稱進行內部網路通訊
- 善用 `docker cp` 在容器與宿主機間傳輸檔案

#### 2. API 設計
- 設定合理的 timeout 值
- 實作完整的錯誤處理機制
- 提供清楚的進度回饋

#### 3. 資料處理
- 統一 CSV 格式規範
- 處理特殊字元和空值
- 保持資料完整性

#### 4. 使用者體驗
- 提供 Shell 和 Python 兩種版本
- 清楚的執行步驟說明
- 豐富的統計資訊回饋

### 擴展建議

#### 1. 增量匯出
```python
# 支援日期範圍匯出
def export_with_date_range(start_date, end_date):
    # 在 GraphQL query 中加入日期篩選
    pass
```

#### 2. 格式支援
```python
# 支援 JSON 格式匯出
def export_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

#### 3. 自動化排程
```bash
# 加入 crontab 進行定期備份
0 2 * * * /path/to/wrenai/docker/scripts/export_data.sh
```

這些知識和經驗可以幫助未來的開發者：
1. 理解 WrenAI 的系統架構
2. 快速解決常見的技術問題  
3. 擴展更多匯出入功能
4. 維護和優化現有工具 