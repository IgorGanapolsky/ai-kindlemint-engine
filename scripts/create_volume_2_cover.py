#!/usr/bin/env python3
"""
Create Volume 2 cover image
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Create cover image
width = 2550  # 8.5" at 300 DPI
height = 3300  # 11" at 300 DPI

# Create image with navy blue background
img = Image.new("RGB", (width, height), "#2C3E50")
draw = ImageDraw.Draw(img)

# Try to load fonts
try:
    title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 180)
    subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    volume_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
    publisher_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
except BaseException:
    # Fallback
    title_font = ImageFont.load_default()
    subtitle_font = title_font
    volume_font = title_font
    publisher_font = title_font

# Title
title_lines = ["LARGE", "PRINT", "CROSSWORD", "MASTERS"]
y_pos = 400
for line in title_lines:
    bbox = draw.textbbox((0, 0), line, font=title_font)
    text_width = bbox[2] - bbox[0]
    x_pos = (width - text_width) // 2
    draw.text((x_pos, y_pos), line, fill="#ECF0F1", font=title_font)
    y_pos += 220

# Volume banner
banner_y = 200
banner_points = [
    (width - 800, banner_y),
    (width - 200, banner_y),
    (width - 300, banner_y + 200),
    (width - 900, banner_y + 200),
]
draw.polygon(banner_points, fill="#F39C12")

# Volume text
draw.text((width - 700, banner_y + 50), "VOLUME 2", fill="#2C3E50", font=volume_font)

# Subtitle band
band_y = height // 2
draw.rectangle([(0, band_y), (width, band_y + 300)], fill="#F39C12")

# Subtitle text
subtitle_lines = ["50 NEW", "CROSSWORD PUZZLES-", "EASY TO CHALLENGING"]
y_pos = band_y + 30
for line in subtitle_lines:
    bbox = draw.textbbox((0, 0), line, font=subtitle_font)
    text_width = bbox[2] - bbox[0]
    x_pos = (width - text_width) // 2
    draw.text((x_pos, y_pos), line, fill="#2C3E50", font=subtitle_font)
    y_pos += 80

# Publisher
publisher_lines = ["CROSSWORD MASTERS", "PUBLISHING"]
y_pos = height - 400
for line in publisher_lines:
    bbox = draw.textbbox((0, 0), line, font=publisher_font)
    text_width = bbox[2] - bbox[0]
    x_pos = (width - text_width) // 2
    draw.text((x_pos, y_pos), line, fill="#ECF0F1", font=publisher_font)
    y_pos += 70

# Save cover
output_path = Path(
    "books/active_production/Large_Print_Crossword_Masters/volume_2/paperback/cover.png"
)
img.save(output_path, "PNG")
print(f"✅ Cover created: {output_path}")
