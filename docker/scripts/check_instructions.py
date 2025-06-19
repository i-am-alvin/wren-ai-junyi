#!/usr/bin/env python3
"""
Check Instructions in Qdrant

This script displays all instructions stored in Qdrant for validation.
"""

import requests
import json
from datetime import datetime

def check_instructions():
    try:
        # 獲取所有 instructions
        response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', 
                                json={'limit': 100, 'with_payload': True})
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch instructions: {response.status_code}")
            return
        
        result = response.json()
        points = result.get('result', {}).get('points', [])
        
        print('=' * 80)
        print('📋 WrenAI Instructions 驗證報告')
        print('=' * 80)
        print(f'⏰ 檢查時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'📊 總共找到: {len(points)} 個 instructions')
        print()
        
        if not points:
            print("⚠️  沒有找到任何 instructions")
            return
        
        # 按 project_id 分組
        project_groups = {}
        for point in points:
            project_id = point['payload'].get('project_id', 'unknown')
            if project_id not in project_groups:
                project_groups[project_id] = []
            project_groups[project_id].append(point)
        
        # 顯示每個 project 的 instructions
        for project_id, project_points in project_groups.items():
            print(f'🎯 Project ID: {project_id} ({len(project_points)} instructions)')
            print('-' * 60)
            
            # 分類 default 和 non-default
            default_instructions = [p for p in project_points if p['payload'].get('is_default', False)]
            question_instructions = [p for p in project_points if not p['payload'].get('is_default', False)]
            
            # 顯示 default instructions
            if default_instructions:
                print('🌐 全域指令 (Default Instructions):')
                for i, point in enumerate(default_instructions, 1):
                    payload = point['payload']
                    instruction_id = payload.get('instruction_id', 'N/A')
                    instruction_text = payload.get('instruction', 'N/A')
                    
                    print(f'  {i}. 📝 ID: {instruction_id}')
                    print(f'     📋 指令: {instruction_text}')
                    print()
            
            # 顯示 question-based instructions
            if question_instructions:
                print('❓ 問題導向指令 (Question-based Instructions):')
                
                # 按 instruction_id 分組
                instruction_groups = {}
                for point in question_instructions:
                    inst_id = point['payload'].get('instruction_id', 'unknown')
                    if inst_id not in instruction_groups:
                        instruction_groups[inst_id] = []
                    instruction_groups[inst_id].append(point)
                
                for inst_id, inst_points in instruction_groups.items():
                    print(f'  📝 ID: {inst_id} ({len(inst_points)} 個問題)')
                    
                    # 顯示指令內容（取第一個）
                    first_point = inst_points[0]
                    instruction_text = first_point['payload'].get('instruction', 'N/A')
                    print(f'     📋 指令: {instruction_text}')
                    
                    # 顯示所有相關問題
                    print(f'     ❓ 相關問題:')
                    for j, point in enumerate(inst_points, 1):
                        content = point.get('content', 'N/A')
                        print(f'        {j}. {content}')
                    print()
            
            print()
        
        # 統計摘要
        print('📈 統計摘要:')
        print('-' * 30)
        total_default = sum(1 for p in points if p['payload'].get('is_default', False))
        total_questions = len(points) - total_default
        unique_instruction_ids = len(set(p['payload'].get('instruction_id', '') for p in points))
        
        print(f'🌐 全域指令總數: {total_default}')
        print(f'❓ 問題導向指令總數: {total_questions}')
        print(f'📝 唯一指令 ID 數量: {unique_instruction_ids}')
        print(f'🎯 涵蓋專案數量: {len(project_groups)}')
        
        # 檢查我們匯入的特定指令
        print()
        print('🔍 特定指令檢查:')
        print('-' * 30)
        
        # 檢查 CTE 註解指令
        cte_instructions = [p for p in points if p['payload'].get('instruction_id') == 'cte_comment_global']
        if cte_instructions:
            print(f'✅ CTE 註解指令: 找到 {len(cte_instructions)} 個')
            cte_inst = cte_instructions[0]['payload'].get('instruction', '')
            if 'CTE' in cte_inst and '註解' in cte_inst:
                print('   ✅ 內容驗證: 包含 CTE 和註解關鍵字')
            else:
                print('   ⚠️  內容驗證: 可能缺少預期內容')
        else:
            print('❌ CTE 註解指令: 未找到')
        
        # 檢查其他指令
        expected_ids = ['teacher_student_relation', 'user_dimension_info', 'date_format_rules', 'sql_best_practices']
        for exp_id in expected_ids:
            found = any(p['payload'].get('instruction_id') == exp_id for p in points)
            status = '✅' if found else '❌'
            print(f'{status} {exp_id}: {"找到" if found else "未找到"}')
        
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_instructions() 