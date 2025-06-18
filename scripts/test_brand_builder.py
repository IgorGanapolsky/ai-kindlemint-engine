#!/usr/bin/env python3
"""
Test script for the Brand Builder with Large Print Crossword Masters series.
Tests the fixed OPENAI_API_KEY configuration.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.intelligence.brand_builder import BrandBuilder

def main():
    """Test the Brand Builder with the official series strategy."""
    logger = get_logger('brand_builder_test')
    
    logger.info("🧪 Testing Brand Builder with Large Print Crossword Masters...")
    
    # Check if OPENAI_API_KEY is available
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.error("❌ OPENAI_API_KEY not found in environment")
        logger.info("💡 Make sure to load .env file or set environment variable")
        return False
    
    logger.info(f"✅ OPENAI_API_KEY found: {openai_key[:10]}...")
    
    # Official series strategy from OFFICIAL_SERIES_STRATEGY.md
    test_series = {
        'series_name': 'Large Print Crossword Masters',
        'series_brand': 'Senior Puzzle Studio',
        'micro_niche': 'Large print crossword puzzles for seniors',
        'email_offer': '5 Exclusive Bonus Crossword Puzzles',
        'target_audience': 'seniors_55_plus',
        'difficulty_progression': ['beginner', 'easy', 'medium', 'challenging', 'expert']
    }
    
    try:
        # Test Brand Builder initialization
        logger.info("🏗️ Initializing Brand Builder...")
        builder = BrandBuilder()
        logger.info("✅ Brand Builder initialized successfully")
        
        # Test complete brand system creation
        logger.info("🎯 Creating complete brand system...")
        brand_system = asyncio.run(builder.build_complete_brand_system(test_series))
        
        # Display results
        logger.info("🎉 BRAND SYSTEM CREATED SUCCESSFULLY!")
        logger.info(f"📊 Results Summary:")
        logger.info(f"   Brand Name: {brand_system['brand_name']}")
        logger.info(f"   Website URL: {brand_system['website']['url']}")
        logger.info(f"   Website Platform: {brand_system['website']['platform']}")
        logger.info(f"   Email Provider: {brand_system['email_funnel']['provider']}")
        logger.info(f"   Email List: {brand_system['email_funnel']['list_name']}")
        logger.info(f"   Bonus Product: {brand_system['bonus_product']['title']}")
        logger.info(f"   Setup Time: {brand_system['estimated_setup_time']}")
        logger.info(f"   Monthly Cost: {brand_system['monthly_cost']}")
        logger.info(f"   Expected Capture Rate: {brand_system['expected_email_capture_rate']}")
        
        # Test back matter integration
        if 'book_integration' in brand_system:
            logger.info(f"\n📖 Book Integration Preview:")
            back_matter = brand_system['book_integration']['back_matter_cta']
            logger.info(f"Back matter CTA preview:\n{back_matter[:200]}...")
        
        logger.info("\n✅ Brand Builder test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Brand Builder test failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    success = main()
    sys.exit(0 if success else 1)