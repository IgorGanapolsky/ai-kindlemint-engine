#!/usr/bin/env python3
"""
Generate covers with DALL-E (clean version)
Now that auto-recharge is enabled, generate actual cover images
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def clean_volume_folder(folder):
    """Remove unnecessary cover files from volume folder"""
    files_to_remove = [
        "COVER_INSTRUCTIONS_VOL_*.md",
        "cover_vol_*_template.html"
    ]
    
    for pattern in files_to_remove:
        for file in folder.glob(pattern):
            file.unlink()
            print(f"🗑️  Removed: {file.name}")

def generate_dalle_cover(vol_num, logger):
    """Generate cover with DALL-E using simple, effective prompt"""
    try:
        from openai import OpenAI
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("❌ OpenAI API key not found")
            return None
            
        client = OpenAI(api_key=openai_key)
        
        # Simple, effective prompt that should work
        prompt = f"Professional book cover background with crossword puzzle theme for seniors. Blue and green colors. Clean minimal design. Abstract crossword grid pattern. Volume {vol_num}."
        
        logger.info(f"🎨 Generating DALL-E cover for Volume {vol_num}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url, timeout=30)
        
        if image_response.status_code == 200:
            logger.info(f"✅ DALL-E cover generated successfully for Volume {vol_num}")
            return image_response.content
        else:
            logger.error(f"❌ Failed to download cover for Volume {vol_num}")
            return None
            
    except Exception as e:
        logger.error(f"❌ DALL-E generation failed for Volume {vol_num}: {e}")
        return None

def generate_all_covers():
    """Generate DALL-E covers for all volumes"""
    logger = get_logger('dalle_cover_generation')
    
    logger.info("🎨 Generating DALL-E covers for all volumes...")
    
    load_environment()
    
    # Find volume folders
    generated_books_dir = Path("output/generated_books")
    volume_folders = {}
    
    for folder in generated_books_dir.iterdir():
        if folder.is_dir() and "vol_" in folder.name and "_final" in folder.name:
            if "vol_1_final" in folder.name:
                volume_folders[1] = folder
            elif "vol_2_final" in folder.name:
                volume_folders[2] = folder
            elif "vol_3_final" in folder.name:
                volume_folders[3] = folder
            elif "vol_4_final" in folder.name:
                volume_folders[4] = folder
            elif "vol_5_final" in folder.name:
                volume_folders[5] = folder
    
    logger.info(f"📁 Found {len(volume_folders)} volume folders")
    
    covers_generated = 0
    
    for vol_num in sorted(volume_folders.keys()):
        folder = volume_folders[vol_num]
        
        # Clean up unnecessary files first
        clean_volume_folder(folder)
        
        # Check if cover already exists
        existing_covers = list(folder.glob("cover*.png")) + list(folder.glob("cover*.jpg"))
        if existing_covers:
            logger.info(f"✅ Cover already exists for Volume {vol_num}")
            covers_generated += 1
            continue
        
        # Generate with DALL-E
        cover_data = generate_dalle_cover(vol_num, logger)
        
        if cover_data:
            # Save cover
            cover_file = folder / f"cover_vol_{vol_num}.png"
            with open(cover_file, 'wb') as f:
                f.write(cover_data)
            covers_generated += 1
            logger.info(f"✅ Cover saved: {cover_file}")
            print(f"✅ Volume {vol_num} cover generated: {cover_file}")
        else:
            logger.error(f"❌ Failed to generate cover for Volume {vol_num}")
            print(f"❌ Volume {vol_num} cover generation failed")
    
    logger.info(f"🎉 Cover generation completed!")
    logger.info(f"✅ {covers_generated}/{len(volume_folders)} covers generated")
    
    return covers_generated, len(volume_folders)

def update_publishing_ready():
    """Update the PUBLISHING_READY folder with new covers"""
    logger = get_logger('publishing_update')
    
    logger.info("📦 Updating PUBLISHING_READY folder with covers...")
    
    # Copy covers to PUBLISHING_READY structure
    publishing_dir = Path("output/PUBLISHING_READY")
    
    if not publishing_dir.exists():
        logger.warning("⚠️ PUBLISHING_READY folder not found")
        return
    
    # Update Google Drive backup
    drive_backup = publishing_dir / "GOOGLE_DRIVE_BACKUP" / "Large_Print_Crossword_Masters_Series"
    
    # Update KDP submission
    kdp_submission = publishing_dir / "KDP_SUBMISSION" / "Large_Print_Crossword_Masters_Volumes"
    
    generated_books = Path("output/generated_books")
    
    for vol_num in range(1, 6):
        # Find source folder
        source_folder = None
        for folder in generated_books.iterdir():
            if folder.is_dir() and f"vol_{vol_num}_final" in folder.name:
                source_folder = folder
                break
        
        if not source_folder:
            continue
            
        # Check if source has cover
        cover_files = list(source_folder.glob("cover*.png")) + list(source_folder.glob("cover*.jpg"))
        if not cover_files:
            continue
            
        cover_file = cover_files[0]
        
        # Copy to Google Drive backup
        if drive_backup.exists():
            target_drive = drive_backup / f"Volume_{vol_num:02d}"
            if target_drive.exists():
                target_cover = target_drive / cover_file.name
                import shutil
                shutil.copy2(cover_file, target_cover)
                logger.info(f"📁 Copied cover to Drive backup: Volume {vol_num}")
        
        # Copy to KDP submission
        if kdp_submission.exists():
            target_kdp = kdp_submission / f"Volume_{vol_num:02d}"
            if target_kdp.exists():
                target_cover = target_kdp / cover_file.name
                import shutil
                shutil.copy2(cover_file, target_cover)
                logger.info(f"📚 Copied cover to KDP submission: Volume {vol_num}")
    
    logger.info("✅ PUBLISHING_READY folder updated with covers")

def main():
    """Main cover generation function"""
    print("=" * 60)
    print("🎨 DALL-E COVER GENERATION")
    print("=" * 60)
    
    try:
        # Generate covers
        covers_generated, total_volumes = generate_all_covers()
        
        if covers_generated > 0:
            # Update publishing folders
            update_publishing_ready()
        
        print("=" * 60)
        print("🎉 DALL-E COVER GENERATION COMPLETED!")
        print("=" * 60)
        print(f"✅ Covers generated: {covers_generated}/{total_volumes}")
        
        if covers_generated == total_volumes:
            print("🚀 ALL COVERS READY!")
            print("📁 Covers available in:")
            print("   - output/generated_books/*/cover_vol_*.png")
            print("   - output/PUBLISHING_READY/GOOGLE_DRIVE_BACKUP/")
            print("   - output/PUBLISHING_READY/KDP_SUBMISSION/")
            print("\n🎯 Ready for publishing!")
        else:
            print(f"⚠️ {total_volumes - covers_generated} covers still needed")
            print("💡 Check OpenAI account status if some failed")
            
        print("=" * 60)
        
        return covers_generated == total_volumes
        
    except Exception as e:
        print(f"❌ Cover generation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)