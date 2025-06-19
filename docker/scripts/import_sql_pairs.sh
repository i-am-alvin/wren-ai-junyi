#!/bin/bash

# Import SQL-Question Pairs via UI GraphQL API
# This script imports SQL-question pairs through the UI's GraphQL API

UI_GRAPHQL_ENDPOINT="http://localhost:3000/api/graphql"

echo "🚀 開始透過 UI GraphQL API 匯入 SQL-Question Pairs"
echo "======================================================"

# Function to create SQL pair via GraphQL
create_sql_pair() {
    local question="$1"
    local sql="$2"
    
    # Escape quotes in SQL and question for JSON
    local escaped_sql=$(echo "$sql" | sed 's/"/\\"/g' | tr '\n' ' ')
    local escaped_question=$(echo "$question" | sed 's/"/\\"/g')
    
    local payload=$(cat <<EOF
{
  "query": "mutation CreateSqlPair(\$data: CreateSqlPairInput!) { createSqlPair(data: \$data) { id projectId sql question createdAt updatedAt } }",
  "variables": {
    "data": {
      "question": "$escaped_question",
      "sql": "$escaped_sql"
    }
  }
}
EOF
)
    
    echo "📝 建立 SQL pair:"
    echo "   問題: $question"
    echo "   SQL: $(echo "$sql" | head -1 | cut -c1-60)..."
    
    response=$(curl -s -X POST "$UI_GRAPHQL_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | grep -q '"errors"'; then
        echo "   ❌ 失敗: $(echo "$response" | grep -o '"message":"[^"]*"' | head -1)"
        return 1
    elif echo "$response" | grep -q '"createSqlPair"'; then
        local id=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   ✅ 成功 - ID: $id"
        return 0
    else
        echo "   ❌ 未知錯誤: $response"
        return 1
    fi
}

echo ""
echo "📋 開始匯入 SQL-Question Pairs..."

success_count=0
total_count=0

# 1. 使用者角色統計（含 CTE 註解）
echo ""
echo "1/5 使用者角色統計"
sql1="-- CTE: 使用者角色統計 - 計算每個角色的使用者數量
WITH user_role_stats AS (
  SELECT 
    user_role,
    COUNT(*) as user_count
  FROM dim_user_data 
  GROUP BY user_role
)
SELECT 
  user_role,
  user_count,
  ROUND(user_count * 100.0 / SUM(user_count) OVER(), 2) as percentage
FROM user_role_stats 
ORDER BY user_count DESC;"

if create_sql_pair "每個使用者角色有多少人？比例是多少？" "$sql1"; then
    ((success_count++))
fi
((total_count++))

# 2. 師生關係查詢（含 CTE 註解）
echo ""
echo "2/5 師生關係查詢"
sql2="-- CTE: 班級師生統計 - 統計每個班級的師生數量
WITH class_stats AS (
  SELECT 
    class_id,
    class_name,
    COUNT(DISTINCT teacher_user_id) as teacher_count,
    COUNT(DISTINCT student_user_id) as student_count
  FROM dim_teacher_student_joins 
  GROUP BY class_id, class_name
)
SELECT 
  class_name,
  teacher_count,
  student_count,
  (teacher_count + student_count) as total_members
FROM class_stats 
ORDER BY total_members DESC
LIMIT 10;"

if create_sql_pair "每個班級有多少老師和學生？" "$sql2"; then
    ((success_count++))
fi
((total_count++))

# 3. 學校統計（含 CTE 註解）
echo ""
echo "3/5 學校統計"
sql3="-- CTE: 學校統計 - 計算每個學校的基本資訊
WITH school_stats AS (
  SELECT 
    school_name,
    school_city,
    school_level_type,
    COUNT(*) as record_count
  FROM dim_schools_metadata 
  GROUP BY school_name, school_city, school_level_type
)
SELECT 
  school_city,
  school_level_type,
  COUNT(*) as school_count,
  SUM(record_count) as total_records
FROM school_stats 
GROUP BY school_city, school_level_type
ORDER BY school_count DESC;"

if create_sql_pair "每個縣市各學制的學校數量是多少？" "$sql3"; then
    ((success_count++))
fi
((total_count++))

# 4. 日期範圍查詢（含 CTE 註解）
echo ""
echo "4/5 日期範圍查詢"
sql4="-- CTE: 最近活動 - 查詢最近一週的使用者活動
WITH recent_activity AS (
  SELECT 
    DATE(created_at_tw) as activity_date,
    user_role,
    COUNT(*) as daily_count
  FROM dim_user_data 
  WHERE created_at_tw >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  GROUP BY DATE(created_at_tw), user_role
)
SELECT 
  activity_date,
  user_role,
  daily_count,
  SUM(daily_count) OVER (PARTITION BY activity_date) as total_daily
FROM recent_activity 
ORDER BY activity_date DESC, daily_count DESC;"

if create_sql_pair "最近一週每天各角色的使用者註冊數量？" "$sql4"; then
    ((success_count++))
fi
((total_count++))

# 5. 複雜聯結查詢（含 CTE 註解）
echo ""
echo "5/5 複雜聯結查詢"
sql5="-- CTE: 學校使用者統計 - 結合學校和使用者資訊
WITH school_user_stats AS (
  SELECT 
    s.school_name,
    s.school_city,
    u.user_role,
    COUNT(u.user_id) as user_count
  FROM dim_schools_metadata s
  LEFT JOIN dim_user_data u ON s.school_id_sha256 = u.school_id_sha256
  GROUP BY s.school_name, s.school_city, u.user_role
),
-- CTE: 學校總計 - 計算每個學校的總使用者數
school_totals AS (
  SELECT 
    school_name,
    school_city,
    SUM(user_count) as total_users
  FROM school_user_stats
  GROUP BY school_name, school_city
)
SELECT 
  st.school_name,
  st.school_city,
  sus.user_role,
  sus.user_count,
  st.total_users,
  ROUND(sus.user_count * 100.0 / st.total_users, 2) as role_percentage
FROM school_user_stats sus
JOIN school_totals st ON sus.school_name = st.school_name AND sus.school_city = st.school_city
WHERE st.total_users > 0
ORDER BY st.total_users DESC, sus.user_count DESC
LIMIT 20;"

if create_sql_pair "各學校不同角色的使用者分布情況？" "$sql5"; then
    ((success_count++))
fi
((total_count++))

echo ""
echo "======================================================"
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