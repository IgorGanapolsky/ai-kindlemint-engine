#!/usr/bin/env python3
"""
Automated KDP Publishing for Volume 1
Uses the approved PDF manuscript and existing metadata
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kindlemint.publisher.kdp_agent import KDPPublisherAgent, BookAssets
from kindlemint.utils.logger import get_logger

def prepare_volume_1_assets():
    """Prepare Volume 1 assets for KDP publishing."""
    logger = get_logger('volume_1_publisher')
    
    try:
        # Volume 1 folder path
        vol_1_folder = Path("output/generated_books/large_print_crossword_masters_vol_1_final")
        
        if not vol_1_folder.exists():
            raise FileNotFoundError(f"Volume 1 folder not found: {vol_1_folder}")
        
        logger.info(f"📁 Found Volume 1 folder: {vol_1_folder}")
        
        # Load metadata
        metadata_file = vol_1_folder / "metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Load KDP publishing guide for details
        kdp_guide_file = vol_1_folder / "KDP_PUBLISHING_GUIDE.txt"
        with open(kdp_guide_file, 'r') as f:
            kdp_guide = f.read()
        
        # Extract description from KDP guide
        description_start = kdp_guide.find("→ Description:") + len("→ Description:")
        description_end = kdp_guide.find("\n4. KEYWORDS")
        description = kdp_guide[description_start:description_end].strip()
        
        # Extract keywords
        keywords = [
            "large print crossword",
            "easy crossword puzzles", 
            "senior crossword puzzles",
            "crossword for seniors",
            "puzzle book for seniors",
            "large print puzzle book",
            "easy brain games"
        ]
        
        # File paths
        pdf_manuscript = vol_1_folder / "large_print_crossword_masters_vol_1_final_KDP_READY.pdf"
        cover_image = vol_1_folder / "cover_vol_1.png"
        
        if not pdf_manuscript.exists():
            raise FileNotFoundError(f"PDF manuscript not found: {pdf_manuscript}")
        
        if not cover_image.exists():
            raise FileNotFoundError(f"Cover image not found: {cover_image}")
        
        # Create BookAssets object
        book_assets = BookAssets(
            book_id="vol_1_crossword_masters",
            title="Large Print Crossword Masters: Volume 1",
            subtitle="Easy Large Print Crosswords for Seniors",
            description=description,
            keywords=keywords,
            categories=["Games & Puzzles > Crosswords", "Health & Fitness > Aging"],
            manuscript_path=str(pdf_manuscript),
            cover_path=str(cover_image),
            author_name="Senior Puzzle Studio",
            price=7.99,
            niche="large_print_crosswords_seniors"
        )
        
        logger.info("✅ Volume 1 assets prepared successfully")
        logger.info(f"📄 Manuscript: {pdf_manuscript.name}")
        logger.info(f"🎨 Cover: {cover_image.name}")
        logger.info(f"💰 Price: ${book_assets.price}")
        
        return book_assets
        
    except Exception as e:
        logger.error(f"❌ Failed to prepare Volume 1 assets: {e}")
        raise

def publish_volume_1():
    """Publish Volume 1 to KDP using automation."""
    logger = get_logger('volume_1_publisher')
    
    logger.info("🚀 Starting automated KDP publishing for Volume 1")
    
    # Load environment variables from .env file
    env_file = Path(".env")
    if env_file.exists():
        logger.info("📄 Loading credentials from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check environment
    kdp_email = os.getenv('KDP_EMAIL')
    kdp_password = os.getenv('KDP_PASSWORD')
    
    if not kdp_email or not kdp_password:
        logger.error("❌ KDP credentials not found in environment")
        logger.info("💡 Please set KDP_EMAIL and KDP_PASSWORD environment variables")
        logger.info("💡 Or run manually: export KDP_EMAIL=your_email@example.com")
        logger.info("💡 Or run manually: export KDP_PASSWORD=your_password")
        return False
    
    try:
        # Prepare assets
        book_assets = prepare_volume_1_assets()
        
        # Initialize KDP publisher
        logger.info("🔧 Initializing KDP Publisher Agent...")
        
        with KDPPublisherAgent(
            headless=False,  # Set to True for full automation
            timeout=60000,   # Extended timeout for uploads
            slow_mo=2000,    # Slower for reliability
            kdp_email=kdp_email,
            kdp_password=kdp_password
        ) as agent:
            
            logger.info("🔐 Logging into KDP...")
            login_success = agent.login_to_kdp()
            
            if not login_success:
                logger.error("❌ KDP login failed")
                return False
            
            logger.info("📚 Creating new book on KDP...")
            result = agent.create_new_book(book_assets)
            
            # Process result
            if result.success:
                logger.info("🎉 SUCCESS: Volume 1 published to KDP!")
                logger.info(f"📖 Book ID: {result.book_id}")
                if result.asin:
                    logger.info(f"🔢 ASIN: {result.asin}")
                if result.kdp_url:
                    logger.info(f"🔗 KDP URL: {result.kdp_url}")
                
                # Save publishing result
                result_file = Path("output/volume_1_publishing_result.json")
                result_data = {
                    'success': result.success,
                    'book_id': result.book_id,
                    'kdp_url': result.kdp_url,
                    'asin': result.asin,
                    'errors': result.errors,
                    'warnings': result.warnings,
                    'publishing_timestamp': result.publishing_timestamp,
                    'title': book_assets.title,
                    'price': book_assets.price
                }
                
                with open(result_file, 'w') as f:
                    json.dump(result_data, f, indent=2)
                
                logger.info(f"📊 Publishing result saved to: {result_file}")
                
                print("\n" + "="*60)
                print("🎉 VOLUME 1 PUBLISHED SUCCESSFULLY!")
                print("="*60)
                print(f"📚 Title: {book_assets.title}")
                print(f"💰 Price: ${book_assets.price}")
                print(f"📄 Manuscript: PDF with 50 crossword puzzles")
                print(f"⏰ Published: {result.publishing_timestamp}")
                if result.asin:
                    print(f"🔢 ASIN: {result.asin}")
                print("="*60)
                print("📋 Next Steps:")
                print("1. Book is now in KDP review queue")
                print("2. Review typically takes 24-72 hours")
                print("3. You'll receive email notification when approved")
                print("4. Book will be live on Amazon for purchase")
                print("="*60)
                
                return True
                
            else:
                logger.error("❌ Publishing failed")
                for error in result.errors:
                    logger.error(f"   Error: {error}")
                for warning in result.warnings:
                    logger.warning(f"   Warning: {warning}")
                
                return False
        
    except Exception as e:
        logger.error(f"❌ Volume 1 publishing failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function for Volume 1 publishing."""
    print("=" * 60)
    print("🤖 AUTOMATED KDP PUBLISHING - VOLUME 1")
    print("=" * 60)
    print("📚 Book: Large Print Crossword Masters: Volume 1")
    print("📄 Format: PDF (KDP-ready)")
    print("💰 Price: $7.99")
    print("🎯 Target: Seniors who love crossword puzzles")
    print("=" * 60)
    
    try:
        success = publish_volume_1()
        
        if success:
            print("\n🎉 AUTOMATED PUBLISHING COMPLETED!")
            return True
        else:
            print("\n❌ AUTOMATED PUBLISHING FAILED!")
            print("💡 Check logs above for details")
            return False
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)