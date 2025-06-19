# WrenAI Instructions 匯入指南

## 概述

本文件說明如何正確匯入 instructions 到 WrenAI 系統。Instructions 是指導 AI 生成 SQL 的重要規則和上下文資訊。

## 系統架構理解

WrenAI 使用**雙層資料架構**來儲存 instructions：

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
1. **UI Layer (SQLite)**: 儲存 instructions 的 metadata，用於 UI 顯示
2. **AI Service Layer (Qdrant)**: 儲存向量化的 instructions，用於語意搜尋

⚠️ **重要**: 直接寫入 Qdrant 的資料**不會**出現在 UI 中！

## 正確匯入方法

### 方法一：透過 UI 介面手動新增
1. 開啟 WrenAI UI: `http://localhost:3000`
2. 導航至 Knowledge > Instructions
3. 點擊 "Add an instruction" 按鈕
4. 填寫指令內容、相關問題、是否為全域指令
5. 儲存

### 方法二：透過 GraphQL API 批次匯入（推薦）

#### 準備 CSV 檔案
建立 `docker/data/instructions.csv` 檔案：

```csv
instruction_id,instruction,questions,is_default,project_id
cte_comment_global,"在生成 SQL 時，必須在每一個 CTE (Common Table Expression) 前加上適當的註解，說明該 CTE 的用途和邏輯。註解格式應為：-- CTE: [名稱] - [用途說明]。這有助於提高 SQL 的可讀性和維護性。","",true,20
teacher_student_relation,"dim_teacher_student_joins 記錄了老師、學生和班級之間的關係，包含 class_id, teacher_user_id, student_user_id, class_name。建議規則: 當查詢需要連接老師和其對應的學生，或查詢某班級的師生名單時，應使用 dim_teacher_student_joins。","老師和學生的關係如何查詢？;如何找到某個班級的所有師生？",false,20
```

#### CSV Schema 說明
- `instruction_id`: 指令唯一識別碼（可選，僅用於追蹤）
- `instruction`: 指令內容（必填）
- `questions`: 相關問題，用分號分隔（可選）
- `is_default`: 是否為全域指令（必填：true/false）
- `project_id`: 專案識別碼（必填）

#### 使用匯入腳本

我們提供了兩個匯入腳本：

##### Shell 腳本（推薦）
```bash
# 給予執行權限
chmod +x docker/scripts/import_via_ui_api.sh

# 執行匯入
./docker/scripts/import_via_ui_api.sh
```

##### Python 腳本
```bash
# 在 UI 容器中執行（如果有 Python）
docker exec -it wrenai-wren-ui-1 python /app/docker/scripts/import_via_ui_api.py
```

#### 手動 GraphQL 呼叫範例

```bash
curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation CreateInstruction($data: CreateInstructionInput!) { createInstruction(data: $data) { id projectId instruction questions isDefault createdAt updatedAt } }",
    "variables": {
      "data": {
        "instruction": "在生成 SQL 時，必須在每一個 CTE 前加上適當的註解",
        "questions": [],
        "isDefault": true
      }
    }
  }'
```

## 驗證匯入結果

### 檢查 UI 中的 Instructions
```bash
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id projectId instruction questions isDefault createdAt } }"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'UI 中找到 {len(data[\"data\"][\"instructions\"])} 個 instructions')"
```

### 檢查 Qdrant 中的向量資料
```bash
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', 
                        json={'limit': 10, 'with_payload': True})
result = response.json()
print(f'Qdrant 中找到 {len(result[\"result\"][\"points\"])} 個 instruction 向量')
"
```

## 故障排除

### 問題：UI 中看不到匯入的 Instructions

**原因**: 直接寫入 Qdrant 的資料不會出現在 UI 中

**解決方案**: 使用正確的 GraphQL API 匯入方法

### 問題：GraphQL API 回傳錯誤

**常見錯誤及解決方案**:

1. **"Cannot query field"**: 檢查 GraphQL schema 是否正確
2. **"Instruction is required"**: 確認 instruction 欄位不為空
3. **"Instruction is too long"**: instruction 內容不得超過 1000 字元

### 問題：匯入後 AI 沒有套用新指令

**可能原因**:
1. 指令沒有設為全域指令 (`isDefault: true`)
2. 向量索引尚未完成（等待幾分鐘）
3. 需要重新啟動 WrenAI service

**解決方案**:
```bash
# 重新啟動 WrenAI service
docker restart wrenai-wren-ai-service-1

# 檢查服務狀態
docker logs -f wrenai-wren-ai-service-1
```

## 最佳實踐

