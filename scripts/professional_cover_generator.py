#!/usr/bin/env python3
"""
Professional Two-Stage Cover Generator
Combines AI art generation with programmatic typography
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
# Import locally from current directory
sys.path.append(str(Path(__file__).parent))
from generate_background_art import BackgroundArtGenerator
from typography_engine import TypographyEngine

class ProfessionalCoverGenerator:
    def __init__(self):
        self.logger = get_logger('professional_cover_generator')
        self.art_generator = BackgroundArtGenerator()
        self.typography_engine = TypographyEngine()
        
    def generate_complete_cover(self, volume_data, force_regenerate=False):
        """
        Generate a complete professional cover using two-stage pipeline
        """
        volume_num = volume_data.get('volume', 1)
        self.logger.info(f"🎨 Starting two-stage cover generation for Volume {volume_num}")
        
        # Define paths
        background_path = f"output/background_art/background_vol_{volume_num}.png"
        final_cover_path = self._get_cover_output_path(volume_num)
        
        # Stage 1: Generate TEXT-FREE background art
        if not Path(background_path).exists() or force_regenerate:
            self.logger.info(f"🎨 Stage 1: Generating background art for Volume {volume_num}")
            background_path = self.art_generator.generate_crossword_background(
                volume_num, volume_data.get('theme', 'crossword')
            )
            
            if not background_path:
                self.logger.error(f"❌ Stage 1 failed: Could not generate background art")
                return None
        else:
            self.logger.info(f"✅ Stage 1: Using existing background art: {background_path}")
        
        # Stage 2: Add professional typography
        self.logger.info(f"🖋️ Stage 2: Adding professional typography to Volume {volume_num}")
        success = self.typography_engine.create_professional_cover(
            background_path, volume_data, final_cover_path
        )
        
        if success:
            self.logger.info(f"✅ Professional cover completed: {final_cover_path}")
            
            # Copy to volume folder for integration
            self._copy_to_volume_folder(final_cover_path, volume_num)
            
            return final_cover_path
        else:
            self.logger.error(f"❌ Stage 2 failed: Typography overlay failed")
            return None
    
    def _get_cover_output_path(self, volume_num):
        """Get standardized cover output path"""
        covers_dir = Path("output/professional_covers")
        covers_dir.mkdir(exist_ok=True)
        return covers_dir / f"cover_vol_{volume_num}_professional.png"
    
    def _copy_to_volume_folder(self, cover_path, volume_num):
        """Copy finished cover to volume folder for publishing"""
        try:
            # Find volume folder
            books_dir = Path("output/generated_books")
            vol_folders = [f for f in books_dir.iterdir() 
                          if f.is_dir() and f"vol_{volume_num}_final" in f.name]
            
            if vol_folders:
                vol_folder = vol_folders[0]
                destination = vol_folder / f"cover_vol_{volume_num}.png"
                
                # Copy the professional cover
                import shutil
                shutil.copy2(cover_path, destination)
                
                self.logger.info(f"✅ Cover copied to volume folder: {destination}")
            else:
                self.logger.warning(f"⚠️ Volume {volume_num} folder not found for cover copy")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to copy cover to volume folder: {e}")
    
    def regenerate_all_covers(self, series_name="Large_Print_Crossword_Masters", max_volumes=5):
        """Regenerate all covers using the new professional pipeline"""
        
        self.logger.info(f"🎨 Regenerating all covers for {series_name}")
        
        # Get volume metadata for consistent branding
        volumes_data = self._get_volumes_metadata(max_volumes)
        
        successful_covers = []
        failed_covers = []
        
        for volume_data in volumes_data:
            volume_num = volume_data['volume']
            
            try:
                self.logger.info(f"📚 Processing Volume {volume_num}...")
                
                cover_path = self.generate_complete_cover(volume_data, force_regenerate=True)
                
                if cover_path:
                    successful_covers.append(volume_num)
                    self.logger.info(f"✅ Volume {volume_num} cover completed")
                else:
                    failed_covers.append(volume_num)
                    self.logger.error(f"❌ Volume {volume_num} cover failed")
                    
            except Exception as e:
                self.logger.error(f"❌ Volume {volume_num} processing failed: {e}")
                failed_covers.append(volume_num)
        
        # Report results
        self.logger.info(f"📊 Cover generation complete:")
        self.logger.info(f"✅ Successful: {successful_covers}")
        
        if failed_covers:
            self.logger.warning(f"❌ Failed: {failed_covers}")
        
        return len(failed_covers) == 0
    
    def _get_volumes_metadata(self, max_volumes):
        """Get metadata for all volumes to ensure consistent branding"""
        
        volumes_data = []
        
        for vol_num in range(1, max_volumes + 1):
            # Try to load existing metadata
            volume_data = self._load_existing_metadata(vol_num)
            
            if not volume_data:
                # Create default metadata
                volume_data = {
                    'volume': vol_num,
                    'title': 'Large Print Crossword Masters',
                    'subtitle': 'Easy Large Print Crosswords for Seniors',
                    'brand': 'Senior Puzzle Studio',
                    'theme': 'crossword',
                    'series': 'Large_Print_Crossword_Masters'
                }
            
            volumes_data.append(volume_data)
        
        return volumes_data
    
    def _load_existing_metadata(self, volume_num):
        """Load existing volume metadata if available"""
        try:
            books_dir = Path("output/generated_books")
            vol_folders = [f for f in books_dir.iterdir() 
                          if f.is_dir() and f"vol_{volume_num}_final" in f.name]
            
            if vol_folders:
                metadata_file = vol_folders[0] / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Convert to volume_data format
                    return {
                        'volume': volume_num,
                        'title': metadata.get('title', 'Large Print Crossword Masters'),
                        'subtitle': metadata.get('subtitle', 'Easy Large Print Crosswords for Seniors'), 
                        'brand': metadata.get('brand', 'Senior Puzzle Studio'),
                        'theme': 'crossword',
                        'series': metadata.get('series', 'Large_Print_Crossword_Masters')
                    }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load metadata for Volume {volume_num}: {e}")
            return None

def main():
    """Main professional cover generation function"""
    parser = argparse.ArgumentParser(description='Professional Two-Stage Cover Generator')
    parser.add_argument('--volume', type=int, help='Generate cover for specific volume')
    parser.add_argument('--all', action='store_true', help='Regenerate all covers')
    parser.add_argument('--force', action='store_true', help='Force regeneration even if exists')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🎨 PROFESSIONAL TWO-STAGE COVER GENERATOR")
    print("=" * 70)
    print("Stage 1: AI generates TEXT-FREE background art")
    print("Stage 2: Code adds precise, professional typography")
    print("=" * 70)
    
    generator = ProfessionalCoverGenerator()
    
    if args.all:
        print("🔄 Regenerating ALL covers with new professional pipeline...")
        success = generator.regenerate_all_covers()
        
        if success:
            print("🎉 ALL COVERS REGENERATED SUCCESSFULLY!")
            print("✅ Your book series now has professional, consistent covers")
        else:
            print("⚠️ Some covers failed - check logs for details")
            
    elif args.volume:
        print(f"🔄 Generating professional cover for Volume {args.volume}...")
        
        volume_data = {
            'volume': args.volume,
            'title': 'Large Print Crossword Masters',
            'subtitle': 'Easy Large Print Crosswords for Seniors',
            'brand': 'Senior Puzzle Studio',
            'theme': 'crossword'
        }
        
        cover_path = generator.generate_complete_cover(volume_data, args.force)
        
        if cover_path:
            print(f"✅ Professional cover created: {cover_path}")
        else:
            print("❌ Cover generation failed")
            sys.exit(1)
    
    else:
        print("❌ Please specify --volume X or --all")
        sys.exit(1)
    
    print("=" * 70)

if __name__ == "__main__":
    main()