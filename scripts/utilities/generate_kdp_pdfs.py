#!/usr/bin/env python3
"""
KDP PDF Generator Script
Automatically converts all crossword manuscripts to KDP-ready PDFs
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.core.pdf_generator import generate_all_volume_pdfs
from kindlemint.utils.logger import get_logger

def main():
    """Generate KDP-ready PDFs for all volumes."""
    logger = get_logger('kdp_pdf_generator')
    
    logger.info("🎯 KDP PDF Generator - Converting manuscripts to PDFs")
    
    try:
        # Generate PDFs for all volumes
        generated_pdfs = generate_all_volume_pdfs()
        
        if generated_pdfs:
            logger.info(f"🎉 SUCCESS: Generated {len(generated_pdfs)} KDP-ready PDFs!")
            
            print("\n" + "="*60)
            print("📄 KDP-READY PDF FILES GENERATED:")
            print("="*60)
            
            for pdf_path in generated_pdfs:
                file_size = os.path.getsize(pdf_path)
                size_mb = file_size / (1024 * 1024)
                print(f"✅ {Path(pdf_path).name}")
                print(f"   📊 Size: {size_mb:.1f} MB")
                print(f"   📁 Path: {pdf_path}")
                print()
            
            print("="*60)
            print("🚀 NEXT STEPS FOR KDP PUBLISHING:")
            print("="*60)
            print("1. Go to kdp.amazon.com")
            print("2. Create/Edit your book")
            print("3. Upload the PDF file as your manuscript")
            print("4. Use your existing cover image")
            print("5. Your books now have 100+ pages (no narrow spine error)")
            print("6. Preview and publish!")
            print()
            print("💡 TIP: PDF format preserves crossword grid formatting perfectly")
            print("💡 TIP: Large print fonts are optimized for senior readers")
            
            return True
            
        else:
            logger.error("❌ No PDFs were generated. Check for errors above.")
            return False
            
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)