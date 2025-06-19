#!/usr/bin/env python3
"""
Migration Script - Convert Legacy Structure to New Hierarchical Format
Migrates from flat output/generated_books to brand/series/volume structure
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.utils.asset_manager import AssetManager
from kindlemint.utils.logger import get_logger

def main():
    """Migrate legacy structure to new hierarchical format"""
    logger = get_logger('migration')
    
    logger.info("🔄 Starting migration to new hierarchical asset structure...")
    
    asset_manager = AssetManager()
    
    # Perform migration
    success = asset_manager.migrate_legacy_structure()
    
    if success:
        logger.info("✅ Migration completed successfully")
        
        # Display inventory
        inventory = asset_manager.get_asset_inventory()
        logger.info(f"📊 Asset Inventory:")
        logger.info(f"   Total Brands: {inventory['total_brands']}")
        logger.info(f"   Total Series: {inventory['total_series']}")
        logger.info(f"   Total Volumes: {inventory['total_volumes']}")
        
        for brand_name, brand_data in inventory['brands'].items():
            logger.info(f"   📁 {brand_name}")
            for series_name, series_data in brand_data['series'].items():
                logger.info(f"     📚 {series_name} ({series_data['volume_count']} volumes)")
                logger.info(f"       Volumes: {series_data['volumes']}")
    else:
        logger.error("❌ Migration failed or no legacy files found")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)