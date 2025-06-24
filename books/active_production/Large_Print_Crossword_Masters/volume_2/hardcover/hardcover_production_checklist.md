# Hardcover Production Checklist - Volume 2

## 📋 Pre-Production Requirements
- [ ] Source cover image ready (1600×2560 PNG/JPG)
- [ ] Interior PDF finalized (110 pages)
- [ ] Spine width calculated: 0.335 inches
- [ ] KDP template for 6×9, 110 pages ready

## 🎨 Cover Wrap Creation
1. [ ] Run hardcover production script:
   ```bash
   python scripts/hardcover/create_hardcover_package.py books/active_production/Large_Print_Crossword_Masters/volume_2_proper/hardcover_config.json
   ```

2. [ ] Verify generated files:
   - [ ] hardcover_cover_wrap.pdf (PDF/X-1a format)
   - [ ] hardcover_cover_wrap_final.png 
   - [ ] hardcover_cover_wrap_preview.png (with template overlay)
   - [ ] amazon_kdp_metadata.json
   - [ ] cover_wrap_design_brief.md

## ✅ Quality Checks
- [ ] Cover wrap dimensions: 13.996" × 10.417" (exact)
- [ ] Spine text margins: 0.125" from edges
- [ ] Barcode area: 2" × 1.2" on back cover
- [ ] Color mode: CMYK
- [ ] PDF format: PDF/X-1a
- [ ] File size: Under 650 MB

## 📤 KDP Upload Process
1. [ ] Log into KDP Dashboard
2. [ ] Select "Create Hardcover"
3. [ ] Book details:
   - Title: Large Print Crossword Masters
   - Subtitle: 50 New Crossword Puzzles - Easy to Challenging - Volume 2
   - Author: Crossword Masters Publishing
   - Series: Large Print Crossword Masters (Book 2)
   
4. [ ] Content upload:
   - Interior: Use paperback PDF
   - Cover: hardcover_cover_wrap.pdf
   
5. [ ] Categories (3 maximum):
   - Books > Humor & Entertainment > Puzzles & Games > Crossword Puzzles
   - Books > Health, Fitness & Dieting > Aging  
   - Books > Self-Help > Memory Improvement

6. [ ] Pricing:
   - List price: $22.99
   - Markets: All available territories

## 🚀 Post-Upload
- [ ] Order proof copy
- [ ] Review physical book quality
- [ ] Check spine alignment
- [ ] Verify cover print quality
- [ ] Approve for publication

## 💰 Revenue Projections
- Printing cost: ~$6.75
- List price: $22.99
- Expected royalty: ~$6.48 per book (28%)
- Target: Premium gift market