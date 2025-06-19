#!/usr/bin/env python3
"""
⚠️ DEPRECATED - DO NOT USE ⚠️

This script is DEPRECATED and should NOT be used.
It directly writes to Qdrant which causes data inconsistency.

PROBLEM:
- Data written directly to Qdrant will NOT appear in the UI
- UI and Qdrant will be out of sync
- Cannot manage instructions through the web interface

CORRECT METHOD:
Use import_instructions_via_ui.py instead, which:
- Uses the proper UI GraphQL API
- Automatically syncs UI database and Qdrant
- Allows management through web interface

Simple Instructions Importer for WrenAI

This script provides a simplified way to import instructions directly to Qdrant.
It bypasses the full WrenAI service stack for faster testing and development.

WARNING: This approach writes directly to Qdrant and may not sync with UI database.
For production use, consider using the full WrenAI service API.
"""

import argparse
import asyncio
import csv
import logging
import uuid
import sys
import os
from typing import List, Dict, Any, Optional
import requests

# Add WrenAI service to path
sys.path.insert(0, '/')

try:
    from src.pipelines.indexing.instructions import Instruction, Instructions
    from src.providers.document_store.qdrant import QdrantProvider
    from src.providers.embedder.litellm import LitellmEmbedderProvider
    
    # Change working directory to /src for relative file paths
    os.chdir('/src')
except ImportError as e:
    print(f"Error importing WrenAI modules: {e}")
    print("Make sure this script is running inside the WrenAI Docker container")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ⚠️ DEPRECATED WARNING ⚠️
print("=" * 80)
print("⚠️  WARNING: THIS SCRIPT IS DEPRECATED AND SHOULD NOT BE USED!")
print("⚠️  Use 'import_instructions_via_ui.py' instead for proper UI API import.")
print("⚠️  Direct Qdrant writes will NOT appear in the UI interface!")
print("=" * 80)
input("Press Enter to continue anyway, or Ctrl+C to cancel...")

class SimpleInstructionsImporter:
    def __init__(self):
        """Initialize with minimal WrenAI infrastructure"""
        try:
            # Initialize providers directly
            logger.info("🔧 Initializing Qdrant provider...")
            self.document_store_provider = QdrantProvider(
                location="qdrant",  # Docker service name
                embedding_model_dim=3072,
                recreate_index=False
            )
            
            logger.info("🔧 Initializing embedder provider...")
            self.embedder_provider = LitellmEmbedderProvider(
                api_base="https://api.openai.com/v1",
                model="text-embedding-3-large"
            )
            
            # Initialize instructions pipeline
            logger.info("🔧 Initializing instructions pipeline...")
            self.instructions_pipeline = Instructions(
                embedder_provider=self.embedder_provider,
                document_store_provider=self.document_store_provider
            )
            
            logger.info("✅ Simple importer initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize simple importer: {e}")
            raise
        
    async def import_from_csv(self, csv_file: str, project_id: str) -> Dict[str, int]:
        """Import instructions from CSV file"""
        stats = {"success": 0, "failed": 0, "total": 0}
        instructions_to_import = []
        
        try:
            logger.info(f"📖 Reading CSV file: {csv_file}")
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate required columns
                required_columns = ["instruction_id", "instruction", "is_default"]
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {missing_columns}")
                
                logger.info(f"📋 CSV columns: {reader.fieldnames}")
                
                for row_num, row in enumerate(reader, 1):
                    stats["total"] += 1
                    
                    try:
                        instruction_id = row["instruction_id"].strip()
                        instruction_text = row["instruction"].strip()
                        questions_str = row.get("questions", "").strip()
                        is_default = row["is_default"].strip().lower() == "true"
                        
                        if not instruction_id or not instruction_text:
                            raise ValueError(f"instruction_id and instruction cannot be empty")
                        
                        if is_default:
                            # Single instruction for default
                            instruction = Instruction(
                                id=instruction_id,
                                instruction=instruction_text,
                                question="",  # Empty for default
                                is_default=True
                            )
                            instructions_to_import.append(instruction)
                            logger.info(f"✅ Row {row_num}: {instruction_id} (🌐 global/default)")
                        else:
                            # Parse questions and create multiple instructions
                            questions = []
                            if questions_str:
                                questions = [q.strip() for q in questions_str.split(";") if q.strip()]
                            
                            if not questions:
                                logger.warning(f"⚠️  Row {row_num}: Non-default instruction without questions: {instruction_id}")
                                continue
                            
                            for question in questions:
                                instruction = Instruction(
                                    id=instruction_id,
                                    instruction=instruction_text,
                                    question=question,
                                    is_default=False
                                )
                                instructions_to_import.append(instruction)
                            
                            logger.info(f"✅ Row {row_num}: {instruction_id} (❓ {len(questions)} questions)")
                        
                    except Exception as e:
                        logger.error(f"❌ Row {row_num}: Failed to parse - {e}")
                        logger.error(f"   Row data: {row}")
                        stats["failed"] += 1
                        continue
            
            # Import all instructions at once
            if instructions_to_import:
                logger.info(f"\n🚀 Importing {len(instructions_to_import)} instructions to project {project_id}...")
                
                # Execute import using the pipeline
                logger.info("⏳ Processing instructions...")
                await self.instructions_pipeline.run(
                    project_id=project_id,
                    instructions=instructions_to_import
                )
                
                stats["success"] = len(instructions_to_import)
                logger.info(f"🎉 Successfully imported all {stats['success']} instructions!")
            else:
                logger.warning("⚠️  No valid instructions to import")
            
            # Print summary
            logger.info(f"\n{'='*50}")
            logger.info(f"📊 IMPORT SUMMARY")
            logger.info(f"{'='*50}")
            logger.info(f"📁 File: {csv_file}")
            logger.info(f"🎯 Project ID: {project_id}")
            logger.info(f"📈 Total rows processed: {stats['total']}")
            logger.info(f"✅ Successfully imported: {stats['success']}")
            logger.info(f"❌ Failed: {stats['failed']}")
            logger.info(f"{'='*50}")
            
        except Exception as e:
            logger.error(f"💥 Failed to import from CSV: {e}")
            raise
        
        return stats

async def main():
    parser = argparse.ArgumentParser(
        description="Simple import instructions from CSV to WrenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import with specific project ID
  python simple_import.py /app/data/instructions.csv --project_id 20
        """
    )
    parser.add_argument("csv_file", help="Path to CSV file containing instructions")
    parser.add_argument("--project_id", required=True, help="Project ID for the instructions")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate CSV file
    if not os.path.exists(args.csv_file):
        logger.error(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    logger.info(f"🚀 Starting Simple WrenAI Instructions Importer")
    logger.info(f"📁 CSV File: {args.csv_file}")
    logger.info(f"🎯 Project ID: {args.project_id}")
    
    try:
        importer = SimpleInstructionsImporter()
        stats = await importer.import_from_csv(args.csv_file, args.project_id)
        
        if stats["failed"] > 0:
            logger.error(f"⚠️  Import completed with {stats['failed']} failures")
            sys.exit(1)
        else:
            logger.info(f"🎉 Import completed successfully!")
            
    except Exception as e:
        logger.error(f"💥 Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 