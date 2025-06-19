# WrenAI 匯入快速參考

## 🚨 重要提醒
**永遠透過 UI API 匯入，不要直接操作 Qdrant！**

## ✅ 正確的匯入指令

### Instructions 匯入
```bash
cd docker
python3 scripts/import_instructions_via_ui.py
```

### SQL Pairs 匯入
```bash
cd docker
python3 scripts/import_csv_sql_pairs.py
```

## 🔍 驗證指令

### 檢查 UI 中的資料
```bash
curl -s http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { instructions { id } sqlPairs { id } }"}' \
  | jq '.data | {instructions: (.instructions | length), sqlPairs: (.sqlPairs | length)}'
```

### 檢查 Qdrant 同步狀態
```bash
docker exec wrenai-wren-ai-service-1 python -c "
import requests
i = requests.post('http://qdrant:6333/collections/instructions/points/scroll', json={'limit': 1}).json()
s = requests.post('http://qdrant:6333/collections/sql_pairs/points/scroll', json={'limit': 1}).json()
print(f'Qdrant: instructions={len(i[\"result\"][\"points\"])}, sql_pairs={len(s[\"result\"][\"points\"])}')
"
```

## ❌ 禁止使用的檔案
- `scripts/import_instructions.py` ❌
- `scripts/simple_import.py` ❌
- 任何直接操作 Qdrant 的腳本 ❌

## 📁 檔案位置
- **正確腳本**: `docker/scripts/import_*_via_ui.py`
- **資料檔案**: `docker/data/*.csv`
- **詳細文檔**: `docker/docs/import.md`
- **最佳實踐**: `docker/BEST_PRACTICES.md`

## 🆘 如果出錯了
1. 檢查是否使用了正確的 UI API 腳本
2. 確認 WrenAI UI 服務正常運行：`curl http://localhost:3000/api/graphql`
3. 查看詳細故障排除：`docker/BEST_PRACTICES.md`

---
**記住**：UI API → 自動同步 → 成功！ 