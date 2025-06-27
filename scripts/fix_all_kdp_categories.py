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
    """Fix categories in a single metadata file"""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Skip if no categories field
        if 'categories' not in data:
            print(f"  - Adding missing categories")
            data['categories'] = CORRECT_CATEGORIES["puzzle_books"]
            modified = True
        else:
            # Check current categories
            current = data['categories']
            print(f"  - Current categories: {current}")
            
            # Fix incomplete categories (missing subcategories) or wrong subcategories
            modified = False
            if (len(current) != 3 or 
                any('>' not in cat for cat in current) or
                any('Games, Puzzles' in cat for cat in current) or  # Hallucinated category
                any('Activity Books' in cat for cat in current)):   # Wrong subcategory
                
                print(f"  - Fixing categories")
                data['categories'] = CORRECT_CATEGORIES["puzzle_books"]
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
    print("✓ All metadata files processed with correct KDP categories")
    print()
    print("Categories used (verified from KDP interface):")
    for i, cat in enumerate(CORRECT_CATEGORIES["puzzle_books"], 1):
        print(f"  {i}. {cat}")

if __name__ == "__main__":
    main()