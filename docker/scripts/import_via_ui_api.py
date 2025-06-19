#!/usr/bin/env python3
"""
Import Instructions via UI GraphQL API

This script properly imports instructions through the UI's GraphQL API,
which will handle both SQLite storage and Qdrant indexing automatically.
"""

import requests
import json
import csv
import time
from pathlib import Path

# Configuration
UI_GRAPHQL_ENDPOINT = "http://localhost:3000/api/graphql"
CSV_FILE_PATH = "/app/docker/data/instructions.csv"

def read_csv_instructions(csv_path: str):
    """Read instructions from CSV file"""
    instructions = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse questions (semicolon separated)
            questions = [q.strip() for q in row['questions'].split(';') if q.strip()] if row['questions'] else []
            
            # Convert is_default to boolean
            is_default = row['is_default'].lower() in ('true', '1', 'yes')
            
            instruction_data = {
                'instruction': row['instruction'],
                'questions': questions,
                'isDefault': is_default
            }
            
            instructions.append({
                'id': row['instruction_id'],
                'data': instruction_data
            })
    
    return instructions

def create_instruction_via_graphql(instruction_data):
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
            UI_GRAPHQL_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ GraphQL Error: {result['errors']}")
                return None
            else:
                return result['data']['createInstruction']
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def main():
    print("🚀 開始透過 UI API 匯入 Instructions")
    print("=" * 50)
    
    # Check if CSV file exists
    if not Path(CSV_FILE_PATH).exists():
        print(f"❌ CSV 檔案不存在: {CSV_FILE_PATH}")
        return
    
    # Read instructions from CSV
    try:
        instructions = read_csv_instructions(CSV_FILE_PATH)
        print(f"📋 從 CSV 讀取到 {len(instructions)} 個指令")
    except Exception as e:
        print(f"❌ 讀取 CSV 檔案失敗: {e}")
        return
    
    # Create instructions via GraphQL API
    success_count = 0
    failed_count = 0
    
    for i, instruction in enumerate(instructions, 1):
        print(f"\n📝 處理指令 {i}/{len(instructions)}: {instruction['id']}")
        print(f"   指令內容: {instruction['data']['instruction'][:100]}...")
        print(f"   問題數量: {len(instruction['data']['questions'])}")
        print(f"   全域指令: {instruction['data']['isDefault']}")
        
        result = create_instruction_via_graphql(instruction['data'])
        
        if result:
            print(f"   ✅ 成功建立 - UI ID: {result['id']}, Project: {result['projectId']}")
            success_count += 1
        else:
            print(f"   ❌ 建立失敗")
            failed_count += 1
        
        # Add delay between requests to avoid overwhelming the server
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 匯入結果統計:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失敗: {failed_count}")
    print(f"📋 總計: {len(instructions)}")
    
    if success_count > 0:
        print("\n🎉 Instructions 已成功匯入到 UI 系統！")
        print("💡 這些指令現在會同時存在於:")
        print("   - UI SQLite 資料庫 (用於顯示)")
        print("   - Qdrant 向量資料庫 (用於語意搜尋)")
    else:
        print("\n⚠️  沒有成功匯入任何指令，請檢查錯誤訊息")

if __name__ == "__main__":
    main() 