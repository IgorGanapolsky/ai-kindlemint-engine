#!/usr/bin/env python3
"""
Generate cover generation checklists for all book volumes
"""

import os
from pathlib import Path
from datetime import datetime

def calculate_spine_width(page_count, format_type="hardcover"):
    """Calculate spine width based on page count and format"""
    if format_type == "hardcover":
        # Hardcover uses thicker paper, approximately 0.003" per page
        return round(page_count * 0.003 + 0.1, 3)  # 0.1" for board thickness
    else:
        # Paperback uses thinner paper, approximately 0.0025" per page
        return round(page_count * 0.0025, 3)

def generate_checklist(book_info):
    """Generate a cover checklist from template with book-specific information"""
    
    template = """# {format_type} Cover Generation Checklist

## Book Information
- **Title**: {title}
- **Volume**: {volume}
- **Format**: {format_type} ({dimensions})
- **Page Count**: {page_count} pages
- **Spine Width**: {spine_width} inches (calculated)

## Pre-Generation Requirements
- [ ] Verify book dimensions ({dimensions})
- [ ] Confirm page count for spine width calculation
- [ ] Check KDP template requirements for {format_type}
- [ ] Ensure all fonts are embedded or outlined
- [ ] Verify color profile (CMYK for print)

## DALL-E Prompt for Cover

### Suggested Prompt Template
```
Create a professional FULL WRAP book cover for "{title} Volume {volume}" - a large print crossword puzzle book. 
CRITICAL: This is a FULL COVER (front + spine + back) for {format_type} binding.
Full cover dimensions: {full_width}" wide x {full_height}" tall (includes 0.125" bleed)
- Front cover area: 8.5" x 11" (right side)
- Spine area: {spine_width}" wide (center)
- Back cover area: 8.5" x 11" (left side)

Design elements:
- Clean, modern design suitable for seniors
- Large, bold title text reading "{title}" on FRONT cover
- Prominent "Volume {volume}" indicator on FRONT cover
- "LARGE PRINT" badge or banner on FRONT cover
- Spine text: Title and Volume number (rotated for bookshelf display)
- Back cover: Book description area and barcode space (2" x 1.2" white box)
- Subtle crossword grid pattern in background
- Color scheme: [Suggest calming blues, greens, or warm colors]
- Professional typography with high contrast
- Minimalist style that prints well
Style: Professional, clean, accessible, senior-friendly
```

### Prompt Customization Notes
- [ ] Adjust color scheme for each volume to differentiate
- [ ] Consider seasonal themes if applicable
- [ ] Ensure high contrast for visibility
- [ ] Avoid overly complex backgrounds
- [ ] Test prompt variations for best results

## Cover Design Elements

### Front Cover
- [ ] Title clearly visible and properly sized
- [ ] Volume number prominently displayed
- [ ] "{special_feature}" designation visible
- [ ] Professional typography (no pixelation)
- [ ] Appropriate margins (0.125" minimum)
- [ ] No critical elements in bleed area
- [ ] Resolution: 300 DPI minimum

### Back Cover
- [ ] Book description included
- [ ] Barcode placeholder area (2" x 1.2")
- [ ] Publisher information (if applicable)
- [ ] Price (optional for KDP)
- [ ] Category/genre indication
- [ ] Professional layout alignment

### Spine
- [ ] Title readable when book is shelved
- [ ] Volume number on spine
- [ ] Text centered and properly oriented
- [ ] Sufficient margins (0.0625" minimum)
- [ ] Font size appropriate for spine width

## Technical Specifications
- [ ] Full cover dimensions: {full_width}" x {full_height}" (includes bleed)
- [ ] Bleed: 0.125" on all sides
- [ ] Safe zone: 0.25" from trim edge
- [ ] File format: PDF (PDF/X-1a:2001 preferred)
- [ ] Color space: CMYK
- [ ] Fonts: Embedded or converted to outlines
- [ ] Resolution: 300 DPI
- [ ] File size: Under 650MB

## Quality Checks
- [ ] No low-resolution images
- [ ] No transparency issues
- [ ] No missing fonts warnings
- [ ] Text is legible at print size
- [ ] Colors are print-safe (no RGB)
- [ ] Spine text fits within spine width
- [ ] Barcode area is white/light colored

## KDP Compliance
- [ ] Cover meets KDP content guidelines
- [ ] No copyrighted material used without permission
- [ ] No misleading content
- [ ] Appropriate for target audience
- [ ] No promotional content (websites, emails)
- [ ] ISBN placement correct (if using)

## File Preparation
- [ ] Cover saved as high-quality PDF
- [ ] Backup saved in editable format (.ai, .psd, .indd)
- [ ] Test print performed (if possible)
- [ ] File named correctly: cover.pdf
- [ ] Metadata cleaned (no personal info)

## Final Validation
- [ ] Upload preview in KDP Cover Creator
- [ ] Check 3D preview for spine alignment
- [ ] Verify all text is readable
- [ ] Confirm trim lines are correct
- [ ] Review for any printing artifacts

## Post-Generation
- [ ] Archive source files
- [ ] Document any special settings used
- [ ] Note any deviations from standard
- [ ] Save color swatches/palette used
- [ ] Create thumbnail for catalog use

## Sign-off
- **Generated Date**: _______________
- **Generated By**: _______________
- **Quality Check By**: _______________
- **Approved Date**: _______________

## Notes
_Add any specific notes about this cover generation below:_

---

### Common Issues to Avoid
1. **Spine text too large**: Calculate based on page count
2. **Missing bleed**: Always include 0.125" bleed
3. **RGB colors**: Convert all to CMYK
4. **Font issues**: Embed or outline all fonts
5. **Low resolution**: Maintain 300 DPI throughout

### KDP Resources
- [KDP Cover Guidelines](https://kdp.amazon.com/help/topic/G201953020)
- [Cover Calculator](https://kdp.amazon.com/cover-calculator)
- [Template Generator](https://kdp.amazon.com/template-generator)"""
    
    # Calculate full cover dimensions (includes spine and bleed)
    width, height = map(float, book_info['dimensions'].replace('"', '').split(' x '))
    full_width = round((width * 2) + book_info['spine_width'] + 0.25, 3)  # Front + back + spine + bleed
    full_height = round(height + 0.25, 3)  # Height + bleed
    
    return template.format(
        format_type=book_info['format_type'],
        title=book_info['title'],
        volume=book_info['volume'],
        dimensions=book_info['dimensions'],
        page_count=book_info['page_count'],
        spine_width=book_info['spine_width'],
        special_feature=book_info.get('special_feature', 'LARGE PRINT'),
        full_width=full_width,
        full_height=full_height
    )

