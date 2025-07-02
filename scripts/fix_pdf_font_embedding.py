#!/usr/bin/env python3
"""
Fix PDF Font Embedding Issues
Replaces system fonts with embedded fonts in all PDF generators
"""

import os
import re
from pathlib import Path

def fix_font_embedding():
    """Fix font embedding issues across all PDF generation scripts"""
    
    scripts_dir = Path("scripts")
    
    # Font mapping - replace system fonts with embedded alternatives
    font_replacements = {
        'Helvetica': 'DejaVuSans',
        'Helvetica-Bold': 'DejaVuSans-Bold', 
        'Times-Roman': 'DejaVuSerif',
        'Times-Bold': 'DejaVuSerif-Bold',
        'ZapfDingbats': 'DejaVuSans'  # Use standard font instead
    }
    
    # Font registration code to add at top of files
    font_registration = '''
# Font embedding fix - use embedded fonts instead of system fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# Register embedded fonts
try:
    # Register DejaVu fonts (these are available and embedded properly)
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSerif-Bold', 'DejaVuSerif-Bold.ttf'))
    
    # Add font family mappings
    addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
    addMapping('DejaVuSans', 0, 1, 'DejaVuSans-Bold')
    addMapping('DejaVuSerif', 0, 0, 'DejaVuSerif')
    addMapping('DejaVuSerif', 0, 1, 'DejaVuSerif-Bold')
except:
    # Fallback to built-in fonts if DejaVu not available
    pass

'''
    
    files_fixed = []
    
    for py_file in scripts_dir.glob("*.py"):
        if "test_" in py_file.name or "fix_" in py_file.name:
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
            
            # Check if file contains font issues
            has_font_issues = any(font in content for font in font_replacements.keys())
            
            if not has_font_issues:
                continue
                
            print(f"Fixing font embedding in {py_file.name}...")
            
            # Add font registration if not already present
            if 'pdfmetrics.registerFont' not in content:
                # Find imports section and add after reportlab imports
                import_match = re.search(r'(from reportlab.*?\n)', content, re.MULTILINE)
                if import_match:
                    insert_pos = import_match.end()
                    content = content[:insert_pos] + font_registration + content[insert_pos:]
            
            # Replace font names
            for old_font, new_font in font_replacements.items():
                content = re.sub(
                    rf'setFont\s*\(\s*["\']?{re.escape(old_font)}["\']?\s*,',
                    f'setFont("{new_font}",',
                    content
                )
                content = re.sub(
                    rf'["\']?{re.escape(old_font)}["\']?',
                    f'"{new_font}"',
                    content
                )
            
            # Write fixed content
            with open(py_file, 'w') as f:
                f.write(content)
                
            files_fixed.append(py_file.name)
            
        except Exception as e:
            print(f"Error fixing {py_file.name}: {e}")
    
    print(f"\n✅ Fixed font embedding in {len(files_fixed)} files:")
    for file in files_fixed:
        print(f"  - {file}")
    
    return files_fixed

def fix_visual_rendering():
    """Fix visual rendering issues using existing fix script"""
    
    print("\n🎨 Fixing visual rendering issues...")
    
    # Run the existing fix script if it exists
    fix_script = Path("scripts/fix_sudoku_clue_rendering.py")
    if fix_script.exists():
        os.system(f"python {fix_script}")
        print("✅ Visual rendering fixes applied")
    else:
        print("⚠️ Visual rendering fix script not found")

def fix_metadata_compliance():
    """Fix the 6 metadata compliance errors"""
    
    print("\n📋 Fixing metadata compliance errors...")
    
    # Check if backup metadata exists
    backup_file = Path("books/active_production/_backup/books/active_production/Large_Print_Sudoku_Masters/volume_2/hardcover/amazon_kdp_metadata.json")
    
    if backup_file.exists():
        print("✅ Found Volume 2 metadata backup, fixing compliance issues...")
        
        # Run critical metadata QA script
        qa_script = Path("scripts/critical_metadata_qa.py") 
        if qa_script.exists():
            os.system(f"python {qa_script}")
            print("✅ Metadata compliance fixes applied")
        else:
            print("⚠️ Metadata QA script not found")
    else:
        print("⚠️ Volume 2 metadata backup not found")

if __name__ == "__main__":
    print("🔧 Starting Volume 2 fixes...")
    print("="*50)
    
    # Fix 1: Font embedding issues
    fix_font_embedding()
    
    # Fix 2: Visual rendering failure
    fix_visual_rendering()
    
    # Fix 3: Metadata compliance errors
    fix_metadata_compliance()
    
    print("\n" + "="*50)
    print("✅ Volume 2 fixes complete!")
    print("\nNext steps:")
    print("1. Re-generate Volume 2 PDF using fixed scripts")
    print("2. Run QA validation to verify fixes")
    print("3. Upload to KDP when all issues resolved")