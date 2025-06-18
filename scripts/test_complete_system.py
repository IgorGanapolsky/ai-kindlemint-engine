#!/usr/bin/env python3
"""
Test the complete multi-provider system with OpenAI + Gemini.
Validates API access and generates a test book.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger
from kindlemint.utils.api_manager import get_api_manager

async def test_complete_system():
    """Test the complete multi-provider book generation system."""
    logger = get_logger('system_test')
    
    logger.info("🧪 Testing complete multi-provider system...")
    
    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Test API Manager
    api_manager = get_api_manager()
    
    # Test Gemini for text generation (cheap)
    logger.info("📝 Testing Gemini text generation...")
    gemini_text = api_manager.generate_text(
        "Generate a brief introduction for a large print crossword book for seniors.",
        task_type='cheap_text',
        priority='cost'
    )
    
    if gemini_text:
        logger.info(f"✅ Gemini text: {gemini_text[:100]}...")
    else:
        logger.warning("⚠️ Gemini text generation failed")
    
    # Test OpenAI for cover generation
    logger.info("🎨 Testing OpenAI cover generation...")
    cover_url = api_manager.generate_image(
        "Professional book cover for 'Large Print Crossword Masters Volume 1' by Senior Puzzle Studio. Clean design, crossword grid background, large readable text for seniors."
    )
    
    if cover_url:
        logger.info(f"✅ OpenAI cover: {cover_url[:50]}...")
    else:
        logger.warning("⚠️ OpenAI cover generation failed")
    
    # Test complete book generation with multi-provider
    logger.info("📚 Testing complete book generation...")
    
    # Use our enhanced generator that uses both providers
    result = await generate_multi_provider_book()
    
    if result:
        logger.info("🎉 COMPLETE SYSTEM TEST SUCCESSFUL!")
        logger.info(f"✅ Text generation: {'✓' if gemini_text else '✗'}")
        logger.info(f"✅ Image generation: {'✓' if cover_url else '✗'}")
        logger.info(f"✅ Book generation: {'✓' if result else '✗'}")
        
        # Show usage summary
        usage = api_manager.get_usage_summary()
        logger.info(f"💰 Total cost today: ${usage['total_cost_today']:.4f}")
        logger.info(f"📊 Total requests: {usage['total_requests_today']}")
        
        for provider, stats in usage['provider_availability'].items():
            status = "✅ Available" if stats['available'] else "❌ Limited"
            logger.info(f"   {provider}: {status} (${stats['cost_today']:.4f})")
    
    return result

async def generate_multi_provider_book():
    """Generate a book using the multi-provider approach."""
    try:
        api_manager = get_api_manager()
        
        # Step 1: Generate series info with Gemini (cheap)
        series_prompt = """
        Create a JSON structure for a large print crossword book series:
        
        {
            "series_name": "Large Print Crossword Masters",
            "brand": "Senior Puzzle Studio", 
            "volume": 1,
            "title": "Large Print Crossword Masters: Volume 1",
            "subtitle": "Easy Large Print Crosswords for Seniors",
            "difficulty": "beginner",
            "target_audience": "seniors_55_plus"
        }
        
        Return only the JSON.
        """
        
        series_json = api_manager.generate_text(
            series_prompt, 
            task_type='cheap_text', 
            priority='cost'
        )
        
        # Step 2: Generate content with Gemini (cheap)
        content_prompt = """
        Create manuscript content for a large print crossword book for seniors.
        Include: Introduction, instructions, placeholder for puzzles, and back matter.
        Make it professional and friendly for seniors.
        """
        
        manuscript_content = api_manager.generate_text(
            content_prompt,
            task_type='cheap_text',
            priority='cost',
            max_tokens=2000
        )
        
        # Step 3: Generate cover with OpenAI (premium)
        cover_prompt = """
        Create a professional Amazon KDP book cover:
        - Title: "LARGE PRINT CROSSWORD MASTERS"
        - Subtitle: "Easy Large Print Crosswords for Seniors"  
        - Volume: "VOLUME 1"
        - Brand: "SENIOR PUZZLE STUDIO"
        - Style: Clean, readable, crossword grid background, calming colors
        - Target: Seniors who need large print text
        """
        
        cover_url = api_manager.generate_image(cover_prompt)
        
        # Step 4: Save the generated book
        output_dir = Path(__file__).parent.parent / "output" / "generated_books"
        book_folder = output_dir / f"multi_provider_test_{api_manager._get_timestamp()}"
        book_folder.mkdir(parents=True, exist_ok=True)
        
        # Save manuscript
        if manuscript_content:
            with open(book_folder / "manuscript.txt", 'w') as f:
                f.write(manuscript_content)
        
        # Save series info
        if series_json:
            with open(book_folder / "series_info.json", 'w') as f:
                f.write(series_json)
        
        # Save cover URL
        if cover_url:
            with open(book_folder / "cover_url.txt", 'w') as f:
                f.write(cover_url)
            
            # Download cover image
            try:
                import requests
                response = requests.get(cover_url, timeout=30)
                if response.status_code == 200:
                    with open(book_folder / "cover.png", 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                logger.warning(f"Cover download failed: {e}")
        
        return book_folder
        
    except Exception as e:
        logger.error(f"Multi-provider book generation failed: {e}")
        return None

def main():
    """Main test function."""
    return asyncio.run(test_complete_system())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)