### 1. 指令設計原則
- **明確性**: 指令應該清楚明確，避免模糊語言
- **具體性**: 提供具體的規則和格式要求
- **一致性**: 保持指令風格和術語的一致性

### 2. 全域指令 vs 問題導向指令
- **全域指令** (`isDefault: true`): 適用於所有 SQL 生成的通用規則
- **問題導向指令** (`isDefault: false`): 針對特定問題類型的專門指令

### 3. 問題設計
- 為問題導向指令提供多樣化的相關問題
- 使用自然語言，模擬使用者真實的提問方式
- 涵蓋不同的問題角度和用詞變化

### 4. 測試驗證
- 匯入後務必透過 UI 確認指令正確顯示
- 測試 AI 是否正確套用新指令
- 監控 Qdrant 中的向量索引狀態

## 範例指令

### CTE 註解全域指令
```
指令: 在生成 SQL 時，必須在每一個 CTE (Common Table Expression) 前加上適當的註解，說明該 CTE 的用途和邏輯。註解格式應為：-- CTE: [名稱] - [用途說明]。這有助於提高 SQL 的可讀性和維護性。
類型: 全域指令 (isDefault: true)
問題: (無)
```

### 資料表關係指令
```
指令: dim_teacher_student_joins 記錄了老師、學生和班級之間的關係，包含 class_id, teacher_user_id, student_user_id, class_name。建議規則: 當查詢需要連接老師和其對應的學生，或查詢某班級的師生名單時，應使用 dim_teacher_student_joins。
類型: 問題導向指令 (isDefault: false)
問題: 
- 老師和學生的關係如何查詢？
- 如何找到某個班級的所有師生？
```

## SQL-Question Pairs 匯入

### 架構說明
SQL-Question pairs 使用與 instructions **完全相同的雙層架構**：
- **UI Layer (SQLite)**: 儲存 SQL pairs 的 metadata，用於 UI 顯示和管理
- **AI Service Layer (Qdrant)**: 儲存向量化的 SQL pairs，用於語意搜尋和學習

### GraphQL API
```bash
# 建立 SQL pair
curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation CreateSqlPair($data: CreateSqlPairInput!) { createSqlPair(data: $data) { id projectId sql question createdAt updatedAt } }",
    "variables": {
      "data": {
        "question": "每個使用者角色有多少人？",
        "sql": "-- CTE: 使用者統計 - 計算使用者總數\nWITH user_stats AS (\n  SELECT user_role, COUNT(*) as user_count\n  FROM dim_user_data GROUP BY user_role\n)\nSELECT user_role, user_count FROM user_stats ORDER BY user_count DESC;"
      }
    }
  }'

# 查詢所有 SQL pairs
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { sqlPairs { id projectId sql question createdAt } }"}'
```

### CSV Schema (SQL Pairs)
```csv
question,sql
"每個使用者角色有多少人？","-- CTE: 使用者統計 - 計算使用者總數
WITH user_stats AS (
  SELECT user_role, COUNT(*) as user_count
  FROM dim_user_data GROUP BY user_role
)
SELECT user_role, user_count FROM user_stats ORDER BY user_count DESC;"
```

### 驗證 SQL Pairs 匯入
```bash
# 檢查 UI 中的 SQL pairs
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { sqlPairs { id sql question } }"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'UI 中找到 {len(data[\"data\"][\"sqlPairs\"])} 個 SQL pairs')"

# 檢查 Qdrant 中的 SQL pairs
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
response = requests.post('http://qdrant:6333/collections/sql_pairs/points/scroll', 
                        json={'limit': 10, 'with_payload': True})
result = response.json()
print(f'Qdrant 中找到 {len(result[\"result\"][\"points\"])} 個 SQL pair 向量')
"
```

## 相關檔案

### Instructions 匯入
- `docker/scripts/import_via_ui_api.sh`: Instructions Shell 匯入腳本
- `docker/scripts/import_via_ui_api.py`: Instructions Python 匯入腳本  
- `docker/data/instructions.csv`: Instructions 範例 CSV 檔案

### SQL Pairs 匯入
- `docker/scripts/import_sql_pairs_simple.sh`: SQL Pairs 簡化匯入腳本
- `docker/data/sql_pairs.csv`: SQL Pairs 範例 CSV 檔案

### 文件
- `docker/docs/storage.md`: 儲存架構詳細說明

## 參考資料

- [WrenAI GraphQL API 文件](../wren-ui/src/apollo/client/graphql/instructions.ts)
- [Instruction Service 實作](../wren-ui/src/apollo/server/services/instructionService.ts)
- [Qdrant 向量資料庫文件](https://qdrant.tech/documentation/) 