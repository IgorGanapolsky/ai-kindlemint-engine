#!/usr/bin/env python3
"""
Fix to REAL KDP Categories - Stop making up fake categories!
"""

import pandas as pd
import json
from pathlib import Path

def fix_real_kdp_categories():
    """Update with ACTUAL KDP categories from the interface"""
    
    print("🔧 FIXING TO REAL KDP CATEGORIES")
    print("=" * 50)
    print("❌ STOP making up fake categories like 'Large Print'!")
    print("✅ Using ACTUAL categories from KDP interface")
    
    # Load current metadata
    metadata_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kindle_metadata.json")
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Use REAL categories visible in the KDP interface
    kdp_data = {
        'Title': [metadata['title']],
        'Subtitle': [metadata['subtitle']],
        'Author': [metadata['author']],
        'Description': [metadata['description']],
        'Keywords': [', '.join(metadata['keywords'])],
        'Category1': ["Kindle Books > Humor & Entertainment > Activities, Puzzles & Games > Crosswords"],
        'Category2': ["Kindle Books > Reference"],
        'Category3': ["Kindle Books > Humor & Entertainment"],
        'Price': [4.99],
        'Territories': ['WORLD'],
        'Royalty': ['70%'],
        'KENP_READY': ['Yes']
    }
    
    # Create DataFrame
    df = pd.DataFrame(kdp_data)
    
    # Save corrected Excel
    output_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kdp_import.xlsx")
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Fixed KDP spreadsheet with REAL categories: {output_file}")
    print(f"📋 Categories used:")
    print(f"   1. Humor & Entertainment > Activities, Puzzles & Games > Crosswords")
    print(f"   2. Reference")
    print(f"   3. Humor & Entertainment")
    print(f"💡 These are ACTUAL categories visible in your KDP interface!")
    
    return output_file

if __name__ == "__main__":
    fix_real_kdp_categories()