# KDP Hardcover Template Generation Guide

## Template Requirements for Each Book

### Step 1: Calculate Page Count and Spine Width
For each book, you need:
1. **Exact page count** from the interior PDF
2. **Spine width calculation**: `(pages × 0.0025) + 0.06`
3. **Interior trim size**: Usually 6×9 inches

### Step 2: Download KDP Template
1. Go to [KDP Cover Calculator](https://kdp.amazon.com/en_US/cover-calculator)
2. Enter book information:
   - **Binding type**: Hardcover
   - **Interior type**: Black & white
   - **Paper type**: White paper
   - **Page count**: [Your book's page count]
   - **Trim size**: 6 x 9 in

3. Click "Calculate dimensions"
4. Click "Download Template"

### Step 3: Save Template with Naming Convention
Save templates as: `templates/hardcover/kdp_case_laminate/6x9_[PAGES]pages_template.png`

Examples:
- `6x9_103pages_template.png` (Volume 1 - already exists)
- `6x9_110pages_template.png` (Volumes 2 & 3 - need to download)
- `6x9_120pages_template.png` (Future volumes)

## Template Dimensions Reference

### 6×9 Book Dimensions (at 300 DPI):
| Pages | Spine Width | Template Width | Template Height | File Name |
|-------|-------------|----------------|-----------------|-----------|
| 50    | 0.185"      | 13.621"        | 10.417"         | 6x9_50pages_template.png |
| 75    | 0.248"      | 13.746"        | 10.417"         | 6x9_75pages_template.png |
| 100   | 0.310"      | 13.870"        | 10.417"         | 6x9_100pages_template.png |
| 103   | 0.318"      | 13.886"        | 10.417"         | 6x9_103pages_template.png ✅ |
| 110   | 0.335"      | 13.920"        | 10.417"         | 6x9_110pages_template.png ❌ |
| 120   | 0.360"      | 13.970"        | 10.417"         | 6x9_120pages_template.png |
| 150   | 0.435"      | 14.120"        | 10.417"         | 6x9_150pages_template.png |

## Current Book Status

### Large Print Crossword Masters
- **Volume 1**: 103 pages - ✅ Template exists
- **Volume 2**: 110 pages - ❌ Need template
- **Volume 3**: 110 pages - ❌ Need template

### Required Actions:
1. Download template for 110-page books from KDP
2. Save as `6x9_110pages_template.png`
3. Update hardcover configs for each volume

## How to Use Templates

### For Each Book Volume:
1. Copy `book_config_template.json` to the book's directory
2. Update with book-specific information:
   - Title and subtitle
   - Exact page count
   - Cover source image path
   - Output directory path

3. Run the hardcover script:
```bash
python scripts/hardcover/create_hardcover_package.py books/active_production/SERIES/VOLUME/hardcover_config.json
```

### Template Usage in Production:
- The script automatically selects the correct template based on page count
- Templates are overlaid at 30% opacity for precise positioning
- Cover designers can see exact placement of spine, barcode area, and bleed

## Quality Checklist
- [ ] Template dimensions match KDP requirements exactly
- [ ] Template saved at high resolution (300 DPI)
- [ ] File named with exact page count
- [ ] Template includes all guide marks (bleed, spine, barcode area)

## Notes
- KDP provides templates for standard trim sizes: 5×8, 5.5×8.5, 6×9, 6.14×9.21
- Always download fresh templates when page count changes
- Templates are specific to binding type (case laminate hardcover)