#!/usr/bin/env python3
"""
WrenAI SQL Pairs 大量匯入腳本
正確調用 UI GraphQL API 來匯入大量的 SQL Pairs
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

def check_wrenai_service():
    """檢查 WrenAI 服務是否運行"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return True
    except:
        return False

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
    """主要執行函數"""
    print("🎯 WrenAI SQL Pairs 大量匯入工具")
    print("=" * 60)
    
    # 檢查服務狀態
    print("📋 檢查 WrenAI 服務狀態...")
    if not check_wrenai_service():
        print("❌ WrenAI UI 服務未運行於 http://localhost:3000")
        print("💡 請先啟動 WrenAI：")
        print("   cd /Users/i-am-alvin/Development/junyi/WrenAI")
        print("   docker-compose up -d")
        sys.exit(1)
    print("✅ WrenAI 服務正在運行")
    
    # 檢查檔案是否存在
    if not Path(SQL_PAIRS_CSV).exists():
        print(f"❌ 找不到檔案: {SQL_PAIRS_CSV}")
        sys.exit(1)
    
    print(f"📁 CSV 檔案: {SQL_PAIRS_CSV}")
    
    # 開始匯入 SQL Pairs
    print("\n🚀 開始大量匯入 SQL Pairs...")
    print("=" * 50)
    
    success_count = 0
    failed_count = 0
    total_count = 0
    
    with open(SQL_PAIRS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_count += 1
            question = row['question']
            sql = row['sql']
            
            # 每 100 筆顯示一次進度
            if total_count % 100 == 0 or total_count <= 10:
                print(f"\n📝 處理 SQL pair {total_count}: {question[:50]}...")
            
            success, result = create_sql_pair_via_graphql(question, sql)
            if success:
                if total_count % 100 == 0 or total_count <= 10:
                    print(f"   ✅ 成功 - ID: {result}")
                success_count += 1
            else:
                print(f"   ❌ 失敗 ({total_count}): {result}")
                failed_count += 1
            
            # 控制請求頻率，避免過載
            if total_count % 100 == 0:
                print(f"   💤 已處理 {total_count} 筆，暫停 3 秒...")
                time.sleep(3)
            elif total_count % 10 == 0:
                time.sleep(0.5)
            else:
                time.sleep(0.1)
    
    # 總結報告
    print("\n" + "=" * 60)
    print("📊 SQL Pairs 匯入結果總結")
    print("=" * 60)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失敗: {failed_count}")
    print(f"📋 總計: {total_count}")
    
    if success_count > 0:
        success_rate = success_count / total_count * 100
        print(f"💡 匯入成功率: {success_rate:.1f}%")
        print("\n🎊 SQL Pairs 已成功匯入到 WrenAI 系統！")
        print("🔗 您現在可以訪問 http://localhost:3000/knowledge/question-sql-pairs 查看匯入的資料")
    else:
        print("\n⚠️ 沒有成功匯入任何 SQL Pairs，請檢查錯誤訊息")

if __name__ == "__main__":
    main() 