#!/bin/bash

# WrenAI Data Export Script
# This script exports instructions and SQL pairs from WrenAI system

set -e

echo "================================================================================"
echo "📤 WrenAI Data Export Tool"
echo "================================================================================"
echo "⏰ Export time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Configuration
CONTAINER_NAME="wrenai-wren-ai-service-1"
SCRIPT_NAME="export_data.py"
LOCAL_DATA_DIR="docker/data"

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: Container $CONTAINER_NAME is not running"
    echo "Please start WrenAI services first"
    exit 1
fi

echo "✅ Container $CONTAINER_NAME is running"

# Copy export script to container
echo "📋 Copying export script to container..."
docker cp "$LOCAL_DATA_DIR/../scripts/$SCRIPT_NAME" "$CONTAINER_NAME:/app/$SCRIPT_NAME"

# Execute export script in container
echo "🔄 Executing export script in container..."
docker exec -it "$CONTAINER_NAME" /app/.venv/bin/python3 "/app/$SCRIPT_NAME"

# Copy exported files back to local
echo "📥 Copying exported files to local..."
docker cp "$CONTAINER_NAME:/app/data/instructions.csv" "$LOCAL_DATA_DIR/instructions.csv"
docker cp "$CONTAINER_NAME:/app/data/sql_pairs.csv" "$LOCAL_DATA_DIR/sql_pairs.csv"

# Show results
echo ""
echo "================================================================================"
echo "✅ Export completed successfully!"
echo "📁 Files saved to: $LOCAL_DATA_DIR/"
echo "   - instructions.csv ($(wc -l < "$LOCAL_DATA_DIR/instructions.csv") lines)"
echo "   - sql_pairs.csv ($(wc -l < "$LOCAL_DATA_DIR/sql_pairs.csv") lines)"
echo "================================================================================"
echo ""
echo "📊 Summary:"
echo "   Instructions: $(($(wc -l < "$LOCAL_DATA_DIR/instructions.csv") - 1)) records"
echo "   SQL Pairs: $(($(wc -l < "$LOCAL_DATA_DIR/sql_pairs.csv") - 1)) records"
echo ""
echo "🎯 You can now use these files for:"
echo "   - Backup and version control"
echo "   - Import to other WrenAI instances"
echo "   - Analysis and review"
echo "" 