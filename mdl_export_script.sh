#!/bin/bash

# WrenAI MDL Export Script
# 自動化導出 WrenAI 建模定義
# 作者: Development Team
# 版本: 1.0
# 更新日期: 2024-06-22

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：印出帶顏色的訊息
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函數：檢查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 '$1' 未找到，請先安裝"
        exit 1
    fi
}

# 函數：檢查 Docker 容器狀態
check_docker_container() {
    local container_name=$1
    if ! docker ps | grep -q $container_name; then
        print_error "Docker 容器 '$container_name' 未運行"
        print_status "請先啟動 WrenAI Docker 環境"
        exit 1
    fi
    print_success "Docker 容器 '$container_name' 運行正常"
}

# 函數：執行 GraphQL 查詢
execute_graphql_query() {
    local query=$1
    local container_name=${2:-"wrenai-wren-ui-1"}
    
    docker exec -it $container_name curl -s -X POST http://localhost:3000/api/graphql \
        -H "Content-Type: application/json" \
        -d "$query"
}

# 函數：獲取部署哈希
get_deploy_hash() {
    print_status "執行部署以獲取最新哈希..."
    
    local deploy_result=$(execute_graphql_query '{"query": "mutation { deploy(force: false) }"}')
    
    if echo "$deploy_result" | jq -e '.data.deploy' &> /dev/null; then
        print_success "部署成功"
    else
        print_error "部署失敗"
        echo "$deploy_result" | jq
        exit 1
    fi
    
    print_status "獲取部署哈希..."
    local hash_result=$(execute_graphql_query '{"query": "{ deployLogQuery { hash } }"}')
    local deploy_hash=$(echo "$hash_result" | jq -r '.data.deployLogQuery[-1].hash')
    
    if [ "$deploy_hash" = "null" ] || [ -z "$deploy_hash" ]; then
        print_error "無法獲取部署哈希"
        exit 1
    fi
    
    print_success "獲取到部署哈希: $deploy_hash"
    echo "$deploy_hash"
}

# 函數：導出 MDL
export_mdl() {
    local deploy_hash=$1
    local output_file=${2:-"exported_mdl_$(date +%Y%m%d_%H%M%S).json"}
    
    print_status "使用哈希 $deploy_hash 導出 MDL..."
    
    # 構建 GraphQL 查詢
    local query="{
        \"query\": \"query GetMDL(\$hash: String!) { getMDL(hash: \$hash) { hash mdl } }\",
        \"variables\": {
            \"hash\": \"$deploy_hash\"
        }
    }"
    
    # 執行查詢並保存響應
    local temp_response="/tmp/mdl_response_$$.json"
    execute_graphql_query "$query" > "$temp_response"
    
    # 檢查響應是否包含 MDL 數據
    if ! jq -e '.data.getMDL.mdl' "$temp_response" &> /dev/null; then
        print_error "MDL 導出失敗"
        cat "$temp_response" | jq
        rm -f "$temp_response"
        exit 1
    fi
    
    # 解碼 base64 並格式化 JSON
    print_status "解碼並格式化 MDL 數據..."
    cat "$temp_response" | jq -r '.data.getMDL.mdl' | base64 -d | jq > "$output_file"
    
    if [ $? -eq 0 ]; then
        print_success "MDL 導出成功: $output_file"
        rm -f "$temp_response"
    else
        print_error "MDL 格式化失敗"
        rm -f "$temp_response"
        exit 1
    fi
    
    echo "$output_file"
}

# 函數：驗證導出的 MDL
validate_mdl() {
    local mdl_file=$1
    
    print_status "驗證 MDL 文件..."
    
    # 檢查文件是否存在
    if [ ! -f "$mdl_file" ]; then
        print_error "MDL 文件不存在: $mdl_file"
        return 1
    fi
    
    # 檢查 JSON 格式
    if ! jq empty "$mdl_file" 2>/dev/null; then
        print_error "MDL 文件不是有效的 JSON 格式"
        return 1
    fi
    
    # 檢查必要字段
    local required_fields=("schema" "catalog" "dataSource" "models" "relationships" "views")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$mdl_file" &> /dev/null; then
            print_error "MDL 文件缺少必要字段: $field"
            return 1
        fi
    done
    
    # 顯示基本統計
    local file_size=$(du -h "$mdl_file" | cut -f1)
    local model_count=$(jq '.models | length' "$mdl_file")
    local relationship_count=$(jq '.relationships | length' "$mdl_file")
    local data_source=$(jq -r '.dataSource' "$mdl_file")
    local catalog=$(jq -r '.catalog' "$mdl_file")
    
    print_success "MDL 驗證通過"
    echo ""
    echo "=== MDL 摘要 ==="
    echo "文件大小: $file_size"
    echo "資料源: $data_source"
    echo "目錄: $catalog"
    echo "模型數量: $model_count"
    echo "關係數量: $relationship_count"
    echo ""
    
    # 顯示模型列表
    echo "模型列表:"
    jq -r '.models[] | "  - " + .name + " (" + (.columns | length | tostring) + " 列)"' "$mdl_file"
    
    return 0
}

# 主函數
main() {
    print_status "開始 WrenAI MDL 導出流程"
    
    # 檢查必要工具
    check_command "docker"
    check_command "jq"
    check_command "base64"
    
    # 檢查 Docker 容器
    check_docker_container "wrenai-wren-ui-1"
    
    # 獲取部署哈希
    local deploy_hash=$(get_deploy_hash)
    
    # 設置輸出文件名
    local output_file="exported_mdl_$(date +%Y%m%d_%H%M%S)_${deploy_hash:0:8}.json"
    
    # 導出 MDL
    local exported_file=$(export_mdl "$deploy_hash" "$output_file")
    
    # 驗證導出結果
    if validate_mdl "$exported_file"; then
        print_success "MDL 導出完成: $exported_file"
        
        # 詢問是否要移動到特定目錄
        if [ -d "./backups" ]; then
            print_status "檢測到 backups 目錄，是否移動文件? (y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                mv "$exported_file" "./backups/"
                print_success "文件已移動到 ./backups/$exported_file"
            fi
        fi
    else
        print_error "MDL 驗證失敗"
        exit 1
    fi
}

# 腳本入口點
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 