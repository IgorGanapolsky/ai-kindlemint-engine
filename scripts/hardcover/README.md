# Hardcover Production System

## Overview
Automated system for creating KDP-ready hardcover editions from existing paperback books. Generates complete production packages including cover wraps, metadata, and quality control documentation.

## Quick Start

### 1. Create Book Configuration
```bash
cp templates/hardcover/production_docs/book_config_template.json my_book_config.json
# Edit configuration with your book details
```

### 2. Run Production
```bash
python scripts/hardcover/create_hardcover_package.py my_book_config.json
```

### 3. Upload to KDP
Use the generated `hardcover_cover_wrap.pdf` file for KDP upload.

## System Components

### Templates
- `templates/hardcover/kdp_case_laminate/` - KDP template files
- `templates/hardcover/production_docs/` - Configuration templates

### Scripts
- `create_hardcover_package.py` - Main production script
- Automatic spine width calculation: `(pages × 0.0025) + 0.06`
- PDF/X-1a export with CMYK color mode

### Output Files
- `hardcover_cover_wrap.pdf` - KDP-ready cover wrap
- `amazon_kdp_metadata.json` - Upload metadata
- `hardcover_production_checklist.md` - Quality control guide

## Supported Formats
- **Trim Size**: 6" × 9" (standard)
- **Binding**: Case-Laminate (KDP's only hardcover option)
- **Page Range**: 24-550 pages
- **Color**: Black & White (cost-optimized)

## Pricing Strategy
- **Target**: 2-3x paperback price
- **Margin**: Higher per-unit profit despite printing costs
- **Market**: Premium gift segment, collectors

## Quality Standards
- ✅ Exact KDP template dimensions
- ✅ CMYK color mode
- ✅ PDF/X-1a compliance
- ✅ <650 MB file size
- ✅ Proper spine margins

## Revenue Impact
Hardcover editions typically generate 150-200% higher revenue per unit while targeting the premium gift market segment.
