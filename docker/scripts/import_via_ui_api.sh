#!/bin/bash

# Import Instructions via UI GraphQL API
# This script properly imports instructions through the UI's GraphQL API

UI_GRAPHQL_ENDPOINT="http://localhost:3000/api/graphql"

echo "🚀 開始透過 UI GraphQL API 匯入 Instructions"
echo "=================================================="

# Function to create instruction via GraphQL
create_instruction() {
    local instruction="$1"
    local questions="$2"
    local is_default="$3"
    
    # Convert questions string to JSON array
    if [ -z "$questions" ]; then
        questions_json="[]"
    else
        # Split by semicolon and create JSON array
        questions_json="[\"$(echo "$questions" | sed 's/;/","/g')\"]"
    fi
    
    local payload=$(cat <<EOF
{
  "query": "mutation CreateInstruction(\$data: CreateInstructionInput!) { createInstruction(data: \$data) { id projectId instruction questions isDefault createdAt updatedAt } }",
  "variables": {
    "data": {
      "instruction": "$instruction",
      "questions": $questions_json,
      "isDefault": $is_default
    }
  }
}
EOF
)
    
    echo "📝 建立指令: $(echo "$instruction" | cut -c1-50)..."
    echo "   問題: $questions"
    echo "   全域: $is_default"
    
    response=$(curl -s -X POST "$UI_GRAPHQL_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | grep -q '"errors"'; then
        echo "   ❌ 失敗: $(echo "$response" | grep -o '"message":"[^"]*"' | head -1)"
        return 1
    elif echo "$response" | grep -q '"createInstruction"'; then
        local id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   ✅ 成功 - ID: $id"
        return 0
    else
        echo "   ❌ 未知錯誤: $response"
        return 1
    fi
}

echo ""
echo "📋 開始匯入指令..."

success_count=0
total_count=0

# 1. CTE 註解全域指令
echo ""
echo "1/5 CTE 註解全域指令"
if create_instruction "在生成 SQL 時，必須在每一個 CTE (Common Table Expression) 前加上適當的註解，說明該 CTE 的用途和邏輯。註解格式應為：-- CTE: [名稱] - [用途說明]。這有助於提高 SQL 的可讀性和維護性。" "" "true"; then
    ((success_count++))
fi
((total_count++))

# 2. 師生關係指令
echo ""
echo "2/5 師生關係指令"
if create_instruction "dim_teacher_student_joins 記錄了老師、學生和班級之間的關係，包含 class_id, teacher_user_id, student_user_id, class_name。建議規則: 當查詢需要連接老師和其對應的學生，或查詢某班級的師生名單時，應使用 dim_teacher_student_joins。" "老師和學生的關係如何查詢？;如何找到某個班級的所有師生？" "false"; then
    ((success_count++))
fi
((total_count++))

# 3. 使用者維度指令
echo ""
echo "3/5 使用者維度指令"
if create_instruction "dim_user_data 是核心的使用者資訊表，包含了 user_id, user_email, backend_user_id, user_role 等重要欄位。建議規則：查詢使用者相關資訊時應優先使用此表，注意區分 user_id 和 backend_user_id 的差異。" "如何查詢使用者資訊？;user_id 和 backend_user_id 有什麼不同？" "false"; then
    ((success_count++))
fi
((total_count++))

# 4. 日期格式規則
echo ""
echo "4/5 日期格式規則"
if create_instruction "在處理日期相關查詢時，請注意：1. calendar_date 使用 YYYY-MM-DD 格式 2. session_year_type_tw 表示台灣學年學期制 3. 日期比較時請使用適當的日期函數" "如何處理日期查詢？;台灣學年學期制如何表示？;日期格式是什麼？" "false"; then
    ((success_count++))
fi
((total_count++))

# 5. SQL 最佳實踐
echo ""
echo "5/5 SQL 最佳實踐"
if create_instruction "SQL 生成最佳實踐：1. 使用明確的 JOIN 語法而非隱式連接 2. 為複雜查詢添加適當的索引提示 3. 使用 LIMIT 來控制結果集大小 4. 避免使用 SELECT * 5. 對於大表查詢考慮分頁處理" "" "true"; then
    ((success_count++))
fi
((total_count++))

echo ""
echo "=================================================="
echo "📊 匯入結果統計:"
echo "✅ 成功: $success_count"
echo "❌ 失敗: $((total_count - success_count))"
echo "📋 總計: $total_count"

if [ $success_count -gt 0 ]; then
    echo ""
    echo "🎉 Instructions 已成功匯入到 UI 系統！"
    echo "💡 這些指令現在會同時存在於:"
    echo "   - UI SQLite 資料庫 (用於顯示)"
    echo "   - Qdrant 向量資料庫 (用於語意搜尋)"
    echo ""
    echo "🔄 請重新整理瀏覽器頁面來查看新的 instructions"
else
    echo ""
    echo "⚠️  沒有成功匯入任何指令，請檢查錯誤訊息"
fi 