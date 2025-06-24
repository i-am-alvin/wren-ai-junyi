# WrenAI MDL Import/Export 操作指南

## 📋 概述

本文檔詳細記錄 WrenAI 的建模資料 (MDL) 導入/導出功能的完整操作流程，包括與傳統 CSV 方式的對比分析。

## 🎯 MDL vs CSV 對比

### MDL (Model Definition Language) 方式

**優勢：**
- ✅ **完整性**：包含完整的模型定義、關係、欄位類型、中文描述等
- ✅ **結構化**：JSON 格式，包含豐富的 metadata 和語義資訊
- ✅ **版本控制**：每次部署都有唯一的 SHA1 哈希值，可追蹤版本
- ✅ **語義保持**：保留中文描述和顯示名稱，便於理解
- ✅ **關係映射**：明確定義模型間的關聯和 JOIN 條件
- ✅ **類型安全**：包含精確的資料類型和約束資訊

**劣勢：**
- ❌ **複雜性**：需要技術背景才能理解和編輯
- ❌ **文件大小**：比 CSV 大，包含更多 metadata
- ❌ **導入功能**：目前缺少直接的 MDL 導入 API

### CSV 方式 (如 sql_pairs.csv, instructions.csv)

**優勢：**
- ✅ **簡單直觀**：純文本格式，任何人都能編輯
- ✅ **輕量級**：文件小，處理速度快
- ✅ **工具友好**：可用 Excel、Google Sheets 等工具編輯
- ✅ **導入支援**：有現成的導入腳本

**劣勢：**
- ❌ **資訊有限**：只能存儲平面資料，缺少結構化資訊
- ❌ **無關聯性**：無法表達模型間的複雜關係
- ❌ **語義缺失**：缺少類型、約束、描述等重要資訊

---

## 🔧 MDL Export 操作流程

### 前置條件檢查

```bash
# 1. 確認 Docker 環境運行
docker ps | grep wren

# 2. 檢查資料庫連接
docker exec -it wrenai-wren-ui-1 ls /app/data/db.sqlite3

# 3. 驗證 GraphQL API 可用性
docker exec -it wrenai-wren-ui-1 curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}' | jq
```

### Step 1: 獲取部署狀態

```bash
# 查詢現有模型
docker exec -it wrenai-wren-ui-1 curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ listModels { name } }"
  }' | jq

# 執行部署並獲取哈希
docker exec -it wrenai-wren-ui-1 curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { deploy(force: false) }"
  }' | jq
```

### Step 2: 獲取部署哈希

```bash
# 查詢最新部署記錄
docker exec -it wrenai-wren-ui-1 curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ deployLogQuery { hash } }"
  }' | jq -r '.data.deployLogQuery[-1].hash'
```

### Step 3: 導出 MDL

```bash
# 使用哈希導出 MDL
DEPLOY_HASH="852c9584f33bf6df0006a983b332dfa524282eeb"  # 替換為實際哈希

docker exec -it wrenai-wren-ui-1 curl -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query GetMDL(\$hash: String!) { getMDL(hash: \$hash) { hash mdl } }\",
    \"variables\": {
      \"hash\": \"$DEPLOY_HASH\"
    }
  }" > mdl_response.json

# 解碼並格式化 MDL
cat mdl_response.json | jq -r '.data.getMDL.mdl' | base64 -d | jq > exported_mdl.json
```

### Step 4: 驗證導出結果

```bash
# 基本驗證
echo "文件大小: $(du -h exported_mdl.json | cut -f1)"
echo "JSON 格式: $(jq empty exported_mdl.json && echo '✅ 有效' || echo '❌ 無效')"

# 結構驗證
jq -r '
"模型數量: " + (.models | length | tostring),
"關係數量: " + (.relationships | length | tostring),
"資料源: " + .dataSource,
"目錄: " + .catalog
' exported_mdl.json

# 模型列表
jq -r '.models[] | "- " + .name + " (" + (.columns | length | tostring) + " 列)"' exported_mdl.json
```

---

## 📥 MDL Import 操作流程

### 現狀分析

**目前狀況：**
- ❌ WrenAI 目前**沒有**直接的 MDL 導入 GraphQL API
- ❌ UI 界面也沒有 MDL 上傳功能
- ✅ 只在評估工具中有部分 MDL 上傳功能 (`wren-ai-service/eval/data_curation/app.py`)

### 可能的導入方案

#### 方案 1: 直接資料庫操作 (高風險)

