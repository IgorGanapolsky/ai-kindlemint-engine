#!/usr/bin/env python3
"""
Cover Redesign - High-Converting Kindle Cover
Fixes thumbnail legibility and adds professional elements
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import random

def create_high_converting_cover():
    """Create high-converting cover with improved legibility"""
    
    print("🎨 HIGH-CONVERTING COVER REDESIGN")
    print("=" * 50)
    print("🎯 Optimizing for thumbnail legibility and sales conversion")
    
    # Create 2560x1600 cover
    width, height = 2560, 1600
    
    # Start with dark green pattern background
    img = Image.new('RGB', (width, height), color='#2c3e50')
    draw = ImageDraw.Draw(img)
    
    # Create subtle crossword pattern (darker than before for better contrast)
    pattern_color = (35, 50, 65)  # Darker green
    cell_size = 120
    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            if (x // cell_size + y // cell_size) % 8 == 0:
                draw.rectangle([x, y, x + cell_size, y + cell_size], 
                             outline=(45, 60, 75), width=3)
    
    # Add 50% black-to-transparent vertical gradient overlay
    gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    
    for y in range(height):
        alpha = int(128 * (1 - y / height))  # 50% to 0% opacity
        grad_draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    
    # Composite gradient over background
    img = Image.alpha_composite(img.convert('RGBA'), gradient).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Load fonts (with fallbacks)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Optima.ttc", 160)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Optima.ttc", 70)
        ribbon_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 85)
        badge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 90)
    except:
        print("⚠️ Using default fonts")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        ribbon_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()
    
    # Main title with drop shadow
    title_lines = ["LARGE PRINT", "CROSSWORD", "MASTERS"]
    y_start = 150
    
    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + i * 140
        
        # Drop shadow (2px offset)
        shadow_offset = 6
        draw.text((x + shadow_offset, y + shadow_offset), line, 
                 fill=(0, 0, 0, 200), font=title_font)
        
        # Main title text (pure white)
        draw.text((x, y), line, fill='white', font=title_font)
    
    # Gold ribbon across full width (180px high)
    ribbon_y = 750
    ribbon_height = 180
    draw.rectangle([0, ribbon_y, width, ribbon_y + ribbon_height], 
                  fill='#E2B23A')
    
    # Ribbon text
    ribbon_text = "CROSSWORD MASTERS PUBLISHING"
    ribbon_bbox = draw.textbbox((0, 0), ribbon_text, font=ribbon_font)
    ribbon_text_width = ribbon_bbox[2] - ribbon_bbox[0]
    ribbon_x = (width - ribbon_text_width) // 2
    ribbon_text_y = ribbon_y + (ribbon_height - (ribbon_bbox[3] - ribbon_bbox[1])) // 2
    
    # Ribbon text shadow
    draw.text((ribbon_x + 3, ribbon_text_y + 3), ribbon_text, 
             fill=(0, 0, 0, 100), font=ribbon_font)
    draw.text((ribbon_x, ribbon_text_y), ribbon_text, 
             fill='white', font=ribbon_font)
    
    # Volume 1 diagonal teal ribbon (top-right)
    ribbon_width = 400
    ribbon_height_small = 120
    
    # Create diagonal ribbon
    ribbon_img = Image.new('RGBA', (ribbon_width, ribbon_height_small), '#0F7CAC')
    ribbon_draw = ImageDraw.Draw(ribbon_img)
    
    # Add "VOLUME 1" text to ribbon
    vol_text = "VOLUME 1"
    vol_bbox = ribbon_draw.textbbox((0, 0), vol_text, font=badge_font)
    vol_x = (ribbon_width - (vol_bbox[2] - vol_bbox[0])) // 2
    vol_y = (ribbon_height_small - (vol_bbox[3] - vol_bbox[1])) // 2
    
    ribbon_draw.text((vol_x + 2, vol_y + 2), vol_text, fill=(0, 0, 0, 80), font=badge_font)
    ribbon_draw.text((vol_x, vol_y), vol_text, fill='white', font=badge_font)
    
    # Rotate ribbon slightly
    ribbon_rotated = ribbon_img.rotate(-15, expand=True)
    
    # Position in top-right
    ribbon_x = width - ribbon_rotated.width + 50
    ribbon_y = 80
    
    # Paste ribbon with alpha
    img.paste(ribbon_rotated, (ribbon_x, ribbon_y), ribbon_rotated)
    
    # Add subtitle at bottom
    subtitle_text = "50 Easy, Relaxing Crossword Puzzles for Seniors"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = height - 200
    
    # Subtitle with better contrast
    draw.text((subtitle_x + 2, subtitle_y + 2), subtitle_text, 
             fill=(0, 0, 0, 150), font=subtitle_font)
    draw.text((subtitle_x, subtitle_y), subtitle_text, 
             fill='#f1c40f', font=subtitle_font)
    
    # Save main cover
    cover_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/cover_v1b.jpg")
    img.save(cover_path, "JPEG", quality=90, optimize=True)
    
    # Create thumbnail proof (128x200)
    thumbnail = img.resize((128, 200), Image.Resampling.LANCZOS)
    thumb_path = Path("books/active_production/Large_Print_Crossword_Masters/volume_1/cover_thumb_128x200.jpg")
    thumbnail.save(thumb_path, "JPEG", quality=85)
    
    # Check file sizes
    cover_size = cover_path.stat().st_size / (1024 * 1024)
    thumb_size = thumb_path.stat().st_size / 1024
    
    print(f"✅ High-converting cover created: {cover_path}")
    print(f"📐 Dimensions: 2560×1600 pixels")
    print(f"💾 File size: {cover_size:.2f} MB")
    print(f"🔍 Thumbnail proof: {thumb_path} ({thumb_size:.1f} KB)")
    
    # Optimize if over 2MB
    if cover_size > 2.0:
        print("⚠️ Optimizing file size...")
        img.save(cover_path, "JPEG", quality=80, optimize=True)
        cover_size = cover_path.stat().st_size / (1024 * 1024)
        print(f"✅ Optimized to: {cover_size:.2f} MB")
    
    print(f"\n🎯 IMPROVEMENTS MADE:")
    print(f"✅ Added 50% black-to-transparent gradient overlay")
    print(f"✅ Enhanced title contrast with drop shadows")
    print(f"✅ Added gold ribbon with publisher branding")
    print(f"✅ Added diagonal teal Volume 1 badge")
    print(f"✅ Created 128×200 thumbnail proof for legibility check")
    
    return cover_path, thumb_path

if __name__ == "__main__":
    cover_file, thumb_file = create_high_converting_cover()