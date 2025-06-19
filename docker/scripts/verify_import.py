#!/usr/bin/env python3
"""
Verify imported data in WrenAI
"""

import requests
import json

def verify_qdrant_instructions():
    """Verify instructions in Qdrant"""
    try:
        response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', 
                               json={'limit': 100, 'with_payload': True})
        result = response.json()
        
        print('📋 Instructions in Qdrant:')
        instructions = result['result']['points']
        
        for i, point in enumerate(instructions[:10], 1):  # Show first 10
            payload = point.get('payload', {})
            instruction_text = payload.get('instruction', 'N/A')[:100] + '...' if len(payload.get('instruction', '')) > 100 else payload.get('instruction', 'N/A')
            print(f'  {i}. ID: {payload.get("id", "N/A")} - Default: {payload.get("is_default", False)}')
            print(f'     Text: {instruction_text}')
        
        print(f'  Total instructions: {len(instructions)}')
        return len(instructions)
        
    except Exception as e:
        print(f'❌ Error checking instructions: {e}')
        return 0

def verify_qdrant_sql_pairs():
    """Verify SQL pairs in Qdrant"""
    try:
        response = requests.post('http://qdrant:6333/collections/sql_pairs/points/scroll', 
                               json={'limit': 100, 'with_payload': True})
        result = response.json()
        
        print('\n📋 SQL Pairs in Qdrant:')
        sql_pairs = result['result']['points']
        
        for i, point in enumerate(sql_pairs, 1):
            payload = point.get('payload', {})
            question = payload.get('question', 'N/A')[:50] + '...' if len(payload.get('question', '')) > 50 else payload.get('question', 'N/A')
            print(f'  {i}. Question: {question}')
        
        print(f'  Total SQL pairs in Qdrant: {len(sql_pairs)}')
        return len(sql_pairs)
        
    except Exception as e:
        print(f'❌ Error checking SQL pairs: {e}')
        return 0

def verify_ui_sql_pairs():
    """Verify SQL pairs in UI database"""
    try:
        query = '''
        query {
          sqlPairs {
            id
            question
            createdAt
          }
        }
        '''
        
        response = requests.post('http://localhost:3000/api/graphql', 
                               json={'query': query})
        result = response.json()
        
        print('\n📋 SQL Pairs in UI Database:')
        sql_pairs = result['data']['sqlPairs']
        
        for pair in sql_pairs:
            question = pair['question'][:50] + '...' if len(pair['question']) > 50 else pair['question']
            print(f'  ID {pair["id"]}: {question} (Created: {pair["createdAt"]})')
        
        print(f'  Total SQL pairs in UI: {len(sql_pairs)}')
        return len(sql_pairs)
        
    except Exception as e:
        print(f'❌ Error checking UI SQL pairs: {e}')
        return 0

def verify_qdrant_collections():
    """Verify all Qdrant collections"""
    try:
        response = requests.get('http://qdrant:6333/collections')
        collections = response.json()
        
        print('\n📋 All Qdrant Collections:')
        for collection in collections['result']['collections']:
            # Get collection info
            info_response = requests.get(f'http://qdrant:6333/collections/{collection["name"]}')
            info = info_response.json()
            points_count = info['result']['points_count']
            print(f'  {collection["name"]}: {points_count} points')
        
    except Exception as e:
        print(f'❌ Error checking collections: {e}')

def main():
    print('🔍 WrenAI 匯入資料驗證')
    print('='*50)
    
    # Verify instructions
    instructions_count = verify_qdrant_instructions()
    
    # Verify SQL pairs in Qdrant
    qdrant_sql_count = verify_qdrant_sql_pairs()
    
    # Verify SQL pairs in UI
    ui_sql_count = verify_ui_sql_pairs()
    
    # Verify all collections
    verify_qdrant_collections()
    
    # Summary
    print('\n' + '='*50)
    print('📊 匯入驗證摘要:')
    print(f'✅ Instructions (Qdrant): {instructions_count}')
    print(f'✅ SQL Pairs (Qdrant): {qdrant_sql_count}')
    print(f'✅ SQL Pairs (UI Database): {ui_sql_count}')
    
    if instructions_count > 0 and ui_sql_count > 0:
        print('\n🎉 匯入成功！所有資料都已正確載入到 WrenAI 系統中。')
        print('💡 您現在可以在 WrenAI UI 中看到這些 instructions 和 SQL pairs。')
    else:
        print('\n⚠️  部分匯入可能有問題，請檢查上述錯誤訊息。')

if __name__ == '__main__':
    main() 