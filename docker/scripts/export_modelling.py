#!/usr/bin/env python3
"""
Export Modelling (MDL) from WrenAI

This script exports the complete modelling definition from WrenAI system:
- Models, columns, relationships, views
- Export to JSON file in docker/data/
"""

import requests
import json
import os
from datetime import datetime

# Configuration
UI_GRAPHQL_ENDPOINT = "http://wrenai-wren-ui-1:3000/api/graphql"  # Use container hostname
OUTPUT_DIR = "/app/data"  # Inside container path

def get_latest_deploy_hash():
    """Get the latest deployment hash from deploy logs"""
    
    query = """
    query {
        __typename
    }
    """
    
    # For now, we'll use a known hash or get it from deploy_log table
    # This would need to be implemented to query the database directly
    # or add a GraphQL query for deploy logs
    
    # Return the hash we used in our test
    return "852c9584f33bf6df0006a983b332dfa524282eeb"

def query_mdl(hash_value):
    """Query MDL via GraphQL API using deployment hash"""
    
    query = f"""
    query GetMDL {{
        getMDL(hash: "{hash_value}") {{
            hash
            mdl
        }}
    }}
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
                return result['data']['getMDL']
        else:
            print(f"❌ HTTP Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None

def decode_mdl(encoded_mdl):
    """Decode base64 encoded MDL to JSON"""
    import base64
    
    try:
        decoded_bytes = base64.b64decode(encoded_mdl)
        decoded_str = decoded_bytes.decode('utf-8')
        return json.loads(decoded_str)
    except Exception as e:
        print(f"❌ Error decoding MDL: {e}")
        return None

def export_mdl_to_json(mdl_data, output_path):
    """Export MDL to JSON file"""
    
    if not mdl_data:
        print("⚠️  No MDL data to export")
        return False
    
    try:
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(mdl_data, jsonfile, indent=2, ensure_ascii=False)
        
        # Print summary
        models_count = len(mdl_data.get('models', []))
        relationships_count = len(mdl_data.get('relationships', []))
        views_count = len(mdl_data.get('views', []))
        
        print(f"✅ Successfully exported MDL to {output_path}")
        print(f"   📊 Models: {models_count}")
        print(f"   🔗 Relationships: {relationships_count}")
        print(f"   👁️  Views: {views_count}")
        print(f"   🗄️  DataSource: {mdl_data.get('dataSource', 'Unknown')}")
        print(f"   🏷️  Catalog: {mdl_data.get('catalog', 'Unknown')}")
        print(f"   📋 Schema: {mdl_data.get('schema', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting MDL: {e}")
        return False

def main():
    print('=' * 80)
    print('📤 WrenAI Modelling (MDL) Export Tool')
    print('=' * 80)
    print(f'⏰ Export time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get latest deployment hash
    print("🔍 Getting latest deployment hash...")
    hash_value = get_latest_deploy_hash()
    print(f"   Hash: {hash_value}")
    print()
    
    # Export MDL
    print("📋 Exporting MDL...")
    mdl_result = query_mdl(hash_value)
    
    if mdl_result is not None:
        # Decode the base64 encoded MDL
        print("🔓 Decoding MDL...")
        mdl_data = decode_mdl(mdl_result['mdl'])
        
        if mdl_data:
            # Export to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mdl_file = os.path.join(OUTPUT_DIR, f'modelling_export_{timestamp}.json')
            
            if export_mdl_to_json(mdl_data, mdl_file):
                print()
                print("✅ MDL export completed successfully!")
                print(f"📁 File saved: {mdl_file}")
            else:
                print("❌ Failed to export MDL")
                exit(1)
        else:
            print("❌ Failed to decode MDL")
            exit(1)
    else:
        print("❌ Failed to query MDL")
        exit(1)
    
    print()
    print("🎉 Export process completed!")

if __name__ == "__main__":
    main() 