def main():
    """Generate cover checklists for all book volumes"""
    
    # Define book series information
    book_series = {
        "Large_Print_Crossword_Masters": {
            "title": "Large Print Crossword Masters",
            "special_feature": "LARGE PRINT",
            "dimensions": "8.5 x 11",
            "volumes": {
                1: {"pages": 105},
                2: {"pages": 120},
                3: {"pages": 105},
                4: {"pages": 110}
            }
        }
    }
    
    generated_count = 0
    
    for series_dir, series_info in book_series.items():
        series_path = Path(f"books/active_production/{series_dir}")
        
        if not series_path.exists():
            print(f"⚠️  Series directory not found: {series_path}")
            continue
            
        for volume_num, volume_info in series_info["volumes"].items():
            volume_path = series_path / f"volume_{volume_num}"
            
            if not volume_path.exists():
                print(f"⚠️  Volume directory not found: {volume_path}")
                continue
            
            # Generate for both hardcover and paperback
            for format_type in ["hardcover", "paperback"]:
                format_path = volume_path / format_type
                
                if not format_path.exists():
                    print(f"⚠️  Format directory not found: {format_path}")
                    continue
                
                checklist_path = format_path / "cover_generation_checklist.md"
                
                # Skip if already exists
                if checklist_path.exists():
                    print(f"✓ Checklist already exists: {checklist_path}")
                    continue
                
                # Prepare book information
                book_info = {
                    "title": series_info["title"],
                    "volume": volume_num,
                    "format_type": format_type.capitalize(),
                    "dimensions": series_info["dimensions"],
                    "page_count": volume_info["pages"],
                    "spine_width": calculate_spine_width(volume_info["pages"], format_type),
                    "special_feature": series_info["special_feature"]
                }
                
                # Generate and save checklist
                checklist_content = generate_checklist(book_info)
                
                with open(checklist_path, 'w') as f:
                    f.write(checklist_content)
                
                print(f"✅ Generated: {checklist_path}")
                generated_count += 1
    
    print(f"\n📋 Generated {generated_count} cover checklists")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()