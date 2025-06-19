#!/usr/bin/env python3
"""
Export Instructions and SQL Pairs from WrenAI

This script exports all instructions and SQL pairs from WrenAI system:
- Instructions from UI backend (GraphQL API)
- SQL pairs from UI backend (GraphQL API)
- Export to CSV files in docker/data/
"""

import requests
import json
import csv
import os
from datetime import datetime

# Configuration
UI_GRAPHQL_ENDPOINT = "http://wrenai-wren-ui-1:3000/api/graphql"  # Use container hostname
OUTPUT_DIR = "/app/docker/data"  # Inside container path
LOCAL_OUTPUT_DIR = "docker/data"  # Local path

def query_instructions():
    """Query all instructions via GraphQL API"""
    
    query = """
    query Instructions {
        instructions {
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
    
    payload = {"query": query}
    
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
                return result['data']['instructions']
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def query_sql_pairs():
    """Query all SQL pairs via GraphQL API"""
    
    query = """
    query SqlPairs {
        sqlPairs {
            id
            projectId
            sql
            question
            createdAt
            updatedAt
        }
    }
    """
    
    payload = {"query": query}
    
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
                return result['data']['sqlPairs']
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def export_instructions_to_csv(instructions, output_path):
    """Export instructions to CSV file"""
    
    if not instructions:
        print("⚠️  No instructions to export")
        return False
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['instruction_id', 'instruction', 'questions', 'is_default', 'project_id', 'created_at', 'updated_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for idx, instruction in enumerate(instructions):
                # Convert questions array to semicolon-separated string
                questions_str = ';'.join(instruction.get('questions', []))
                
                writer.writerow({
                    'instruction_id': f'exported_instruction_{instruction["id"]}',
                    'instruction': instruction.get('instruction', ''),
                    'questions': questions_str,
                    'is_default': str(instruction.get('isDefault', False)).lower(),
                    'project_id': instruction.get('projectId', ''),
                    'created_at': instruction.get('createdAt', ''),
                    'updated_at': instruction.get('updatedAt', '')
                })
        
        print(f"✅ Successfully exported {len(instructions)} instructions to {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting instructions: {e}")
        return False

def export_sql_pairs_to_csv(sql_pairs, output_path):
    """Export SQL pairs to CSV file"""
    
    if not sql_pairs:
        print("⚠️  No SQL pairs to export, creating empty file")
        # Create empty file with headers
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['question', 'sql', 'project_id', 'created_at', 'updated_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            print(f"✅ Created empty SQL pairs file: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating empty SQL pairs file: {e}")
            return False
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['question', 'sql', 'project_id', 'created_at', 'updated_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for pair in sql_pairs:
                writer.writerow({
                    'question': pair.get('question', ''),
                    'sql': pair.get('sql', ''),
                    'project_id': pair.get('projectId', ''),
                    'created_at': pair.get('createdAt', ''),
                    'updated_at': pair.get('updatedAt', '')
                })
        
        print(f"✅ Successfully exported {len(sql_pairs)} SQL pairs to {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting SQL pairs: {e}")
        return False

def main():
    print('=' * 80)
    print('📤 WrenAI Data Export Tool')
    print('=' * 80)
    print(f'⏰ Export time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Determine output directory - always use /app/data in container
    output_dir = "/app/data"
    print(f"📁 Using container path: {output_dir}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Export Instructions
    print("📋 Exporting Instructions...")
    instructions = query_instructions()
    
    if instructions is not None:
        instructions_file = os.path.join(output_dir, 'instructions.csv')
        export_instructions_to_csv(instructions, instructions_file)
    else:
        print("❌ Failed to query instructions")
    
    print()
    
    # Export SQL Pairs
    print("🔗 Exporting SQL Pairs...")
    sql_pairs = query_sql_pairs()
    
    if sql_pairs is not None:
        sql_pairs_file = os.path.join(output_dir, 'sql_pairs.csv')
        export_sql_pairs_to_csv(sql_pairs, sql_pairs_file)
    else:
        print("❌ Failed to query SQL pairs")
    
    print()
    print('=' * 80)
    print('✅ Export completed!')
    print(f'📁 Files saved to: {output_dir}')
    print('   - instructions.csv')
    print('   - sql_pairs.csv')
    print('=' * 80)

if __name__ == "__main__":
    main() 