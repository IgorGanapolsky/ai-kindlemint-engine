#!/usr/bin/env python3
"""
Font Embedding QA Checker
Validates that PDF has properly embedded fonts for Amazon KDP compliance
"""

import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF for PDF analysis
except ImportError:
    print("Installing PyMuPDF for font analysis...")
    import os
    os.system("pip install PyMuPDF")
    import fitz

def check_font_embedding(pdf_path):
    """Check if fonts are properly embedded in PDF"""
    
    print(f"🔍 FONT EMBEDDING QA CHECK")
    print("=" * 50)
    print(f"📄 Analyzing: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        
        # Get font information
        font_info = []
        embedded_fonts = 0
        total_fonts = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            font_list = page.get_fonts()
            
            for font in font_list:
                font_name = font[3]  # Font name
                font_type = font[1]  # Font type
                embedded = font[5]   # Embedded flag
                
                total_fonts += 1
                if embedded:
                    embedded_fonts += 1
                
                font_info.append({
                    "page": page_num + 1,
                    "name": font_name,
                    "type": font_type,
                    "embedded": embedded
                })
        
        # Analysis results
        print(f"\n📊 FONT ANALYSIS RESULTS")
        print("-" * 30)
        print(f"Total fonts found: {total_fonts}")
        print(f"Embedded fonts: {embedded_fonts}")
        print(f"Non-embedded fonts: {total_fonts - embedded_fonts}")
        
        # Detailed font list
        print(f"\n🔤 FONT DETAILS:")
        unique_fonts = {}
        for font in font_info:
            key = font["name"]
            if key not in unique_fonts:
                unique_fonts[key] = font
                status = "✅ EMBEDDED" if font["embedded"] else "❌ NOT EMBEDDED"
                print(f"  • {font['name']} ({font['type']}) - {status}")
        
        # KDP Compliance Check
        print(f"\n🎯 AMAZON KDP COMPLIANCE:")
        if embedded_fonts == total_fonts and total_fonts > 0:
            print("✅ PASS: All fonts are properly embedded")
            print("✅ Ready for Amazon KDP upload")
            compliance_score = 100
        elif embedded_fonts > 0:
            percentage = (embedded_fonts / total_fonts) * 100
            print(f"⚠️ PARTIAL: {percentage:.1f}% fonts embedded")
            print("❌ KDP may show font warning")
            compliance_score = percentage
        else:
            print("❌ FAIL: No fonts are embedded")
            print("❌ KDP will definitely show font warning")
            compliance_score = 0
        
        doc.close()
        
        return {
            "compliance_score": compliance_score,
            "total_fonts": total_fonts,
            "embedded_fonts": embedded_fonts,
            "font_details": unique_fonts,
            "kdp_ready": compliance_score == 100
        }
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return None

def main():
    """Run font embedding QA check"""
    
    pdf_path = "active_production/Large_Print_Crossword_Masters/volume_1/crossword_book_volume_1_embedded.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    results = check_font_embedding(pdf_path)
    
    if results:
        print(f"\n📋 FINAL QA VERDICT:")
        print("=" * 50)
        if results["kdp_ready"]:
            print("🎉 PDF IS 100% KDP READY!")
            print("✅ No font warnings expected")
            print("✅ Safe to upload to Amazon KDP")
        else:
            print("⚠️ PDF needs font embedding fixes")
            print(f"📊 Compliance score: {results['compliance_score']:.1f}%")

if __name__ == "__main__":
    main()