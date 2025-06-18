#!/usr/bin/env python3
"""
Add an existing cover image to a book directory.
Useful when you have a manually created cover.
"""
import sys
import shutil
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def main():
    """Add cover to the latest book directory."""
    logger = get_logger('add_cover')
    
    if len(sys.argv) != 2:
        logger.error("Usage: python add_cover_to_book.py <cover_image_path>")
        logger.info("Example: python add_cover_to_book.py ~/Downloads/cover.png")
        return False
    
    cover_path = Path(sys.argv[1])
    
    if not cover_path.exists():
        logger.error(f"❌ Cover file not found: {cover_path}")
        return False
    
    # Find the latest book directory
    output_dir = Path(__file__).parent.parent / "output" / "generated_books"
    book_dirs = [d for d in output_dir.iterdir() 
                if d.is_dir() and d.name != 'archive']
    
    if not book_dirs:
        logger.error("❌ No book directories found")
        return False
    
    # Get the most recent book
    latest_book = max(book_dirs, key=lambda d: d.stat().st_mtime)
    
    # Copy cover to book directory
    target_cover = latest_book / f"cover{cover_path.suffix}"
    shutil.copy2(cover_path, target_cover)
    
    size_kb = target_cover.stat().st_size / 1024
    logger.info(f"✅ Cover added to: {latest_book.name}")
    logger.info(f"   📂 Location: {target_cover}")
    logger.info(f"   💾 Size: {size_kb:.1f} KB")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)