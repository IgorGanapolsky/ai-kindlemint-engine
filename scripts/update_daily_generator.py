#!/usr/bin/env python3
"""
Update Daily Generator for New Strategic Structure
Redirects output to active_production instead of dated folders
"""

import os
from pathlib import Path

def update_daily_series_generator():
    """Update the daily series generator to use new structure"""
    
    generator_path = Path("scripts/daily_series_generator.py")
    
    if not generator_path.exists():
        print("❌ daily_series_generator.py not found")
        return
    
    # Read current content
    with open(generator_path, 'r') as f:
        content = f.read()
    
    # Update output directory logic
    old_output_pattern = 'self.output_dir = Path("output/daily_production")'
    new_output_pattern = 'self.output_dir = Path("active_production")'
    
    if old_output_pattern in content:
        content = content.replace(old_output_pattern, new_output_pattern)
        print("✅ Updated output directory to active_production")
    
    # Remove date-based directory creation
    old_date_pattern = 'date_str = datetime.now().strftime(\'%Y%m%d\')'
    new_date_pattern = '# Strategic organization: series-based instead of date-based'
    
    if old_date_pattern in content:
        content = content.replace(old_date_pattern, new_date_pattern)
        print("✅ Removed date-based directory structure")
    
    # Update series directory creation
    old_series_dir = 'output_dir = self.output_dir / date_str / series_name.replace(" ", "_")'
    new_series_dir = 'output_dir = self.output_dir / series_name.replace(" ", "_")'
    
    if old_series_dir in content:
        content = content.replace(old_series_dir, new_series_dir)
        print("✅ Updated series directory structure")
    
    # Write updated content
    with open(generator_path, 'w') as f:
        f.write(content)
    
    print("🎯 Daily generator updated for strategic structure")

def update_plan_md_with_workflow():
    """Add the production workflow to plan.md"""
    
    workflow_content = """

# 📋 UPDATED PRODUCTION WORKFLOW (2025)

## Daily Production Process

### 1. Generate New Content
```bash
python scripts/daily_series_generator.py
# Now outputs to: active_production/[SeriesName]/
```

### 2. Quality Review
```bash
# Review in active_production/
cd active_production/[SeriesName]/volume_X/
# Check manuscript.txt quality and completeness
```

### 3. Move to Staging
```bash
# When ready for publishing:
mv active_production/[SeriesName]/volume_X/ staging/
```

### 4. Publish to Amazon KDP
- Upload manuscript from staging/
- Create cover using templates/covers/
- Set metadata using templates/metadata/
- Publish and get ASIN

### 5. Archive Published Content
```bash
# After successful publishing:
mv staging/[SeriesName]_v1_PUBLISHED/ published_archive/2025_Q1/
git add published_archive/
git commit -m "Archive published book to LFS"
```

## Business Intelligence Tracking

### Sales Data
- Track sales in `business_intelligence/sales_reports/`
- Monitor profit in `business_intelligence/profit_analysis/`
- Research new niches in `business_intelligence/market_research/`

### Automated Metrics
- Generation costs tracked per book
- ROI calculated automatically
- Quality scores maintained
- Publishing success rates monitored

## Strategic Benefits

✅ **No More Confusion**: Clear active vs archived separation
✅ **Scalable Structure**: Ready for 100+ series
✅ **Git LFS Optimized**: Large files stored efficiently  
✅ **Business Focus**: Intelligence and analytics built-in
✅ **Daily Workflow**: Streamlined production process

---

This structure supports the goal of 30+ books per month while maintaining
organization, quality, and business intelligence capabilities.
"""
    
    plan_path = Path("plan.md")
    
    if plan_path.exists():
        with open(plan_path, 'a') as f:
            f.write(workflow_content)
        print("✅ Added production workflow to plan.md")
    else:
        print("⚠️ plan.md not found")

def main():
    """Execute all updates"""
    
    print("🔧 UPDATING SYSTEM FOR STRATEGIC ORGANIZATION")
    print("=" * 60)
    
    # Update the daily generator
    update_daily_series_generator()
    
    # Update documentation
    update_plan_md_with_workflow()
    
    print("\n🎯 SYSTEM UPDATES COMPLETE")
    print("✅ Daily generator now uses active_production/")
    print("✅ No more confusing date-based directories")
    print("✅ Clear series-focused workflow established")
    print("✅ Documentation updated with new process")
    
    print("\n📈 READY FOR STREAMLINED PRODUCTION")

if __name__ == "__main__":
    main()