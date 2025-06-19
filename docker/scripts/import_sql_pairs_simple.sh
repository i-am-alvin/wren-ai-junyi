#!/bin/bash

# Import SQL-Question Pairs via UI GraphQL API (Simplified Version)
# This script imports simple SQL-question pairs to demonstrate the process

UI_GRAPHQL_ENDPOINT="http://localhost:3000/api/graphql"

echo "🚀 開始透過 UI GraphQL API 匯入 SQL-Question Pairs (簡化版)"
echo "============================================================="

# Function to create SQL pair via GraphQL
create_sql_pair() {
    local question="$1"
    local sql="$2"
    
    echo "📝 建立 SQL pair:"
    echo "   問題: $question"
    echo "   SQL: $(echo "$sql" | head -1 | cut -c1-60)..."
    
    # Use Python to properly escape JSON
    response=$(python3 -c "
import json
import requests

query = '''
mutation CreateSqlPair(\$data: CreateSqlPairInput!) {
  createSqlPair(data: \$data) {
    id
    projectId
    sql
    question
    createdAt
    updatedAt
  }
}
'''

variables = {
    'data': {
        'question': '''$question''',
        'sql': '''$sql'''
    }
}

payload = {
    'query': query,
    'variables': variables
}

try:
    response = requests.post(
        '$UI_GRAPHQL_ENDPOINT',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print(f'ERROR: {result[\"errors\"]}')
        else:
            data = result['data']['createSqlPair']
            print(f'SUCCESS: {data[\"id\"]}')
    else:
        print(f'HTTP_ERROR: {response.status_code}')
        
except Exception as e:
    print(f'EXCEPTION: {e}')
")
    
    if echo "$response" | grep -q "SUCCESS:"; then
        local id=$(echo "$response" | grep "SUCCESS:" | cut -d':' -f2 | tr -d ' ')
        echo "   ✅ 成功 - ID: $id"
        return 0
    else
        echo "   ❌ 失敗: $response"
        return 1
    fi
}

echo ""
echo "📋 開始匯入 SQL-Question Pairs..."

success_count=0
total_count=0

# 1. 簡單的使用者統計
echo ""
echo "1/3 使用者統計"
sql1="-- CTE: 使用者統計 - 計算使用者總數
WITH user_stats AS (
  SELECT 
    user_role,
    COUNT(*) as user_count
  FROM dim_user_data 
  GROUP BY user_role
)
SELECT 
  user_role,
  user_count
FROM user_stats 
ORDER BY user_count DESC;"

if create_sql_pair "每個使用者角色有多少人？" "$sql1"; then
    ((success_count++))
fi
((total_count++))

# 2. 班級統計
echo ""
echo "2/3 班級統計"
sql2="-- CTE: 班級統計 - 統計班級資訊
WITH class_stats AS (
  SELECT 
    class_name,
    COUNT(DISTINCT teacher_user_id) as teachers,
    COUNT(DISTINCT student_user_id) as students
  FROM dim_teacher_student_joins 
  GROUP BY class_name
)
SELECT 
  class_name,
  teachers,
  students
FROM class_stats 
ORDER BY (teachers + students) DESC
LIMIT 5;"

if create_sql_pair "每個班級有多少老師和學生？" "$sql2"; then
    ((success_count++))
fi
((total_count++))

# 3. 學校統計
echo ""
echo "3/3 學校統計"
sql3="-- CTE: 學校統計 - 統計學校分布
WITH school_stats AS (
  SELECT 
    school_city,
    COUNT(*) as school_count
  FROM dim_schools_metadata 
  GROUP BY school_city
)
SELECT 
  school_city,
  school_count
FROM school_stats 
ORDER BY school_count DESC
LIMIT 10;"

if create_sql_pair "每個縣市有多少學校？" "$sql3"; then
    ((success_count++))
fi
((total_count++))

echo ""
echo "============================================================="
echo "📊 匯入結果統計:"
echo "✅ 成功: $success_count"
echo "❌ 失敗: $((total_count - success_count))"
echo "📋 總計: $total_count"

if [ $success_count -gt 0 ]; then
    echo ""
    echo "🎉 SQL-Question Pairs 已成功匯入到系統！"
    echo "💡 這些 SQL pairs 現在會同時存在於:"
    echo "   - UI SQLite 資料庫 (用於顯示和管理)"
    echo "   - Qdrant 向量資料庫 (用於語意搜尋和 AI 學習)"
    echo ""
    echo "📋 所有 SQL 都包含 CTE 註解，符合我們設定的全域指令"
    echo "🔄 請重新整理瀏覽器頁面來查看新的 SQL pairs"
else
    echo ""
    echo "⚠️  沒有成功匯入任何 SQL pair，請檢查錯誤訊息"
fi 