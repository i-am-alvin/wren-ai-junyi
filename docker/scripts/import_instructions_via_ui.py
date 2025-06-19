#!/usr/bin/env python3
"""
Import instructions from CSV file to WrenAI via UI GraphQL API
This is the correct way to import instructions as it:
1. Stores instructions in UI database
2. Triggers proper indexing to Qdrant via WrenAI service
3. Maintains data consistency
"""

import csv
import json
import requests
import sys
import time

def create_instruction_via_api(instruction_data, ui_graphql_endpoint):
    """Create instruction via GraphQL API"""
    
    mutation = """
    mutation CreateInstruction($data: CreateInstructionInput!) {
        createInstruction(data: $data) {
            id
            projectId
            instruction
            questions
            isDefault
            createdAt
            updatedAt
        }
    }
    """
    
    payload = {
        "query": mutation,
        "variables": {
            "data": instruction_data
        }
    }
    
    try:
        response = requests.post(
            ui_graphql_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                return f"ERROR: {result['errors']}"
            else:
                return f"SUCCESS: {result['data']['createInstruction']['id']}"
        else:
            return f"HTTP_ERROR: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"EXCEPTION: {e}"

def main():
    csv_file = 'data/instructions.csv'
    ui_graphql_endpoint = 'http://localhost:3000/api/graphql'
    
    print('🚀 開始透過 UI API 匯入 Instructions...')
    print('📋 這是正確的匯入方式，會同時更新 UI 資料庫和 Qdrant')
    
    success_count = 0
    total_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validate required columns
            required_columns = ["instruction_id", "instruction", "is_default"]
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                print(f"❌ 缺少必要欄位: {missing_columns}")
                sys.exit(1)
            
            print(f"📋 CSV 欄位: {reader.fieldnames}")
            
            for row in reader:
                total_count += 1
                
                try:
                    instruction_text = row['instruction'].strip()
                    questions_str = row.get('questions', '').strip()
                    is_default = row['is_default'].strip().lower() == 'true'
                    
                    if not instruction_text:
                        print(f"❌ 第 {total_count} 行: instruction 不能為空")
                        continue
                    
                    # Parse questions
                    questions = []
                    if questions_str:
                        questions = [q.strip() for q in questions_str.split(';') if q.strip()]
                    
                    # Prepare instruction data for API
                    instruction_data = {
                        'instruction': instruction_text,
                        'questions': questions,
                        'isDefault': is_default
                    }
                    
                    print(f'📝 匯入 instruction {total_count}: {instruction_text[:50]}...')
                    print(f'   Questions: {len(questions)}, Default: {is_default}')
                    
                    result = create_instruction_via_api(instruction_data, ui_graphql_endpoint)
                    
                    if 'SUCCESS' in result:
                        success_count += 1
                        instruction_id = result.split(':')[1].strip()
                        print(f'   ✅ 成功 - ID: {instruction_id}')
                        
                        # Add delay to avoid overwhelming the API
                        time.sleep(0.5)
                    else:
                        print(f'   ❌ 失敗: {result}')
                
                except KeyError as e:
                    print(f"❌ 第 {total_count} 行: 缺少欄位 {e}")
                except Exception as e:
                    print(f"❌ 第 {total_count} 行: 處理錯誤 - {e}")
    
    except FileNotFoundError:
        print(f'❌ 檔案不存在: {csv_file}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ 錯誤: {e}')
        sys.exit(1)
    
    print(f'\n📊 匯入結果:')
    print(f'✅ 成功: {success_count}')
    print(f'❌ 失敗: {total_count - success_count}')
    print(f'📋 總計: {total_count}')
    
    if success_count > 0:
        print(f'\n💡 Instructions 已正確匯入到:')
        print(f'   📊 UI 資料庫 (可在介面中管理)')
        print(f'   🔍 Qdrant 向量資料庫 (用於 AI 查詢)')

if __name__ == '__main__':
    main() 