```bash
# ⚠️ 警告：此方法會直接修改資料庫，風險極高
# 僅供技術研究參考，不建議在生產環境使用

# 1. 備份資料庫
docker exec wrenai-wren-ui-1 cp /app/data/db.sqlite3 /app/data/db.sqlite3.backup

# 2. 解析 MDL 並重建資料庫表
# (需要開發自定義腳本)
```

#### 方案 2: 通過 UI 手動重建 (推薦)

```bash
# 1. 讀取 MDL 文件獲取模型定義
jq -r '.models[] | 
"模型: " + .name + 
"\n表: " + .tableReference.table +
"\n描述: " + .properties.description +
"\n欄位數: " + (.columns | length | tostring) + "\n"
' exported_mdl.json

# 2. 在 WrenAI UI 中逐一重建模型
# 3. 根據 relationships 設定模型間關聯
```

#### 方案 3: 開發導入 API (長期方案)

需要在 WrenAI 中新增：
1. GraphQL mutation for MDL import
2. MDL 解析和驗證邏輯
3. 資料庫 migration 處理
4. UI 上傳界面

---

## 📊 實際測試結果

### 測試環境
- **日期**: 2024-06-22
- **WrenAI 版本**: Docker Compose 部署
- **資料源**: BigQuery
- **測試資料**: Junyi Academy 教育資料

### 導出測試結果

```bash
=== MDL 導出成功 ===
✅ 文件大小: 58K
✅ JSON 格式: 有效
✅ 部署哈希: 852c9584f33bf6df0006a983b332dfa524282eeb

📊 包含模型: 8 個
📊 關係定義: 6 個  
📊 視圖: 0 個
📊 總欄位數: 156 個

模型清單:
- dim_schools_metadata (53 列) - 學校基本資料
- fct_user_records_of_missions_grained_to_missions (22 列) - 用戶任務記錄
- dim_user_data (42 列) - 用戶資料維度表
- dim_dates (4 列) - 日期維度表
- dim_teacher_student_joins (11 列) - 師生關係表
- fct_user_records_of_all_contents_grained_to_date (10 列) - 按日期聚合的用戶內容記錄
- fct_teacher_level_score (5 列) - 教師等級分數
- fct_user_records_of_all_contents (9 列) - 用戶所有內容記錄
```

### 驗證檢查項目

✅ **JSON 格式正確性**: 通過 jq 驗證  
✅ **MDL Schema 合規性**: 包含所有必要欄位  
✅ **中文描述保持**: 完整保留繁體中文描述  
✅ **關係定義完整**: 6 個關係全部正確定義  
✅ **欄位類型精確**: 包含 STRING, INT64, FLOAT64, BOOL, DATE, TIMESTAMP 等  
✅ **Table Reference 正確**: 每個模型都有對應的資料庫表引用  

---

## 📝 最佳實踐建議

### For Export:
1. **定期備份**: 建議每次重大模型變更後都導出 MDL
2. **版本標記**: 用部署哈希追蹤不同版本的模型狀態
3. **文檔化**: 在 MDL 文件名中包含日期和版本資訊
4. **驗證完整性**: 導出後必須驗證 JSON 格式和內容完整性

### For Import:
1. **現階段**: 建議使用 UI 手動重建，配合 MDL 作為參考
2. **備份策略**: 導入前必須備份現有資料庫
3. **測試環境**: 先在測試環境驗證導入效果
4. **漸進式**: 一次導入一個模型，逐步驗證

### 文件管理:
```bash
# 建議的檔案命名規範
exported_mdl_20240622_852c9584.json
exported_mdl_20240622_production.json
exported_mdl_20240622_test_environment.json
```

---

## 🚀 未來改進方向

### 短期 (1-3 個月):
- [ ] 開發 MDL 導入 GraphQL API
- [ ] 增加 UI 中的 MDL 上傳功能
- [ ] 改善導出流程的使用者體驗

### 中期 (3-6 個月):
- [ ] 實現增量導入 (只更新變更的模型)
- [ ] 增加 MDL 差異比較功能
- [ ] 支援模型版本回滾

### 長期 (6-12 個月):
- [ ] 整合 Git 版本控制
- [ ] 自動化 CI/CD 部署流程
- [ ] 跨環境模型同步功能

---

## 📞 技術支援

如遇到問題，請參考：
1. WrenAI GitHub Repository
2. WrenAI 官方文檔
3. GraphQL API Schema 文檔

**文檔版本**: v1.0  
**最後更新**: 2024-06-22  
**維護者**: 開發團隊 