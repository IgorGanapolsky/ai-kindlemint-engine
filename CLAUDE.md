# Claude Memory

## Important Reminders

### Always Push Changes
**CRITICAL**: Always commit and push changes immediately after making them. Igor expects all fixes and updates to be pushed to the repository automatically.

### Workflow Commands
- Lint: `npm run lint` (check if available)
- Typecheck: `npm run typecheck` (check if available)
- Test: `npm test` (check if available)

### Repository Structure
- Main deployment script: `scripts/utilities/deploy_lambda.py`
- GitHub Actions workflows: `.github/workflows/`
- Lambda functions: `lambda/`
- Core application: `kindlemint/`

### Cover Design Policy
**NEVER generate covers automatically.** Always provide DALL-E prompts for Igor to use instead of creating cover images programmatically. Store all DALL-E prompts in checklist.md files for easy reference and reuse.

### KDP Categories Policy
**CRITICAL**: Amazon KDP allows exactly **3 categories** per book. Always use 3 categories to maximize discoverability. Use actual KDP category names from the interface, never hallucinate category paths.

### Accuracy Policy
**ABSOLUTE REQUIREMENT**: Only provide 100% factual, verified information. NEVER claim something exists or was completed unless actually verified. NEVER make excuses for incorrect information. Always verify file existence, tool outputs, and system state before making any claims.

## Claude Max Subscription Status

**CURRENT PLAN**: Claude Max ($20/month) - Includes unlimited Claude Code usage!

### Usage Guidelines
Since Claude Code is included in your Claude Max subscription:
- **No credit limits** - Use Claude Code freely without worrying about costs
- **No need to batch sessions** - Work whenever inspiration strikes
- **Full feature access** - All Claude Code capabilities available
- **Unlimited iterations** - Refine and perfect your code without cost concerns

### Development Best Practices
Now that cost isn't a factor, focus on:
- **Code quality** over session efficiency
- **Thorough testing** and experimentation
- **Comprehensive implementations** without rushing
- **Learning and exploration** of new approaches

## Hardcover Production Workflow

### Complete Hardcover Creation Process

**CRITICAL**: This is the proven workflow for creating KDP-ready hardcover editions. Follow these exact steps for all future volumes.

#### 1. Preparation Phase
```bash
# Ensure hardcover system is available
ls templates/hardcover/
ls scripts/hardcover/
```

Required components:
- `templates/hardcover/kdp_case_laminate/6x9_103pages_template.png` - KDP template
- `templates/hardcover/production_docs/book_config_template.json` - Configuration template
- `scripts/hardcover/create_hardcover_package.py` - Automated production script

#### 2. Configuration Setup
```bash
# Copy and customize book configuration
cp templates/hardcover/production_docs/book_config_template.json books/active_production/SERIES/VOLUME/hardcover_config.json
```

**Key configuration fields:**
- `title`, `subtitle`, `author`, `publisher`
- `pages` - Used for spine width calculation: `(pages × 0.0025) + 0.06`
- `cover_source` - Path to 1600×2560 source cover image
- `output_dir` - Target hardcover directory
- `pricing` - Hardcover should be 2-3x paperback price for optimal margins

#### 3. Automated Production
```bash
# Run complete hardcover package creation
python scripts/hardcover/create_hardcover_package.py books/active_production/SERIES/VOLUME/hardcover_config.json
```

**This script automatically creates:**
- Complete directory structure
- KDP metadata with hardcover-specific enhancements
- Production checklist with spine calculations
- Print-ready cover wrap design (13.996" × 10.417")
- PDF/X-1a export with CMYK color mode
- All quality control documentation

#### 4. Output Files Generated
```
books/active_production/SERIES/VOLUME/hardcover/
├── amazon_kdp_metadata.json          # KDP upload metadata
├── hardcover_production_checklist.md # Complete production guide
├── cover_wrap_design_brief.md         # Design specifications
├── hardcover_cover_wrap.pdf          # KDP-ready PDF/X-1a (UPLOAD THIS)
├── hardcover_cover_wrap_final.png    # Final artwork
├── hardcover_cover_wrap_preview.png  # With template overlay
└── cover_source_1600x2560.jpg       # Source cover copy

# Scripts and templates are stored separately:
scripts/hardcover/                     # Production scripts
templates/hardcover/                   # KDP templates and configs
```

#### 5. KDP Requirements Verification
**Automated quality checks ensure:**
- ✅ Exact template dimensions (13.996" × 10.417")
- ✅ CMYK color mode for professional printing
- ✅ PDF/X-1a format compliance
- ✅ File size under 650 MB KDP limit
- ✅ Proper spine text margins (0.125" from edges)
- ✅ Barcode placeholder area (2" × 1.2")

#### 6. Revenue Optimization
**Hardcover pricing strategy:**
- Printing cost: ~$6.50 for 6×9, 103 pages
- Target price: $19.99 - $24.99 (2-3x paperback)
- Royalty: $3.50 - $8.50 per book
- Market: Premium gift segment, collectors

#### 7. Commit and Deploy
```bash
# Always commit hardcover packages
git add books/active_production/SERIES/VOLUME/hardcover/
git commit -m "feat: complete hardcover production for TITLE VOLUME"
git push
```

### Spine Width Reference
- 50 pages: 0.185 inches
- 75 pages: 0.248 inches  
- 100 pages: 0.310 inches
- 103 pages: 0.318 inches (Large Print Crossword Masters Vol 1)
- 125 pages: 0.373 inches
- 150 pages: 0.435 inches

### Template Library
- `6x9_103pages_template.png` - Tested for Large Print Crossword Masters
- Additional templates added as needed for different page counts
- KDP provides templates for: 5×8, 5.5×8.5, 6×9, 6.14×9.21 trim sizes

### Troubleshooting
- **Font loading errors**: Script includes fallback font handling
- **CMYK conversion issues**: Automatic RGB→CMYK conversion included  
- **File size limits**: Compression automatically optimized for KDP
- **Template misalignment**: 30% opacity guide layer for precise positioning

### Future Volume Creation
**For Volume 2, 3, etc.:**
1. Copy `hardcover_config.json` template
2. Update title, subtitle, volume number, cover source path
3. Run `python scripts/hardcover/create_hardcover_package.py CONFIG_FILE`
4. Commit and push results

**Estimated time per volume:** 10-15 minutes for complete hardcover package generation.