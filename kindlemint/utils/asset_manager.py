#!/usr/bin/env python3
"""
Asset Manager - Professional File Organization System
Manages the hierarchical brand/series/volume directory structure
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class AssetManager:
    """Professional asset management for KindleMint publishing empire"""
    
    def __init__(self, base_output_dir: str = "output"):
        self.base_dir = Path(base_output_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def get_brand_series_path(self, brand_name: str, series_name: str) -> Path:
        """Get the standardized path for a brand/series combination"""
        # Sanitize names for filesystem
        clean_brand = self._sanitize_name(brand_name)
        clean_series = self._sanitize_name(series_name)
        
        return self.base_dir / clean_brand / clean_series
    
    def get_volume_path(self, brand_name: str, series_name: str, volume_num: int) -> Path:
        """Get the full path for a specific volume"""
        series_path = self.get_brand_series_path(brand_name, series_name)
        return series_path / f"volume_{volume_num}"
    
    def create_volume_directory(self, brand_name: str, series_name: str, volume_num: int) -> Path:
        """Create directory structure for a new volume"""
        volume_path = self.get_volume_path(brand_name, series_name, volume_num)
        volume_path.mkdir(parents=True, exist_ok=True)
        return volume_path
    
    def store_volume_assets(self, brand_name: str, series_name: str, volume_num: int, 
                           assets: Dict[str, str]) -> Dict[str, Path]:
        """Store all assets for a volume in the correct locations
        
        Args:
            brand_name: Brand name (e.g., "Senior Puzzle Studio")
            series_name: Series name (e.g., "Large Print Crossword Masters")
            volume_num: Volume number
            assets: Dict mapping asset types to file paths
                   Expected keys: 'cover', 'manuscript_pdf', 'cover_prompt', 'metadata', etc.
        
        Returns:
            Dict mapping asset types to their new stored paths
        """
        volume_path = self.create_volume_directory(brand_name, series_name, volume_num)
        stored_paths = {}
        
        # Standard asset mapping
        asset_mapping = {
            'cover': 'cover.png',
            'manuscript_pdf': 'manuscript.pdf', 
            'cover_prompt': 'cover_prompt.txt',
            'metadata': 'metadata.json',
            'back_cover_content': 'back_cover_content.txt',
            'marketing_content': 'marketing_content.txt',
            'kdp_guide': 'KDP_PUBLISHING_GUIDE.txt',
            'manuscript_txt': 'manuscript.txt'
        }
        
        for asset_type, source_path in assets.items():
            if not source_path or not Path(source_path).exists():
                continue
                
            # Determine target filename
            target_filename = asset_mapping.get(asset_type, f"{asset_type}.txt")
            target_path = volume_path / target_filename
            
            # Copy the file
            shutil.copy2(source_path, target_path)
            stored_paths[asset_type] = target_path
            
        return stored_paths
    
    def get_volume_assets(self, brand_name: str, series_name: str, volume_num: int) -> Dict[str, Path]:
        """Get all assets for a volume"""
        volume_path = self.get_volume_path(brand_name, series_name, volume_num)
        
        if not volume_path.exists():
            return {}
        
        assets = {}
        
        # Standard asset files
        asset_files = {
            'cover': 'cover.png',
            'manuscript_pdf': 'manuscript.pdf',
            'cover_prompt': 'cover_prompt.txt', 
            'metadata': 'metadata.json',
            'back_cover_content': 'back_cover_content.txt',
            'marketing_content': 'marketing_content.txt',
            'kdp_guide': 'KDP_PUBLISHING_GUIDE.txt',
            'manuscript_txt': 'manuscript.txt'
        }
        
        for asset_type, filename in asset_files.items():
            file_path = volume_path / filename
            if file_path.exists():
                assets[asset_type] = file_path
                
        return assets
    
    def list_all_series(self) -> List[Tuple[str, str]]:
        """List all brand/series combinations"""
        series_list = []
        
        if not self.base_dir.exists():
            return series_list
            
        for brand_dir in self.base_dir.iterdir():
            if brand_dir.is_dir():
                for series_dir in brand_dir.iterdir():
                    if series_dir.is_dir():
                        series_list.append((brand_dir.name, series_dir.name))
        
        return series_list
    
    def list_volumes_for_series(self, brand_name: str, series_name: str) -> List[int]:
        """List all volumes for a specific series"""
        series_path = self.get_brand_series_path(brand_name, series_name)
        volumes = []
        
        if not series_path.exists():
            return volumes
            
        for volume_dir in series_path.iterdir():
            if volume_dir.is_dir() and volume_dir.name.startswith('volume_'):
                try:
                    volume_num = int(volume_dir.name.split('_')[1])
                    volumes.append(volume_num)
                except (ValueError, IndexError):
                    continue
                    
        return sorted(volumes)
    
    def get_asset_inventory(self) -> Dict:
        """Get complete inventory of all assets"""
        inventory = {
            'timestamp': datetime.now().isoformat(),
            'total_brands': 0,
            'total_series': 0,
            'total_volumes': 0,
            'brands': {}
        }
        
        for brand_name, series_name in self.list_all_series():
            if brand_name not in inventory['brands']:
                inventory['brands'][brand_name] = {'series': {}}
                inventory['total_brands'] += 1
            
            volumes = self.list_volumes_for_series(brand_name, series_name)
            inventory['brands'][brand_name]['series'][series_name] = {
                'volume_count': len(volumes),
                'volumes': volumes
            }
            inventory['total_series'] += 1
            inventory['total_volumes'] += len(volumes)
        
        return inventory
    
    def migrate_legacy_structure(self, legacy_dir: str = "output/generated_books") -> bool:
        """Migrate from legacy flat structure to new hierarchical structure"""
        legacy_path = Path(legacy_dir)
        
        if not legacy_path.exists():
            return True
            
        migrated_count = 0
        
        for legacy_volume_dir in legacy_path.iterdir():
            if not legacy_volume_dir.is_dir():
                continue
                
            # Parse legacy directory name
            if "large_print_crossword_masters_vol_" in legacy_volume_dir.name:
                try:
                    vol_num = int(legacy_volume_dir.name.split('_vol_')[1].split('_')[0])
                    brand_name = "Senior Puzzle Studio"
                    series_name = "Large Print Crossword Masters"
                    
                    # Prepare assets for migration
                    assets = {}
                    for file_path in legacy_volume_dir.iterdir():
                        if file_path.is_file():
                            if file_path.name.startswith('cover_vol_') and file_path.suffix == '.png':
                                assets['cover'] = str(file_path)
                            elif file_path.name.endswith('_KDP_READY.pdf'):
                                assets['manuscript_pdf'] = str(file_path)
                            elif file_path.name == 'cover_design_prompt.txt':
                                assets['cover_prompt'] = str(file_path)
                            elif file_path.name == 'metadata.json':
                                assets['metadata'] = str(file_path)
                            elif file_path.name == 'back_cover_content.txt':
                                assets['back_cover_content'] = str(file_path)
                            elif file_path.name == 'marketing_content.txt':
                                assets['marketing_content'] = str(file_path)
                            elif file_path.name == 'KDP_PUBLISHING_GUIDE.txt':
                                assets['kdp_guide'] = str(file_path)
                            elif file_path.name == 'manuscript.txt':
                                assets['manuscript_txt'] = str(file_path)
                    
                    # Store in new structure
                    if assets:
                        self.store_volume_assets(brand_name, series_name, vol_num, assets)
                        migrated_count += 1
                        
                except (ValueError, IndexError):
                    continue
        
        return migrated_count > 0
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for filesystem compatibility"""
        # Replace spaces with underscores and remove special characters
        sanitized = name.replace(' ', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in ['_', '-'])
        return sanitized

# Convenience functions for backwards compatibility
def get_volume_data_new_structure(brand_name: str, series_name: str, vol_num: int) -> Optional[Dict]:
    """Get volume data using new directory structure"""
    asset_manager = AssetManager()
    assets = asset_manager.get_volume_assets(brand_name, series_name, vol_num)
    
    if not assets.get('metadata'):
        return None
        
    try:
        with open(assets['metadata'], 'r') as f:
            metadata = json.load(f)
            
        return {
            'volume': vol_num,
            'title': metadata.get('title', f'{series_name}: Volume {vol_num}'),
            'subtitle': metadata.get('subtitle', ''),
            'author': metadata.get('brand', brand_name),
            'description': metadata.get('description', ''),
            'keywords': metadata.get('keywords', []),
            'price': metadata.get('price', 7.99),
            'assets': assets,
            'volume_path': asset_manager.get_volume_path(brand_name, series_name, vol_num)
        }
        
    except Exception:
        return None