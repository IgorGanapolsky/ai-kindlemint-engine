#!/usr/bin/env python3
"""
Generate Large Print Crossword Masters Volume 1 locally.
This will create the complete book package in lambda/output/
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def main():
    """Generate Large Print Crossword Masters Volume 1."""
    logger = get_logger('crossword_generation')
    
    logger.info("🎯 Starting Large Print Crossword Masters Volume 1 generation...")
    
    # Load environment variables from .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        logger.info(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables found")
    
    try:
        # Import the V3 orchestrator
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "intelligent_v3_orchestrator", 
            Path(__file__).parent.parent / "lambda" / "intelligent_v3_orchestrator.py"
        )
        orchestrator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orchestrator_module)
        
        IntelligentV3Orchestrator = orchestrator_module.IntelligentV3Orchestrator
        
        # Initialize orchestrator
        logger.info("🧠 Initializing Intelligent V3 Orchestrator...")
        orchestrator = IntelligentV3Orchestrator()
        
        # Create book specification for Volume 1
        book_spec = {
            'series': 'Large Print Crossword Masters',
            'volume': 1,
            'brand': 'Senior Puzzle Studio', 
            'niche': 'large_print_crosswords_seniors',
            'difficulty': 'beginner',
            'source': 'local_generation',
            'series_info': {
                'series_name': 'Large Print Crossword Masters',
                'series_brand': 'Senior Puzzle Studio',
                'micro_niche': 'Large print crossword puzzles for seniors',
                'target_audience': 'seniors_55_plus',
                'volume_details': {
                    'volume_number': 1,
                    'title': 'Large Print Crossword Masters: Volume 1 - Beginner',
                    'subtitle': 'Easy Large Print Crosswords for Seniors',
                    'difficulty': 'beginner',
                    'page_count': 100,
                    'puzzle_count': 50
                }
            }
        }
        
        logger.info(f"📚 Generating: {book_spec['series']} Volume {book_spec['volume']}")
        logger.info(f"   Brand: {book_spec['brand']}")
        logger.info(f"   Difficulty: {book_spec['difficulty']}")
        logger.info(f"   Target: {book_spec['niche']}")
        
        # Generate the complete book
        result = asyncio.run(orchestrator.execute_intelligent_pipeline())
        
        logger.info("🎉 BOOK GENERATION COMPLETED!")
        logger.info(f"📊 Result: {result.get('status', 'unknown')}")
        
        # Check output directory
        output_dir = Path(__file__).parent.parent / "lambda" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Checking output directory: {output_dir}")
        generated_files = list(output_dir.glob("*"))
        
        if generated_files:
            logger.info(f"✅ Found {len(generated_files)} generated files:")
            for file_path in generated_files:
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    logger.info(f"   {file_path.name}: {size_mb:.2f} MB")
                elif file_path.is_dir():
                    item_count = len(list(file_path.iterdir()))
                    logger.info(f"   {file_path.name}/: {item_count} items")
        else:
            logger.warning("⚠️ No files found in output directory")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Book generation failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)