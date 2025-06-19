# WrenAI Storage Documentation

## Overview
WrenAI uses multiple storage systems to manage different types of data:
- **Qdrant**: Vector database for storing question-SQL pairs, instructions, and embeddings
- **SQLite**: Local database for UI metadata and configurations
- **Docker Volumes**: Persistent storage for container data

## Qdrant Vector Database

### Purpose
Qdrant stores vectorized question-SQL pairs and instructions that enable semantic search and retrieval for the AI assistant. This allows WrenAI to:
1. Find similar questions and their corresponding SQL queries to help generate accurate responses
2. Retrieve relevant instructions that provide context and rules for SQL generation based on database schema and business logic

### Collections Structure
Qdrant contains 6 main collections:
1. **sql_pairs** - Question-SQL pair mappings (primary collection for Q&A)
2. **table_descriptions** - Database schema descriptions
3. **view_questions** - View-related questions
4. **project_meta** - Project metadata
5. **Document** - General documents
6. **instructions** - System instructions

### SQL Pairs Collection Schema
Each document in `sql_pairs` contains:
- `id`: Unique identifier for the question-SQL pair
- `content`: The question text (in Traditional Chinese)
- `sql`: Corresponding SQL query
- `sql_pair_id`: Sequential ID for the pair
- `project_id`: Project identifier
- `dataframe`: Optional dataframe data
- `blob`: Optional binary data
- `score`: Optional relevance score
- `sparse_embedding`: Optional sparse vector representation

### Instructions Collection Schema
Each document in `instructions` contains:
- `instruction_id`: Unique identifier for the instruction
- `instruction`: The instruction content (provides context and rules for SQL generation)
- `content`: Question content (empty for default instructions)
- `is_default`: Boolean indicating if this is a default instruction
- `project_id`: Project identifier

### Vector Configuration
- **Vector Size**: 3072 dimensions
- **Distance Metric**: Cosine similarity
- **Storage**: On-disk storage enabled for efficiency

## Query Methods

### 1. Check Container Status
```bash
# Verify Qdrant container is running
docker ps | grep qdrant
```

### 2. List All Collections
```bash
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
print(requests.get('http://qdrant:6333/collections').json())
"
```

### 3. Get Collection Information
```bash
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
print(requests.get('http://qdrant:6333/collections/sql_pairs').json())
"
```

### 4. Search Question-SQL Pairs
```bash
# Vector search (requires actual embedding vector)
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
import json
response = requests.post('http://qdrant:6333/collections/sql_pairs/points/search', 
                        json={'vector': [0]*3072, 'limit': 3, 'with_payload': True})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
"
```

### 5. Browse All Stored Pairs
```bash
# Scroll through all question-SQL pairs
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
import json
response = requests.post('http://qdrant:6333/collections/sql_pairs/points/scroll', 
                        json={'limit': 10, 'with_payload': True})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
"
```

### 6. Browse All Instructions
```bash
# Scroll through all instructions
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
import json
response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', 
                        json={'limit': 10, 'with_payload': True})
result = response.json()
for point in result['result']['points']:
    print(f'Instruction ID: {point[\"payload\"].get(\"instruction_id\", \"N/A\")}')
    print(f'Project ID: {point[\"payload\"].get(\"project_id\", \"N/A\")}')
    print(f'Is Default: {point[\"payload\"].get(\"is_default\", False)}')
    print(f'Instruction: {point[\"payload\"].get(\"instruction\", \"N/A\")}')
    print('---')
"
```

### 7. Query Instructions by Project
```bash
# Filter instructions by project_id
docker exec -it wrenai-wren-ai-service-1 python -c "
import requests
import json
project_id = '20'  # Replace with actual project_id
response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', 
                        json={
                            'filter': {
                                'must': [
                                    {'key': 'project_id', 'match': {'value': project_id}}
                                ]
                            },
                            'limit': 100, 
                            'with_payload': True
                        })
result = response.json()
for point in result['result']['points']:
    print(f'Instruction: {point[\"payload\"].get(\"instruction\", \"N/A\")}')
    print('---')
"
```

### 8. Check Storage Files
```bash
# Check Qdrant storage directory
docker exec -it wrenai-qdrant-1 ls -la /qdrant/storage/collections/sql_pairs
docker exec -it wrenai-qdrant-1 ls -la /qdrant/storage/collections/instructions
```

## Example Question-SQL Pairs
Based on recent data, the system stores pairs like:
1. "請告訴我目前 dim_user_data 表中有多少筆總紀錄？"
2. "每天註冊的用戶數量是多少？"
3. "每所學校的學生總數、用戶數及用戶佔學生比例是多少？"
4. "知識點的使用情況在過去一年中有何變化？"
5. "在不同的學期類型和縣市中，有多少位 LV1 老師？"

## Example Instructions
Based on recent data, the system stores instructions like:
1. **師生關係 (Teacher-Student Relationship)**: "dim_teacher_student_joins 記錄了老師、學生和班級之間的關係，包含 class_id, teacher_user_id, student_user_id, class_name。建議規則: 當查詢需要連接老師和其對應的學生，或查詢某班級的師生名單時，應使用 dim_teacher_student_joins。"
2. **使用者維度 (User Dimension)**: "dim_user_data 是核心的使用者資訊表，包含了 user_id, user_email, backend_user_id, user_role..."
3. **學校維度 (School Dimension)**: "dim_schools_metadata 包含了學校的詳細資訊，如 school_id_sha256, school_name, school_city..."
4. **內容維度 (Content Dimension)**: "fct_user_records_of_all_contents 及其衍生表格記錄了使用者與不同類型內容..."
5. **時間與學期相關 (Time & Semester Related)**: "calendar_date: 日曆日期。session_year_type_tw: 台灣學年學期制表示..."

## Data Flow

### SQL Pairs Flow
1. User submits question-SQL pair through UI
2. WrenAI service converts question to embedding vector
3. Vector and metadata stored in Qdrant `sql_pairs` collection
4. During query, user questions are vectorized and matched against stored pairs
5. Most similar pairs are retrieved to help generate SQL responses

### Instructions Flow
1. Instructions are indexed through WrenAI service API
2. Each instruction is converted to embedding vector along with associated questions
3. Instructions stored in Qdrant `instructions` collection with metadata
4. During SQL generation, relevant instructions are retrieved based on semantic similarity
5. Retrieved instructions provide context and rules to guide SQL generation

## Persistence
- Qdrant data persists in Docker volume `wrenai_data`
- Volume mounted at `/qdrant/storage` in container
- Collections maintain state across container restarts

## Network Configuration
- Qdrant runs on internal Docker network `wrenai_wren`
- Accessible to other services via hostname `qdrant:6333`
- Not exposed to host machine by default for security

## Monitoring
Monitor real-time operations by watching container logs:
```bash
docker logs -f wrenai-qdrant-1
docker logs -f wrenai-wren-ai-service-1
```

## Related Documentation

- [Instructions Import Guide](import.md) - 完整的 instructions 匯入指南
- [Import Scripts](../scripts/) - 匯入腳本和工具
