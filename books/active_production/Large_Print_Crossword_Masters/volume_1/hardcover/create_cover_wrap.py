#!/usr/bin/env python3
"""
Hardcover Cover Wrap Designer for Large Print Crossword Masters - Volume 1
Creates a print-ready PDF/X-1a cover wrap for KDP hardcover publishing
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json

def create_cover_wrap():
    """Create hardcover cover wrap following KDP specifications"""
    
    # Template dimensions from KDP (13.996" × 10.417" at 300 DPI)
    template_width = int(13.996 * 300)  # 4199 pixels
    template_height = int(10.417 * 300)  # 3125 pixels
    
    # Load template for alignment (will be hidden in final export)
    template_path = "kdp_template.png"
    template = Image.open(template_path).convert("RGBA")
    template = template.resize((template_width, template_height), Image.Resampling.LANCZOS)
    
    # Load source front cover
    front_cover_path = "cover_source_1600x2560.jpg" 
    front_cover = Image.open(front_cover_path).convert("RGB")
    
    # Create main canvas
    canvas = Image.new("RGB", (template_width, template_height), "white")
    
    # Create template overlay at 30% opacity for alignment
    template_overlay = Image.new("RGBA", (template_width, template_height), (0, 0, 0, 0))
    template_alpha = template.copy()
    template_alpha.putalpha(int(255 * 0.3))  # 30% opacity
    template_overlay.paste(template_alpha, (0, 0), template_alpha)
    
    # Calculate cover areas based on template specifications
    # Front cover area (right side): 6" × 9" at 300 DPI = 1800 × 2700 pixels
    front_width = int(6 * 300)  # 1800 pixels
    front_height = int(9 * 300)  # 2700 pixels
    
    # Spine width: 0.421" at 300 DPI = 126 pixels
    spine_width = int(0.421 * 300)  # 126 pixels
    
    # Back cover area (left side): 6" × 9" 
    back_width = front_width
    back_height = front_height
    
    # Position calculations (from right to left: front, spine, back)
    front_x = template_width - front_width - int(0.125 * 300)  # Right margin
    front_y = int((template_height - front_height) / 2)  # Centered vertically
    
    spine_x = front_x - spine_width
    spine_y = front_y
    
    back_x = spine_x - back_width
    back_y = front_y
    
    # === FRONT COVER (RIGHT SIDE) ===
    # Scale front cover to fit maintaining aspect ratio
    front_ratio = min(front_width / front_cover.width, front_height / front_cover.height)
    scaled_width = int(front_cover.width * front_ratio)
    scaled_height = int(front_cover.height * front_ratio)
    
    front_scaled = front_cover.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    
    # Center the scaled front cover in the front area
    front_paste_x = front_x + (front_width - scaled_width) // 2
    front_paste_y = front_y + (front_height - scaled_height) // 2
    
    canvas.paste(front_scaled, (front_paste_x, front_paste_y))
    
    # === BACK COVER (LEFT SIDE) ===
    # Extract background elements from front cover for seamless extension
    # Use the left edge of the front cover to extend to back
    back_sample = front_cover.crop((0, 0, 200, front_cover.height))
    back_background = back_sample.resize((back_width, back_height), Image.Resampling.LANCZOS)
    
    # Apply subtle gradient overlay to distinguish back from front
    gradient = Image.new("RGBA", (back_width, back_height), (0, 0, 0, 0))
    draw_gradient = ImageDraw.Draw(gradient)
    for y in range(back_height):
        alpha = int(40 * (y / back_height))  # Subtle gradient
        draw_gradient.rectangle([(0, y), (back_width, y+1)], fill=(0, 0, 0, alpha))
    
    back_with_gradient = Image.alpha_composite(
        back_background.convert("RGBA"), 
        gradient
    ).convert("RGB")
    
    canvas.paste(back_with_gradient, (back_x, back_y))
    
    # === SPINE (CENTER) ===
    # Create spine background - extend from front cover
    spine_sample = front_cover.crop((front_cover.width//2 - 50, 0, front_cover.width//2 + 50, front_cover.height))
    spine_background = spine_sample.resize((spine_width, front_height), Image.Resampling.LANCZOS)
    canvas.paste(spine_background, (spine_x, spine_y))
    
    # === TEXT OVERLAY ===
    draw = ImageDraw.Draw(canvas)
    
    # Load system fonts (fallback to default if not available)
    def load_font(size):
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/Library/Fonts/Arial.ttf",
            "/opt/homebrew/share/fonts/liberation/LiberationSans-Regular.ttf"
        ]
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        return ImageFont.load_default()
    
    title_font = load_font(48)
    subtitle_font = load_font(32) 
    publisher_font = load_font(24)
    desc_font = load_font(36)
    
    # SPINE TEXT (stacked vertically, centered)
    spine_margin = int(0.125 * 300)  # 0.125" margin
    
    # Title: "LARGE PRINT CROSSWORD MASTERS" (rotated)
    title_text = "LARGE PRINT CROSSWORD MASTERS"
    spine_title_img = Image.new("RGBA", (600, spine_width), (0, 0, 0, 0))
    spine_title_draw = ImageDraw.Draw(spine_title_img)
    spine_title_draw.text((10, spine_width//2), title_text, font=title_font, fill="white", anchor="lm")
    spine_title_rotated = spine_title_img.rotate(90, expand=True)
    
    # Position spine title (centered vertically, with margins)
    spine_title_y = spine_y + spine_margin
    spine_title_x = spine_x + (spine_width - spine_title_rotated.width) // 2
    canvas.paste(spine_title_rotated, (spine_title_x, spine_title_y), spine_title_rotated)
    
    # Publisher at bottom of spine
    publisher_text = "CROSSWORD MASTERS PUBLISHING"
    publisher_img = Image.new("RGBA", (400, spine_width), (0, 0, 0, 0))
    publisher_draw = ImageDraw.Draw(publisher_img)
    publisher_draw.text((10, spine_width//2), publisher_text, font=publisher_font, fill="white", anchor="lm")
    publisher_rotated = publisher_img.rotate(90, expand=True)
    
    publisher_y = spine_y + front_height - publisher_rotated.height - spine_margin
    publisher_x = spine_x + (spine_width - publisher_rotated.width) // 2
    canvas.paste(publisher_rotated, (publisher_x, publisher_y), publisher_rotated)
    
    # BACK COVER TEXT
    # Book description
    description = """Rediscover the joy of crossword puzzles with Large Print 
