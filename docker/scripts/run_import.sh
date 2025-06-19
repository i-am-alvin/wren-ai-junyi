#!/bin/bash

# WrenAI Instructions Import Runner
# This script copies the necessary files to the Docker container and runs the import

set -e

# Configuration
CONTAINER_NAME="wrenai-wren-ai-service-1"
PROJECT_ID="20"
CSV_FILE="instructions.csv"
SCRIPT_FILE="import_instructions.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 WrenAI Instructions Import Runner${NC}"
echo -e "${BLUE}=====================================${NC}"

# Check if Docker container is running
echo -e "${YELLOW}📋 Checking Docker container status...${NC}"
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Container '$CONTAINER_NAME' is not running${NC}"
    echo -e "${YELLOW}💡 Please start WrenAI with: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Container is running${NC}"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

# Check if CSV file exists
CSV_PATH="$DOCKER_DIR/data/$CSV_FILE"
if [ ! -f "$CSV_PATH" ]; then
    echo -e "${RED}❌ CSV file not found: $CSV_PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✅ CSV file found: $CSV_PATH${NC}"

# Check if Python script exists
SCRIPT_PATH="$DOCKER_DIR/scripts/$SCRIPT_FILE"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Python script not found: $SCRIPT_PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python script found: $SCRIPT_PATH${NC}"

# Copy files to container
echo -e "${YELLOW}📁 Copying files to container...${NC}"
docker cp "$CSV_PATH" "$CONTAINER_NAME:/app/data/"
docker cp "$SCRIPT_PATH" "$CONTAINER_NAME:/app/scripts/"
echo -e "${GREEN}✅ Files copied successfully${NC}"

# Run the import
echo -e "${YELLOW}🏃 Running import process...${NC}"
echo -e "${BLUE}📊 Project ID: $PROJECT_ID${NC}"
echo -e "${BLUE}📁 CSV File: $CSV_FILE${NC}"
echo ""

# Execute the Python script inside the container
docker exec -it "$CONTAINER_NAME" python /app/scripts/"$SCRIPT_FILE" /app/data/"$CSV_FILE" --project_id "$PROJECT_ID"

# Check the result
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Import completed successfully!${NC}"
    echo -e "${YELLOW}💡 You can now verify the import using:${NC}"
    echo -e "${BLUE}   docker exec -it $CONTAINER_NAME python -c \"${NC}"
    echo -e "${BLUE}   import requests; import json${NC}"
    echo -e "${BLUE}   response = requests.post('http://qdrant:6333/collections/instructions/points/scroll', json={'limit': 10, 'with_payload': True})${NC}"
    echo -e "${BLUE}   result = response.json()${NC}"
    echo -e "${BLUE}   for point in result['result']['points']:${NC}"
    echo -e "${BLUE}       print(f'ID: {point[\"payload\"].get(\"instruction_id\", \"N/A\")} - Default: {point[\"payload\"].get(\"is_default\", False)}')${NC}"
    echo -e "${BLUE}   \"${NC}"
else
    echo ""
    echo -e "${RED}❌ Import failed. Check the logs above for details.${NC}"
    exit 1
fi 