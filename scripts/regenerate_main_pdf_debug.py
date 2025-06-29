#!/usr/bin/env python3
"""
Regenerate main PDF with debugging to ensure it uses the correct images
"""

import subprocess
import sys
from pathlib import Path

def regenerate_main_pdf_with_debug():
    """Regenerate the main PDF with extensive debugging."""
    
    print("🔧 REGENERATING MAIN PDF WITH DEBUGGING")
    print("="*60)
    
    # 1. Verify images exist and have recent timestamps
    puzzles_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1/puzzles")
    test_images = ["sudoku_puzzle_098.png", "sudoku_puzzle_100.png"]
    
    print("\n📋 Verifying key test images...")
    for img_name in test_images:
        img_path = puzzles_dir / img_name
        if img_path.exists():
            stat = img_path.stat()
            print(f"✅ {img_name}: {stat.st_size} bytes, modified {stat.st_mtime}")
        else:
            print(f"❌ {img_name}: NOT FOUND")
            return False
    
    # 2. Delete old PDF to ensure clean regeneration
    output_dir = Path("books/active_production/Large_Print_Sudoku_Masters/volume_1/paperback")
    old_pdf = output_dir / "Large_Print_Sudoku_Masters_V1_COMPLETE.pdf"
    
    if old_pdf.exists():
        print(f"\n🗑️ Removing old PDF: {old_pdf}")
        old_pdf.unlink()
    
    # 3. Regenerate with explicit parameters
    print("\n🎨 Regenerating main PDF...")
    
    cmd = [
        "python", "scripts/sudoku_pdf_layout_v2.py",
        "--input", str(puzzles_dir),
        "--output", str(output_dir),
        "--title", "Large Print Sudoku Masters",
        "--author", "KindleMint Publishing",
        "--subtitle", "100 Challenging Puzzles with Large Print Format",
        "--page-size", "letter",
        "--include-solutions"
    ]
    
    print(f"🔍 Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ PDF generation completed successfully")
            print(f"📄 Output: {result.stdout}")
        else:
            print("❌ PDF generation failed")
            print(f"📄 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PDF generation timed out")
        return False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False
    
    # 4. Rename the generated PDF to the expected name
    generated_pdf = output_dir / "Large_Print_Sudoku_Masters_Interior.pdf"
    target_pdf = output_dir / "Large_Print_Sudoku_Masters_V1_COMPLETE.pdf"
    
    if generated_pdf.exists():
        print(f"📋 Renaming {generated_pdf.name} to {target_pdf.name}")
        generated_pdf.rename(target_pdf)
    else:
        print(f"❌ Generated PDF not found: {generated_pdf}")
        return False
    
    # 5. Verify the final PDF
    if target_pdf.exists():
        stat = target_pdf.stat()
        print(f"✅ Final PDF: {stat.st_size} bytes")
        
        # Quick sanity check - should be > 5MB for 100 puzzles
        if stat.st_size > 5_000_000:
            print("✅ PDF size looks reasonable for 100 puzzles")
            return True
        else:
            print("⚠️ PDF size seems small - may be missing content")
            return False
    else:
        print(f"❌ Final PDF not found: {target_pdf}")
        return False

if __name__ == "__main__":
    success = regenerate_main_pdf_with_debug()
    
    if success:
        print("\n" + "="*60)
        print("🎉 MAIN PDF REGENERATION COMPLETED")
        print("🔍 Now validate the new PDF...")
    else:
        print("\n" + "="*60)
        print("❌ MAIN PDF REGENERATION FAILED")
    
    print("="*60)