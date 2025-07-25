#!/usr/bin/env python3
"""
Generate cover generation checklists for all book volumes
Using KDP official specifications and actual page counts
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from scripts.kdp_cover_calculator import KDPCoverCalculator

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    """Generate Checklist"""
def generate_checklist(book_info, dimensions):
    """Generate a cover checklist from template with book-specific information"""

    calculator = KDPCoverCalculator()
    dalle_prompt = calculator.generate_dall_e_prompt(
        book_info["title"], book_info["volume"], dimensions
    )

    template = """# {format_type} Cover Generation Checklist

## Book Information
- **Title**: {title}
- **Volume**: {volume}
- **Format**: {format_type} ({trim_size})
- **Page Count**: {page_count} pages
- **Spine Width**: {spine_width} inches (calculated)

## Pre-Generation Requirements
- [ ] Verify book dimensions ({trim_size})
- [ ] Confirm page count for spine width calculation
- [ ] Check KDP template requirements for {format_type}
- [ ] Ensure all fonts are embedded or outlined
- [ ] Verify color profile (CMYK for print)

## DALL-E Prompt for Cover

### Suggested Prompt Template
```
{dalle_prompt}
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

    return template.format(
        format_type=book_info["format_type"],
        title=book_info["title"],
        volume=book_info["volume"],
        trim_size=dimensions["trim_size"].replace("x", " x "),
        page_count=book_info["page_count"],
        spine_width=dimensions["spine_width"],
        special_feature=book_info.get("special_feature", "LARGE PRINT"),
        full_width=dimensions["full_width"],
        full_height=dimensions["full_height"],
        dalle_prompt=dalle_prompt,
    )


    """Main"""
def main():
    """Generate cover checklists for all book volumes"""

    parser = argparse.ArgumentParser(
        description="Generate cover checklists for book volumes"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force regeneration of existing checklists",
    )
    args = parser.parse_args()

    calculator = KDPCoverCalculator()

    # Define book series information with actual page counts
    book_series = {
        "Large_Print_Crossword_Masters": {
            "title": "Large Print Crossword Masters",
            "special_feature": "LARGE PRINT",
            "paperback_trim": "8.5x11",
            "hardcover_trim": "6x9",
            "volumes": {
                1: {"pages": 104},
                2: {"pages": 112},
                3: {"pages": 107},
                4: {"pages": 156},
            },
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

                # Skip if already exists (unless force flag is set)
                if checklist_path.exists() and not args.force:
                    print(f"✓ Checklist already exists: {checklist_path}")
                    continue

                # Determine trim size based on format
                if format_type == "paperback":
                    trim_size = series_info["paperback_trim"]
                else:  # hardcover
                    trim_size = series_info["hardcover_trim"]

                # Calculate dimensions using KDP calculator
                dimensions = calculator.calculate_full_cover_dimensions(
                    trim_size, volume_info["pages"], format_type
                )

                # Prepare book information
                book_info = {
                    "title": series_info["title"],
                    "volume": volume_num,
                    "format_type": format_type.capitalize(),
                    "page_count": volume_info["pages"],
                    "special_feature": series_info["special_feature"],
                }

                # Generate and save checklist
                checklist_content = generate_checklist(book_info, dimensions)

                with open(checklist_path, "w") as f:
                    f.write(checklist_content)

                print(f"✅ Generated: {checklist_path}")
                generated_count += 1

    print(f"\n📋 Generated {generated_count} cover checklists")
    print(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if generated_count == 0 and not args.force:
        print("\n💡 Tip: Use --force flag to regenerate existing checklists")
    else:
        print("\n✅ All checklists now use correct KDP dimensions!")
        print("📐 Remember: Paperback = 8.5×11, Hardcover = 6×9")


if __name__ == "__main__":
    main()
