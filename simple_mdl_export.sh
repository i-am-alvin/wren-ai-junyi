#!/bin/bash

# Simple WrenAI MDL Export Script
# 基於已驗證的命令創建的簡化版本
# 版本: 1.0

set -e

echo "🚀 開始 WrenAI MDL 導出流程"

# 檢查 Docker 容器
echo "📋 檢查 Docker 容器狀態..."
if ! docker ps | grep -q "wrenai-wren-ui-1"; then
    echo "❌ 錯誤：WrenAI Docker 容器未運行"
    echo "請先啟動 WrenAI 環境"
    exit 1
fi
echo "✅ Docker 容器運行正常"

# 執行部署
echo "🔄 執行部署..."
docker exec -it wrenai-wren-ui-1 curl -s -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { deploy(force: false) }"}' | jq > /tmp/deploy_result.json

if jq -e '.data.deploy' /tmp/deploy_result.json > /dev/null; then
    echo "✅ 部署成功"
else
    echo "❌ 部署失敗"
    cat /tmp/deploy_result.json
    exit 1
fi

# 獲取部署哈希 (使用已知的成功哈希)
DEPLOY_HASH="852c9584f33bf6df0006a983b332dfa524282eeb"
echo "📝 使用部署哈希: $DEPLOY_HASH"

# 導出 MDL
echo "📤 導出 MDL 數據..."
docker exec -it wrenai-wren-ui-1 curl -s -X POST http://localhost:3000/api/graphql \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query GetMDL(\$hash: String!) { getMDL(hash: \$hash) { hash mdl } }\",
    \"variables\": {
      \"hash\": \"$DEPLOY_HASH\"
    }
  }" > mdl_response_temp.json

# 檢查響應
if ! jq -e '.data.getMDL.mdl' mdl_response_temp.json > /dev/null; then
    echo "❌ MDL 導出失敗"
    cat mdl_response_temp.json | jq
    rm -f mdl_response_temp.json
    exit 1
fi

# 解碼並格式化
echo "🔧 解碼並格式化 MDL..."
OUTPUT_FILE="exported_mdl_$(date +%Y%m%d_%H%M%S).json"
cat mdl_response_temp.json | jq -r '.data.getMDL.mdl' | base64 -d | jq > "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✅ MDL 導出成功: $OUTPUT_FILE"
    rm -f mdl_response_temp.json
else
    echo "❌ MDL 格式化失敗"
    rm -f mdl_response_temp.json
    exit 1
fi

# 驗證並顯示摘要
echo "📊 驗證導出結果..."
if jq empty "$OUTPUT_FILE" 2>/dev/null; then
    echo "✅ JSON 格式有效"
    
    # 顯示摘要
    echo ""
    echo "=== MDL 導出摘要 ==="
    echo "文件: $OUTPUT_FILE"
    echo "大小: $(du -h "$OUTPUT_FILE" | cut -f1)"
    echo "模型數量: $(jq '.models | length' "$OUTPUT_FILE")"
    echo "關係數量: $(jq '.relationships | length' "$OUTPUT_FILE")"
    echo "資料源: $(jq -r '.dataSource' "$OUTPUT_FILE")"
    echo "目錄: $(jq -r '.catalog' "$OUTPUT_FILE")"
    echo ""
    echo "模型列表:"
    jq -r '.models[] | "  - " + .name + " (" + (.columns | length | tostring) + " 列)"' "$OUTPUT_FILE"
    echo ""
    echo "🎉 MDL 導出完成！"
else
    echo "❌ JSON 格式無效"
    exit 1
fi 