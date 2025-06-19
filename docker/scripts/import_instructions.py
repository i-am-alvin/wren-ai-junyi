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

WrenAI Instructions CSV Importer (Docker Version)

This script runs inside the WrenAI Docker environment and imports instructions from CSV to Qdrant.
It leverages the existing WrenAI infrastructure for embedding generation.

Usage (inside Docker container):
    python import_instructions.py <csv_file> --project_id <id>

Example:
    docker exec -it wrenai-wren-ai-service-1 python /app/scripts/import_instructions.py /app/data/instructions.csv --project_id 20
"""

import argparse
import asyncio
import csv
import logging
import uuid
import sys
import os
from typing import List, Dict, Any, Optional

# ⚠️ DEPRECATED WARNING ⚠️
print("=" * 80)
print("⚠️  WARNING: THIS SCRIPT IS DEPRECATED AND SHOULD NOT BE USED!")
print("⚠️  Use 'import_instructions_via_ui.py' instead for proper UI API import.")
print("⚠️  Direct Qdrant writes will NOT appear in the UI interface!")
print("=" * 80)
input("Press Enter to continue anyway, or Ctrl+C to cancel...")

# Add WrenAI service to path
sys.path.insert(0, '/')

try:
    from src.config import settings
    from src.providers import generate_components
    from src.globals import create_service_container
    from src.pipelines.indexing.instructions import Instruction
    from src.web.v1.services.instructions import InstructionsService
    
    # Change working directory to /src after imports for relative file paths
    os.chdir('/src')
except ImportError as e:
    print(f"Error importing WrenAI modules: {e}")
    print("Make sure this script is running inside the WrenAI Docker container")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WrenAIInstructionsImporter:
    def __init__(self):
        """Initialize using WrenAI's existing infrastructure"""
        try:
            self.pipe_components = generate_components(settings.components)
            self.service_container = create_service_container(self.pipe_components, settings)
            self.instructions_service = self.service_container.instructions_service
            logger.info("✅ WrenAI service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize WrenAI service: {e}")
            raise
        
    async def import_from_csv(self, csv_file: str, project_id: str) -> Dict[str, int]:
        """Import instructions from CSV file using WrenAI service"""
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
                        
                        # Parse questions
                        questions = []
                        if questions_str:
                            questions = [q.strip() for q in questions_str.split(";") if q.strip()]
                        
                        # Create instruction object
                        instruction = InstructionsService.Instruction(
                            id=instruction_id,
                            instruction=instruction_text,
                            questions=questions,
                            is_default=is_default
                        )
                        
                        instructions_to_import.append(instruction)
                        
                        status = "🌐 global/default" if is_default else f"❓ {len(questions)} questions"
                        logger.info(f"✅ Row {row_num}: {instruction_id} ({status})")
                        
                    except Exception as e:
                        logger.error(f"❌ Row {row_num}: Failed to parse - {e}")
                        logger.error(f"   Row data: {row}")
                        stats["failed"] += 1
                        continue
            
            # Import all instructions at once
            if instructions_to_import:
                logger.info(f"\n🚀 Importing {len(instructions_to_import)} instructions to project {project_id}...")
                
                # Create request
                request = InstructionsService.IndexRequest(
                    event_id=str(uuid.uuid4()),
                    instructions=instructions_to_import,
                    project_id=project_id
                )
                
                # Execute import
                logger.info("⏳ Processing instructions...")
                result = await self.instructions_service.index(request)
                
                # Handle result based on its structure
                if isinstance(result, dict) and 'resource' in result:
                    # Extract the resource (Event object)
                    resource = result['resource']
                    if hasattr(resource, 'status') and resource.status == 'finished':
                        stats["success"] = len(instructions_to_import)
                        logger.info(f"🎉 Successfully imported all {stats['success']} instructions!")
                        logger.info(f"   Event ID: {resource.event_id}")
                        logger.info(f"   Trace ID: {resource.trace_id}")
                    else:
                        stats["failed"] = len(instructions_to_import)
                        error_msg = resource.error.message if hasattr(resource, 'error') and resource.error else "Unknown error"
                        logger.error(f"💥 Import failed: {error_msg}")
                        if hasattr(resource, 'trace_id') and resource.trace_id:
                            logger.error(f"   Trace ID: {resource.trace_id}")
                elif isinstance(result, dict):
                    # If result is a dict, check for success indicators
                    if result.get("status") == "finished" or "success" in str(result).lower():
                        stats["success"] = len(instructions_to_import)
                        logger.info(f"🎉 Successfully imported all {stats['success']} instructions!")
                    else:
                        stats["failed"] = len(instructions_to_import)
                        error_msg = result.get("error", {}).get("message", "Unknown error") if result.get("error") else str(result)
                        logger.error(f"💥 Import failed: {error_msg}")
                        if result.get("trace_id"):
                            logger.error(f"   Trace ID: {result.get('trace_id')}")
                else:
                    # If result is an object, use attribute access
                    if hasattr(result, 'status') and result.status == "finished":
                        stats["success"] = len(instructions_to_import)
                        logger.info(f"🎉 Successfully imported all {stats['success']} instructions!")
                    else:
                        stats["failed"] = len(instructions_to_import)
                        error_msg = result.error.message if hasattr(result, 'error') and result.error else "Unknown error"
                        logger.error(f"💥 Import failed: {error_msg}")
                        if hasattr(result, 'trace_id') and result.trace_id:
                            logger.error(f"   Trace ID: {result.trace_id}")
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
        description="Import instructions from CSV to WrenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import with specific project ID
  python import_instructions.py /app/data/instructions.csv --project_id 20
  
  # Import with debug logging
  python import_instructions.py /app/data/instructions.csv --project_id 20 --debug
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
    
    logger.info(f"🚀 Starting WrenAI Instructions Importer")
    logger.info(f"📁 CSV File: {args.csv_file}")
    logger.info(f"🎯 Project ID: {args.project_id}")
    
    try:
        importer = WrenAIInstructionsImporter()
        stats = await importer.import_from_csv(args.csv_file, args.project_id)
        
        if stats["failed"] > 0:
            logger.error(f"⚠️  Import completed with {stats['failed']} failures")
            sys.exit(1)
        else:
            logger.info(f"🎉 Import completed successfully!")
            
    except Exception as e:
        logger.error(f"💥 Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 