#!/usr/bin/env python3
"""
KDP Import Spreadsheet Generator
Creates Excel file for bulk metadata upload to Amazon KDP
"""

import json
import pandas as pd
from pathlib import Path

def create_kdp_import_spreadsheet():
    """Create KDP import Excel file"""
    
    print("📊 KDP IMPORT SPREADSHEET GENERATOR")
    print("=" * 50)
    
    # Load metadata
    metadata_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kindle_metadata.json")
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Create KDP import data
    kdp_data = {
        'Title': [metadata['title']],
        'Subtitle': [metadata['subtitle']],
        'Author': [metadata['author']],
        'Description': [metadata['description']],
        'Keywords': [', '.join(metadata['keywords'])],
        'Category1': [metadata['categories'][0]],
        'Category2': [metadata['categories'][1] if len(metadata['categories']) > 1 else ''],
        'Price': [4.99],
        'Territories': ['WORLD'],
        'Royalty': ['70%'],
        'KENP_READY': ['Yes']
    }
    
    # Create DataFrame
    df = pd.DataFrame(kdp_data)
    
    # Save to Excel
    output_file = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/kdp_import.xlsx")
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"✅ KDP import spreadsheet created: {output_file}")
    print(f"📈 Ready for Amazon KDP bulk upload")
    
    return output_file

def create_professional_cover():
    """Create 2560x1600 professional cover"""
    
    print("\n🎨 PROFESSIONAL COVER GENERATOR")
    print("=" * 50)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import requests
        
        # Create 2560x1600 cover
        width, height = 2560, 1600
        
        # Calm teal-green gradient background
        img = Image.new('RGB', (width, height), color='#2c3e50')
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        for y in range(height):
            # Gradient from teal to darker teal
            ratio = y / height
            r = int(44 + (52 - 44) * ratio)  # 2c to 34
            g = int(62 + (73 - 62) * ratio)  # 3e to 49
            b = int(80 + (94 - 80) * ratio)  # 50 to 5e
            color = (r, g, b)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Draw subtle crossword grid pattern
        grid_color = (255, 255, 255, 30)  # Semi-transparent white
        cell_size = 80
        for x in range(0, width, cell_size):
            for y in range(0, height, cell_size):
                # Random pattern for crossword feel
                if (x // cell_size + y // cell_size) % 7 == 0:
                    draw.rectangle([x, y, x + cell_size, y + cell_size], 
                                 outline=(255, 255, 255, 50), width=2)
        
        # Load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 70)
            badge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 90)
            author_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        except:
            print("⚠️ Using default fonts")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            badge_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
        
        # Title positioning
        title_lines = ["LARGE PRINT", "CROSSWORD", "MASTERS"]
        y_start = 200
        
        for i, line in enumerate(title_lines):
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = y_start + i * 120
            
            # Draw text with shadow for readability
            shadow_offset = 4
            draw.text((x + shadow_offset, y + shadow_offset), line, 
                     fill=(0, 0, 0, 100), font=title_font)  # Shadow
            draw.text((x, y), line, fill='white', font=title_font)  # Main text
        
        # Volume badge (top right)
        badge_text = "Volume 1"
        badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_width = badge_bbox[2] - badge_bbox[0]
        badge_x = width - badge_width - 100
        badge_y = 100
        
        # Badge background
        badge_bg = Image.new('RGBA', (badge_width + 40, 100), (241, 196, 15, 200))
        img.paste(badge_bg, (badge_x - 20, badge_y - 10), badge_bg)
        
        draw.text((badge_x, badge_y), badge_text, fill='white', font=badge_font)
        
        # Subtitle
        subtitle_text = "50 Easy, Relaxing Crossword Puzzles for Seniors"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = 750
        
        # Subtitle background for readability
        subtitle_bg = Image.new('RGBA', (subtitle_width + 60, 90), (0, 0, 0, 120))
        img.paste(subtitle_bg, (subtitle_x - 30, subtitle_y - 10), subtitle_bg)
        
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill='#f1c40f', font=subtitle_font)
        
        # Author at bottom
        author_text = "Crossword Masters Publishing"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (width - author_width) // 2
        author_y = height - 150
        
        draw.text((author_x, author_y), author_text, fill='white', font=author_font)
        
        # Add crossword squares decoration
        square_size = 40
        for i in range(5):
            x = 100 + i * 60
            y = height - 300
            if i % 2 == 0:
                draw.rectangle([x, y, x + square_size, y + square_size], 
                             fill='white', outline='#2c3e50', width=3)
                # Add number
                draw.text((x + 15, y + 10), str(i + 1), fill='#2c3e50', font=author_font)
            else:
                draw.rectangle([x, y, x + square_size, y + square_size], 
                             fill='#2c3e50', outline='white', width=3)
        
        # Save cover
        cover_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/cover_v1.jpg")
        img.save(cover_path, "JPEG", quality=85, optimize=True)
        
        # Check file size
        file_size = cover_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Professional cover created: {cover_path}")
        print(f"📐 Dimensions: 2560×1600 pixels")
        print(f"💾 File size: {file_size:.2f} MB")
        
        if file_size > 2.0:
            print("⚠️ File size over 2MB - optimizing...")
            img.save(cover_path, "JPEG", quality=75, optimize=True)
            file_size = cover_path.stat().st_size / (1024 * 1024)
            print(f"✅ Optimized to: {file_size:.2f} MB")
        
        return cover_path
        
    except ImportError:
        print("❌ PIL (Pillow) not installed. Run: pip install Pillow")
        return None

def main():
    """Generate KDP import files"""
    
    # Create spreadsheet
    xlsx_file = create_kdp_import_spreadsheet()
    
    # Create cover
    cover_file = create_professional_cover()
    
    print(f"\n🎉 KDP IMPORT PACKAGE COMPLETE")
    print(f"📊 Spreadsheet: {xlsx_file}")
    print(f"🎨 Cover: {cover_file}")
    print(f"✅ Ready for Amazon KDP upload")

if __name__ == "__main__":
    main()