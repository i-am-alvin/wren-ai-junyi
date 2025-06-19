#!/usr/bin/env python3
"""
Import SQL pairs from CSV file to WrenAI UI via GraphQL API
"""

import csv
import json
import requests
import sys

def create_sql_pair(question, sql, ui_graphql_endpoint):
    """Create a SQL pair via GraphQL API"""
    query = '''
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
    '''
    
    variables = {
        'data': {
            'question': question,
            'sql': sql
        }
    }
    
    payload = {
        'query': query,
        'variables': variables
    }
    
    try:
        response = requests.post(ui_graphql_endpoint, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                return f'ERROR: {result["errors"]}'
            else:
                data = result['data']['createSqlPair']
                return f'SUCCESS: {data["id"]}'
        else:
            return f'HTTP_ERROR: {response.status_code}'
    except Exception as e:
        return f'EXCEPTION: {e}'

def main():
    csv_file = 'data/sql_pairs.csv'
    ui_graphql_endpoint = 'http://localhost:3000/api/graphql'
    
    print('🚀 開始匯入原始 CSV 中的 SQL pairs...')
    success_count = 0
    total_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_count += 1
                question = row['question']
                sql = row['sql']
                
                print(f'📝 匯入 SQL pair {total_count}: {question[:50]}...')
                result = create_sql_pair(question, sql, ui_graphql_endpoint)
                
                if 'SUCCESS' in result:
                    success_count += 1
                    print(f'   ✅ 成功 - ID: {result.split(":")[1].strip()}')
                else:
                    print(f'   ❌ 失敗: {result}')
    
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

if __name__ == '__main__':
    main() 