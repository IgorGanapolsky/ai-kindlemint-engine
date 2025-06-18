#!/usr/bin/env python3
"""
Organize generated books for Google Drive upload
Creates clean folder structure with proper naming
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

def organize_books_for_upload():
    """Organize all generated books into a clean structure for Google Drive upload"""
    
    print("📁 Organizing books for Google Drive upload...")
    
    # Create organized output directory
    organized_dir = Path("output/READY_FOR_GOOGLE_DRIVE")
    organized_dir.mkdir(exist_ok=True)
    
    # Create series folder
    series_dir = organized_dir / "Large_Print_Crossword_Masters"
    series_dir.mkdir(exist_ok=True)
    
    # Find all correctly numbered volumes (vol_2, vol_3, vol_4, vol_5)
    books_dir = Path("output/generated_books")
    
    # Find the latest generated volumes with correct numbering
    volume_folders = {}
    for folder in books_dir.iterdir():
        if folder.is_dir() and "crossword_masters_vol_" in folder.name:
            # Extract volume number from folder name
            if "_vol_2_" in folder.name:
                volume_folders[2] = folder
            elif "_vol_3_" in folder.name:
                volume_folders[3] = folder
            elif "_vol_4_" in folder.name:
                volume_folders[4] = folder
            elif "_vol_5_" in folder.name:
                volume_folders[5] = folder
    
    # Also include the first correctly named Volume 1
    for folder in books_dir.iterdir():
        if folder.is_dir() and "crossword_masters_vol_1_" in folder.name and folder.name.endswith("122347"):
            volume_folders[1] = folder
            break
    
    print(f"📚 Found {len(volume_folders)} correctly numbered volumes")
    
    # Copy each volume to organized structure
    for vol_num in sorted(volume_folders.keys()):
        source_folder = volume_folders[vol_num]
        
        # Read metadata to get proper title
        metadata_file = source_folder / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            title = metadata.get('title', f'Large Print Crossword Masters: Volume {vol_num}')
        else:
            title = f'Large Print Crossword Masters: Volume {vol_num}'
        
        # Create clean folder name
        clean_name = f"Volume_{vol_num:02d}_{title.replace(':', '').replace(' ', '_')}"
        target_folder = series_dir / clean_name
        
        print(f"📖 Organizing Volume {vol_num}: {clean_name}")
        
        # Copy folder contents
        if target_folder.exists():
            shutil.rmtree(target_folder)
        shutil.copytree(source_folder, target_folder)
        
        # Add a README for this volume
        readme_content = f"""# {title}

## Volume Information
- **Series**: Large Print Crossword Masters
- **Volume**: {vol_num}
- **Brand**: Senior Puzzle Studio
- **Generated**: {datetime.now().strftime('%Y-%m-%d')}

## Files Included
- `manuscript.txt` - Complete book manuscript ready for KDP
- `metadata.json` - Book metadata and keywords
- `cover_design_prompt.txt` - Professional cover design specifications
- `marketing_content.txt` - Social media posts and marketing copy
- `KDP_PUBLISHING_GUIDE.txt` - Step-by-step publishing instructions

## Publishing Status
- [ ] Cover created
- [ ] Uploaded to Amazon KDP
- [ ] Published and available
- [ ] Marketing campaign launched

## Notes
Generated with KindleMint AI Publishing System using Gemini AI (ultra-low cost).
Ready for Amazon KDP publishing.
"""
        
        readme_file = target_folder / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
    
    # Create series-level README
    series_readme = f"""# Large Print Crossword Masters Series

## Series Overview
Complete collection of large print crossword puzzle books designed specifically for seniors.

**Brand**: Senior Puzzle Studio  
**Target Audience**: Seniors 55+  
**Difficulty**: Beginner-friendly  
**Format**: Large print for easy reading  

## Volumes in Series
"""
    
    for vol_num in sorted(volume_folders.keys()):
        series_readme += f"- **Volume {vol_num}**: Large Print Crossword Masters: Volume {vol_num}\n"
    
    series_readme += f"""
## Publishing Strategy
1. **Staggered Release**: Launch one volume every 2-3 weeks
2. **Series Branding**: Consistent cover design and messaging
3. **Cross-promotion**: Link between volumes for series discovery
4. **Customer Retention**: Build loyal customer base

## Marketing Focus
- Large print benefits for aging eyes
- Mental stimulation and cognitive health
- Quality puzzle design and professional presentation
- Series collection for ongoing entertainment

## Business Metrics
- **Cost per book**: ~$0.01 (Gemini AI generation)
- **Suggested retail**: $7.99 per volume
- **Profit margin**: 99%+ after platform fees
- **Market size**: Growing senior population

## Website
https://senior-puzzle-studio.carrd.co

## Generated with KindleMint AI
Ultra-low cost book generation system
Total series cost: ~$0.05 vs $25+ with traditional methods
"""
    
    series_readme_file = series_dir / "README.md"
    with open(series_readme_file, 'w') as f:
        f.write(series_readme)
    
    # Create upload instructions
    upload_instructions = f"""# Google Drive Upload Instructions

## Folder Structure Created
```
Large_Print_Crossword_Masters/
├── README.md (series overview)
├── Volume_01_Large_Print_Crossword_Masters_Volume_1/
├── Volume_02_Large_Print_Crossword_Masters_Volume_2/
├── Volume_03_Large_Print_Crossword_Masters_Volume_3/
├── Volume_04_Large_Print_Crossword_Masters_Volume_4/
└── Volume_05_Large_Print_Crossword_Masters_Volume_5/
```

## Upload Steps

### Method 1: Using Google Apps Script (Automated)
1. Use the `createBookFolder()` function you created
2. Call it for each volume folder
3. Upload files using the Drive web interface

### Method 2: Manual Upload
1. Open Google Drive: https://drive.google.com/
2. Navigate to your folder: https://drive.google.com/drive/folders/1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB
3. Drag and drop the entire `Large_Print_Crossword_Masters` folder

### Method 3: Google Drive Desktop
1. Copy the `Large_Print_Crossword_Masters` folder to your Google Drive desktop folder
2. Wait for sync to complete

## What's Ready
✅ {len(volume_folders)} volumes with correct numbering  
✅ Professional file organization  
✅ Complete metadata and publishing guides  
✅ Marketing content for each volume  
✅ Series-level documentation  

## Next Steps After Upload
1. Create covers using the design prompts
2. Upload first volume to Amazon KDP
3. Set up marketing campaigns
4. Plan additional series expansion

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    upload_file = organized_dir / "UPLOAD_INSTRUCTIONS.md"
    with open(upload_file, 'w') as f:
        f.write(upload_instructions)
    
    print("=" * 60)
    print("🎉 BOOKS ORGANIZED FOR GOOGLE DRIVE!")
    print("=" * 60)
    print(f"📁 Organized folder: {organized_dir}")
    print(f"📚 Series folder: {series_dir}")
    print(f"✅ Volumes ready: {len(volume_folders)}")
    print(f"📋 Upload instructions: {upload_file}")
    print("")
    print("🚀 Ready to upload to Google Drive!")
    print("📂 Upload the entire 'Large_Print_Crossword_Masters' folder")
    print("🔗 Target: https://drive.google.com/drive/folders/1qbTt7l7ooqEKgU2IiwPDKy0WwIgCEbuB")
    print("=" * 60)
    
    return organized_dir

if __name__ == "__main__":
    organize_books_for_upload()