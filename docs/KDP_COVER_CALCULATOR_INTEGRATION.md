# KDP Cover Calculator Integration Guide

## Overview

This guide explains how to integrate KDP's official cover calculator into your book production workflow to ensure accurate cover dimensions for all books.

## Key Components

### 1. Official KDP Cover Calculator
- **URL**: https://kdp.amazon.com/cover-calculator
- **Purpose**: Calculate exact dimensions based on your book specifications
- **Always use this for final verification**

### 2. Python Calculator Script
- **Location**: `/scripts/kdp_cover_calculator.py`
- **Purpose**: Automate dimension calculations and DALL-E prompt generation
- **Usage**: `python scripts/kdp_cover_calculator.py`

### 3. Dimension Reference
- **Location**: `/books/active_production/FULL_COVER_DIMENSIONS_REFERENCE.md`
- **Purpose**: Quick reference for current book dimensions
- **Updated**: With actual page counts from PDFs

## Workflow Integration

### Step 1: Determine Actual Page Count
```bash
# Use the page count checker script
python scripts/check_page_counts.py
```

### Step 2: Calculate Dimensions
```python
from scripts.kdp_cover_calculator import KDPCoverCalculator

calculator = KDPCoverCalculator()

# For paperback (8.5x11)
pb_dims = calculator.calculate_full_cover_dimensions("8.5x11", 104, "paperback")

# For hardcover (6x9)
hc_dims = calculator.calculate_full_cover_dimensions("6x9", 104, "hardcover")
```

### Step 3: Verify with KDP Official Calculator
1. Navigate to https://kdp.amazon.com/cover-calculator
2. Enter your specifications:
   - Binding type
   - Interior type: Black & White
   - Paper type: White (for paperback)
   - Page count: From your PDF
   - Trim size: 8.5×11 (paperback) or 6×9 (hardcover)
3. Compare results with Python calculator

### Step 4: Download Official Template
1. Click "Download Template" in KDP calculator
2. Save with naming convention:
   - Paperback: `kdp_template_8.5x11_[PAGES]pages.png`
   - Hardcover: `kdp_template_6x9_[PAGES]pages.png`
3. Store in `/templates/kdp_official/`

### Step 5: Generate DALL-E Prompt
```python
# Generate accurate DALL-E prompt
prompt = calculator.generate_dall_e_prompt(
    "Large Print Crossword Masters",
    1,  # volume number
    dims
)
```

## Template Organization

```
templates/
├── kdp_official/
│   ├── paperback/
│   │   ├── kdp_template_8.5x11_104pages.png
│   │   ├── kdp_template_8.5x11_112pages.png
│   │   ├── kdp_template_8.5x11_107pages.png
│   │   └── kdp_template_8.5x11_156pages.png
│   └── hardcover/
│       ├── kdp_template_6x9_104pages.png
│       ├── kdp_template_6x9_112pages.png
│       ├── kdp_template_6x9_107pages.png
│       └── kdp_template_6x9_156pages.png
```

## Critical Reminders

### Format Differences
- **Paperback**: 8.5 × 11 inches
- **Hardcover**: 6 × 9 inches
- **NEVER mix these up!**

### Spine Width Formulas
- **Paperback**: `page_count × 0.0025`
- **Hardcover**: `(page_count × 0.0025) + 0.06`

### Full Cover Calculation
```
Full Width = (Trim Width × 2) + Spine Width + 0.25"
Full Height = Trim Height + 0.25"
```

## Automation Scripts

### Generate All Dimensions Report
```bash
# Run the calculator to generate a complete report
python scripts/kdp_cover_calculator.py

# Output: kdp_cover_dimensions_report.json
```

### Update Cover Checklists
```bash
# Update all cover generation checklists with correct dimensions
python scripts/update_cover_checklists.py
```

### Batch Template Download
```bash
# Script to help download all needed templates
python scripts/kdp_template_downloader.py
```

## Quality Assurance Checklist

Before finalizing any cover:

- [ ] Actual page count verified from PDF
- [ ] Dimensions calculated with both Python script and KDP calculator
- [ ] Results match within 0.001" tolerance
- [ ] Official KDP template downloaded
- [ ] DALL-E prompt includes full wraparound dimensions
- [ ] Cover checklist updated with correct values
- [ ] Test upload to KDP preview

## Common Issues and Solutions

### Issue: Dimension Mismatch
**Solution**: Always use actual PDF page count, not estimated

### Issue: Wrong Trim Size
**Solution**: Remember paperback = 8.5×11, hardcover = 6×9

### Issue: Spine Text Doesn't Fit
**Solution**: Recalculate spine width, adjust font size

### Issue: KDP Rejects Cover
**Solution**: Check bleed, ensure CMYK color space, verify dimensions

## Support Resources

### KDP Help
- Cover Guidelines: https://kdp.amazon.com/help/topic/G200735480
- File Creation Guide: https://kdp.amazon.com/help/topic/G202145400
- Common Issues: https://kdp.amazon.com/help/topic/G200952510

### Internal Tools
- Calculator: `/scripts/kdp_cover_calculator.py`
- Page Counter: `/scripts/check_page_counts.py`
- Dimension Reference: `/books/active_production/FULL_COVER_DIMENSIONS_REFERENCE.md`

## Version History
- 2025-06-27: Created integration guide
- 2025-06-27: Added Python calculator script
- 2025-06-27: Updated for correct trim sizes (PB: 8.5×11, HC: 6×9)
