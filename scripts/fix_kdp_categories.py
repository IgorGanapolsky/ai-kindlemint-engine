#!/usr/bin/env python3
"""
Fix KDP Categories - Update to 3 categories as now allowed by Amazon
"""

import pandas as pd
import json
from pathlib import Path

def update_kdp_categories():
    """Update KDP import with correct 3 categories"""
    
    print("📊 UPDATING KDP CATEGORIES")
    print("=" * 50)
    print("🎯 Amazon KDP now allows 3 categories!")
    
    # Load current metadata
    metadata_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kindle_metadata.json")
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Create updated KDP data with 3 categories
    kdp_data = {
        'Title': [metadata['title']],
        'Subtitle': [metadata['subtitle']],
        'Author': [metadata['author']],
        'Description': [metadata['description']],
        'Keywords': [', '.join(metadata['keywords'])],
        'Category1': ["Kindle Books > Humor & Entertainment > Activities, Puzzles & Games > Crosswords"],
        'Category2': ["Kindle Books > Large Print"],
        'Category3': ["Kindle Books > Games > Crosswords"],  # NEW 3rd category
        'Price': [4.99],
        'Territories': ['WORLD'],
        'Royalty': ['70%'],
        'KENP_READY': ['Yes']
    }
    
    # Create DataFrame
    df = pd.DataFrame(kdp_data)
    
    # Save updated Excel
    output_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kdp_import.xlsx")
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ Updated KDP spreadsheet: {output_file}")
    print(f"📈 Now includes 3 categories for maximum visibility:")
    print(f"   1. Crosswords (primary)")
    print(f"   2. Large Print (accessibility)")  
    print(f"   3. Games > Crosswords (broader reach)")
    
    return output_file

if __name__ == "__main__":
    update_kdp_categories()