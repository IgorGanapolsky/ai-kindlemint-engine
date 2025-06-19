#!/usr/bin/env python3
"""
Generate Publishing Report
Creates comprehensive report of publishing operations
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.utils.asset_manager import AssetManager

def main():
    """Generate comprehensive publishing report"""
    logger = get_logger('publishing_report')
    
    logger.info("📊 Generating publishing report...")
    
    # Create reports directory
    reports_dir = Path("output/publishing_reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Get asset inventory
    asset_manager = AssetManager()
    inventory = asset_manager.get_asset_inventory()
    
    # Generate report
    report = {
        "report_timestamp": datetime.now().isoformat(),
        "report_type": "autonomous_publishing",
        "asset_inventory": inventory,
        "system_status": {
            "github_lfs_enabled": check_lfs_status(),
            "asset_structure": "hierarchical",
            "migration_status": "completed"
        },
        "recommendations": generate_recommendations(inventory)
    }
    
    # Save report
    report_filename = f"publishing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = reports_dir / report_filename
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"✅ Publishing report saved: {report_path}")
    
    # Display summary
    logger.info("📊 Publishing Report Summary:")
    logger.info(f"   Total Brands: {inventory['total_brands']}")
    logger.info(f"   Total Series: {inventory['total_series']}")
    logger.info(f"   Total Volumes: {inventory['total_volumes']}")
    
    for brand_name, brand_data in inventory['brands'].items():
        logger.info(f"   📁 {brand_name}")
        for series_name, series_data in brand_data['series'].items():
            logger.info(f"     📚 {series_name}: {series_data['volume_count']} volumes")
    
    return True

def check_lfs_status():
    """Check if Git LFS is properly configured"""
    try:
        gitattributes_path = Path(".gitattributes")
        if gitattributes_path.exists():
            content = gitattributes_path.read_text()
            return "filter=lfs" in content
        return False
    except:
        return False

def generate_recommendations(inventory):
    """Generate actionable recommendations based on inventory"""
    recommendations = []
    
    if inventory['total_volumes'] == 0:
        recommendations.append("No volumes found - consider generating content")
    elif inventory['total_volumes'] < 5:
        recommendations.append("Consider expanding series to 5+ volumes for better market presence")
    
    if inventory['total_series'] == 1:
        recommendations.append("Consider creating additional series to diversify content portfolio")
    
    if inventory['total_brands'] == 1:
        recommendations.append("Consider establishing multiple brands for different target markets")
    
    return recommendations

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)