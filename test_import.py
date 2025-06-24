#!/usr/bin/env python3
"""
測試 SQL Pairs 匯入腳本 - 匯入前 50 筆進行測試
"""

import requests
import json
import csv
import time
import sys
from pathlib import Path

# 配置
UI_GRAPHQL_ENDPOINT = "http://localhost:3000/api/graphql"
SQL_PAIRS_CSV = "/Users/i-am-alvin/Development/junyi/WrenAI/docker/data/sql_pairs.csv"
TEST_LIMIT = 50  # 只測試前 50 筆

def create_sql_pair_via_graphql(question, sql):
    """透過 GraphQL API 建立 SQL pair"""
    mutation = """
    mutation CreateSqlPair($data: CreateSqlPairInput!) {
        createSqlPair(data: $data) {
            id
            projectId
            sql
            question
            createdAt
            updatedAt
        }
    }
    """
    
    payload = {
        "query": mutation,
        "variables": {
            "data": {
                "question": question,
                "sql": sql
            }
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
                return False, f"GraphQL Error: {result['errors']}"
            else:
                return True, result['data']['createSqlPair']['id']
        else:
            return False, f"HTTP Error: {response.status_code}"
    except Exception as e:
        return False, f"Exception: {e}"

def main():
    print(f"🧪 測試匯入前 {TEST_LIMIT} 筆 SQL Pairs")
    print("=" * 50)
    
    success_count = 0
    failed_count = 0
    total_count = 0
    
    with open(SQL_PAIRS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if total_count >= TEST_LIMIT:
                break
                
            total_count += 1
            question = row['question']
            sql = row['sql']
            
            print(f"\n📝 處理 SQL pair {total_count}: {question[:50]}...")
            
            success, result = create_sql_pair_via_graphql(question, sql)
            if success:
                print(f"   ✅ 成功 - ID: {result}")
                success_count += 1
            else:
                print(f"   ❌ 失敗: {result}")
                failed_count += 1
            
            time.sleep(0.5)  # 適度延遲
    
    print(f"\n📊 測試結果:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失敗: {failed_count}")
    print(f"📋 總計: {total_count}")
    print(f"💡 成功率: {success_count/total_count*100:.1f}%")

if __name__ == "__main__":
    main() 