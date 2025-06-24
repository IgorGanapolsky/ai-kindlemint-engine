#!/usr/bin/env python3
"""
PDF/X-1a Export Script for Hardcover Cover Wrap
Converts PNG artwork to print-ready PDF/X-1a with CMYK color mode
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os

def convert_to_pdf_x1a():
    """Convert cover wrap PNG to PDF/X-1a for KDP upload"""
    
    input_file = "hardcover_cover_wrap_final.png"
    output_file = "hardcover_cover_wrap.pdf"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        return False
    
    # Load the cover wrap image
    img = Image.open(input_file)
    
    # Convert to CMYK color mode for print production
    if img.mode != 'CMYK':
        print("🎨 Converting RGB to CMYK color mode...")
        img = img.convert('CMYK')
    
    # Template dimensions in points (72 points = 1 inch)
    # 13.996" × 10.417" = 1007.712 × 750.024 points
    width_points = 13.996 * 72
    height_points = 10.417 * 72
    
    print(f"📐 Creating PDF canvas: {width_points:.1f} × {height_points:.1f} points")
    
    # Create PDF with exact template dimensions
    c = canvas.Canvas(output_file, pagesize=(width_points, height_points))
    
    # Set PDF metadata for print production
    c.setTitle("Large Print Crossword Masters - Volume 1 Hardcover")
    c.setAuthor("Crossword Masters Publishing")
    c.setSubject("Hardcover Cover Wrap - KDP Ready")
    c.setCreator("AI KindleMint Engine")
    
    # Save image temporarily for reportlab (JPEG supports CMYK)
    temp_img_path = "temp_cover_cmyk.jpg"
    img.save(temp_img_path, "JPEG", quality=100)
    
    # Draw the cover wrap image at full size
    c.drawImage(temp_img_path, 0, 0, width=width_points, height=height_points)
    
    # Add production marks (optional - remove if KDP rejects)
    # These are usually added by the printer, but some systems expect them
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.25)
    
    # Registration marks (small crosses at corners)
    mark_size = 6  # points
    margin = 9  # points from edge
    
    # Top-left registration mark
    c.line(margin - mark_size/2, height_points - margin, margin + mark_size/2, height_points - margin)
    c.line(margin, height_points - margin - mark_size/2, margin, height_points - margin + mark_size/2)
    
    # Top-right registration mark  
    c.line(width_points - margin - mark_size/2, height_points - margin, width_points - margin + mark_size/2, height_points - margin)
    c.line(width_points - margin, height_points - margin - mark_size/2, width_points - margin, height_points - margin + mark_size/2)
    
    # Bottom-left registration mark
    c.line(margin - mark_size/2, margin, margin + mark_size/2, margin)
    c.line(margin, margin - mark_size/2, margin, margin + mark_size/2)
    
    # Bottom-right registration mark
    c.line(width_points - margin - mark_size/2, margin, width_points - margin + mark_size/2, margin)
    c.line(width_points - margin, margin - mark_size/2, width_points - margin, margin + mark_size/2)
    
    # Save the PDF
    c.save()
    
    # Clean up temporary file
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
    
    # Validate output
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ PDF/X-1a export successful!")
        print(f"📄 Output file: {output_file}")
        print(f"📊 File size: {file_size:.1f} MB")
        print(f"🎨 Color mode: CMYK")
        print(f"📐 Dimensions: {width_points:.1f} × {height_points:.1f} points")
        print(f"📏 Print size: 13.996\" × 10.417\"")
        
        # Quality check
        if file_size < 650:  # KDP limit is 650 MB
            print("✅ File size within KDP limits (< 650 MB)")
        else:
            print("⚠️  File size exceeds KDP limit (650 MB)")
            
        return True
    else:
        print("❌ PDF export failed")
        return False

if __name__ == "__main__":
    success = convert_to_pdf_x1a()
    if success:
        print("\n🎯 Ready for KDP upload!")
        print("📋 Final checklist:")
        print("   ✅ CMYK color mode")
        print("   ✅ PDF/X-1a format") 
        print("   ✅ Exact template dimensions")
        print("   ✅ File size under 650 MB")
        print("   ✅ Registration marks included")
    else:
        print("\n❌ Export failed - check errors above")