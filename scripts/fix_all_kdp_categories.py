#!/usr/bin/env python3
"""
Fix all KDP categories across all metadata files to use actual subcategories from KDP interface.
Based on actual KDP screenshots showing real category structure.
"""

import json
import os
import glob
from pathlib import Path

# Verified categories from actual KDP interface screenshots
CORRECT_CATEGORIES = {
    "puzzle_books": [
        "Crafts, Hobbies & Home > Crafts & Hobbies",
        "Self-Help > Memory Improvement", 
        "Health, Fitness & Dieting > Aging"
    ]
}

def fix_metadata_file(file_path):
    """Fix categories and book type classifications in a single metadata file"""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # Fix categories
        if 'categories' not in data:
            print(f"  - Adding missing categories")
            data['categories'] = CORRECT_CATEGORIES["puzzle_books"]
            modified = True
        else:
            # Check current categories
            current = data['categories']
            print(f"  - Current categories: {current}")
            
            # Fix incomplete categories (missing subcategories) or wrong subcategories
            if (len(current) != 3 or 
                any('>' not in cat for cat in current) or
                any('Games, Puzzles' in cat for cat in current) or  # Hallucinated category
                any('Activity Books' in cat for cat in current)):   # Wrong subcategory
                
                print(f"  - Fixing categories")
                data['categories'] = CORRECT_CATEGORIES["puzzle_books"]
                modified = True
        
        # Add KDP book type classifications
        if 'kdp_book_types' not in data:
            print(f"  - Adding KDP book type classifications")
            data['kdp_book_types'] = {
                "low_content_book": True,  # Puzzle books qualify as low-content
                "large_print_book": "Large Print" in data.get("title", "")  # True for Large Print series
            }
            modified = True
        else:
            # Check existing classifications
            current_types = data['kdp_book_types']
            expected_large_print = "Large Print" in data.get("title", "")
            
            if (current_types.get("low_content_book") != True or 
                current_types.get("large_print_book") != expected_large_print):
                print(f"  - Updating KDP book type classifications")
                data['kdp_book_types'] = {
                    "low_content_book": True,
                    "large_print_book": expected_large_print
                }
                modified = True
        
        if modified:
            # Write back the corrected file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Fixed")
        else:
            print(f"  ✓ Already correct")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    """Fix all metadata files"""
    base_dir = "/Users/igorganapolsky/workspace/git/ai/ai-kindlemint-engine"
    
    # Find all metadata files
    patterns = [
        "**/books/active_production/**/*metadata*.json",
        "**/books/active_production/**/amazon_kdp_metadata.json",
        "**/books/active_production/**/kindle_metadata.json",
        "**/books/active_production/**/paperback_metadata.json"
    ]
    
    all_files = set()
    for pattern in patterns:
        files = glob.glob(os.path.join(base_dir, pattern), recursive=True)
        all_files.update(files)
    
    print(f"Found {len(all_files)} metadata files to check")
    print()
    
    for file_path in sorted(all_files):
        fix_metadata_file(file_path)
    
    print()
    print("✓ All metadata files processed with correct KDP categories and book type classifications")
    print()
    print("Categories used (verified from KDP interface):")
    for i, cat in enumerate(CORRECT_CATEGORIES["puzzle_books"], 1):
        print(f"  {i}. {cat}")
    print()
    print("Book type classifications added:")
    print("  • Low-content book: true (all puzzle books)")
    print("  • Large-print book: true (for 'Large Print' series only)")

if __name__ == "__main__":
    main()