Crossword Masters – Volume 1, specially designed for seniors 
and anyone who loves clear, readable puzzles!

This thoughtfully crafted collection features 50 brand-new 
crossword puzzles in crisp, large print format that's easy 
on your eyes and gentle on your mind.

• 50 completely unique crossword puzzles
• Extra-large print for comfortable reading  
• Everyday vocabulary that's familiar
• Complete answer key included
• Premium hardcover edition

Perfect for morning coffee, evening relaxation, or as a 
thoughtful gift for puzzle-loving friends and family.

Transform your puzzle time into quality time with this 
premium hardcover collection."""
    
    # Position description text
    desc_x = back_x + 60
    desc_y = back_y + 100
    desc_width = back_width - 120
    
    # Draw description with line wrapping
    lines = description.split('\n')
    line_height = 45
    current_y = desc_y
    
    for line in lines:
        if line.strip():
            draw.text((desc_x, current_y), line.strip(), font=desc_font, fill="white")
        current_y += line_height
    
    # Barcode placeholder (2" × 1.2" in yellow area)
    barcode_width = int(2.0 * 300)  # 600 pixels
    barcode_height = int(1.2 * 300)  # 360 pixels
    barcode_x = back_x + back_width - barcode_width - 60
    barcode_y = back_y + back_height - barcode_height - 60
    
    # Draw barcode placeholder
    draw.rectangle([
        (barcode_x, barcode_y), 
        (barcode_x + barcode_width, barcode_y + barcode_height)
    ], fill="white", outline="black", width=2)
    
    barcode_font = load_font(24)
    draw.text(
        (barcode_x + barcode_width//2, barcode_y + barcode_height//2), 
        "BARCODE\nPLACEHOLDER", 
        font=barcode_font, 
        fill="black", 
        anchor="mm"
    )
    
    # Composite template overlay for alignment reference (will be removed)
    canvas_with_template = Image.alpha_composite(canvas.convert("RGBA"), template_overlay)
    
    # Save preview with template
    preview_path = "hardcover_cover_wrap_preview.png"
    canvas_with_template.convert("RGB").save(preview_path, "PNG", quality=95)
    
    # Save final version without template
    final_path = "hardcover_cover_wrap_final.png"
    canvas.save(final_path, "PNG", quality=95)
    
    print(f"✅ Cover wrap created successfully!")
    print(f"📐 Canvas dimensions: {template_width} × {template_height} pixels")
    print(f"📄 Preview (with template): {preview_path}")
    print(f"🎨 Final artwork: {final_path}")
    print(f"📊 File size: {os.path.getsize(final_path) / (1024*1024):.1f} MB")
    
    return final_path

if __name__ == "__main__":
    create_cover_wrap()