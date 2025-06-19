#!/usr/bin/env python3
"""
Consolidate output directories into a single, clean structure.
Moves all generated books to output/generated_books/ and removes duplicates.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.utils.file_manager import get_file_manager

def main():
    """Consolidate all output directories."""
    logger = get_logger('consolidate_outputs')
    
    logger.info("🧹 Starting output directory consolidation...")
    
    # Initialize file manager
    file_manager = get_file_manager()
    
    # Show current structure
    logger.info("📁 Current structure:")
    project_root = file_manager.project_root
    
    # Check lambda/output
    lambda_output = project_root / "lambda" / "output"
    if lambda_output.exists():
        items = list(lambda_output.iterdir())
        logger.info(f"   lambda/output/: {len(items)} items")
        for item in items:
            if item.is_dir():
                sub_items = len(list(item.iterdir()))
                logger.info(f"     📂 {item.name}/: {sub_items} files")
            else:
                size_kb = item.stat().st_size / 1024
                logger.info(f"     📄 {item.name}: {size_kb:.1f} KB")
    
    # Check main output
    main_output = project_root / "output" / "generated_books"
    if main_output.exists():
        items = list(main_output.iterdir())
        logger.info(f"   output/generated_books/: {len(items)} items")
        for item in items:
            if item.is_dir():
                sub_items = len(list(item.iterdir()))
                logger.info(f"     📂 {item.name}/: {sub_items} files")
    
    # Perform consolidation
    moved_count = file_manager.cleanup_lambda_output()
    
    logger.info("\n📊 Final structure:")
    if main_output.exists():
        items = list(main_output.iterdir())
        logger.info(f"   output/generated_books/: {len(items)} items")
        
        total_books = 0
        total_size = 0
        
        for item in items:
            if item.is_dir():
                sub_items = list(item.iterdir())
                item_size = sum(f.stat().st_size for f in sub_items if f.is_file())
                size_mb = item_size / (1024 * 1024)
                
                if item.name == 'archive':
                    logger.info(f"     📦 {item.name}/: {len(sub_items)} archived files")
                else:
                    total_books += 1
                    total_size += item_size
                    logger.info(f"     📚 {item.name}/: {len(sub_items)} files ({size_mb:.2f} MB)")
        
        logger.info(f"\n✅ Consolidation complete:")
        logger.info(f"   📚 Total books: {total_books}")
        logger.info(f"   💾 Total size: {total_size / (1024 * 1024):.2f} MB")
        logger.info(f"   📁 Main output: {main_output}")
        
        if moved_count > 0:
            logger.info(f"   🔄 Items moved: {moved_count}")
        
        # Check if lambda/output still exists
        if lambda_output.exists():
            logger.warning(f"   ⚠️ lambda/output still exists with {len(list(lambda_output.iterdir()))} items")
        else:
            logger.info(f"   🗑️ lambda/output directory removed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)