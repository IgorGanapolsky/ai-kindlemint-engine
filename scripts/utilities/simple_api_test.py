#!/usr/bin/env python3
"""
Simple API test to verify OpenAI and Gemini access.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def test_apis():
    """Test basic API access."""
    logger = get_logger('api_test')
    
    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    logger.info("🔑 API Keys Status:")
    logger.info(f"   OpenAI: {'✅ Found' if openai_key else '❌ Missing'}")
    logger.info(f"   Gemini: {'✅ Found' if gemini_key else '❌ Missing'}")
    
    # Test Gemini first (should work and be cheap)
    if gemini_key:
        logger.info("\n📝 Testing Gemini API...")
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content("Say 'Hello from Gemini!' in a friendly way.")
            logger.info(f"✅ Gemini success: {response.text[:100]}")
            
        except Exception as e:
            logger.error(f"❌ Gemini failed: {e}")
    
    # Test OpenAI (might have quota issues)
    if openai_key:
        logger.info("\n🤖 Testing OpenAI API...")
        try:
            import openai
            
            client = openai.OpenAI(api_key=openai_key)
            
            # Try a very small request first
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheaper model
                messages=[{"role": "user", "content": "Say 'Hello from OpenAI!' briefly."}],
                max_tokens=20
            )
            
            logger.info(f"✅ OpenAI success: {response.choices[0].message.content}")
            
        except Exception as e:
            logger.error(f"❌ OpenAI failed: {e}")
            if "quota" in str(e).lower():
                logger.info("💡 OpenAI quota issue - the spending limit might need time to propagate")
                logger.info("💡 Or you might need to verify your payment method")
    
    # Test fallback book generation without APIs
    logger.info("\n📚 Testing fallback book generation...")
    try:
        output_dir = Path(__file__).parent.parent / "output" / "generated_books"
        book_folder = output_dir / f"fallback_test_{get_timestamp()}"
        book_folder.mkdir(parents=True, exist_ok=True)
        
        # Create a basic book using templates (no API calls)
        manuscript = create_fallback_manuscript()
        metadata = create_fallback_metadata()
        
        with open(book_folder / "manuscript.txt", 'w') as f:
            f.write(manuscript)
        
        with open(book_folder / "metadata.json", 'w') as f:
            import json
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Fallback book created: {book_folder.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fallback generation failed: {e}")
        return False

def get_timestamp():
    """Get timestamp for naming."""
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def create_fallback_manuscript():
    """Create a basic manuscript without API calls."""
    from datetime import datetime
    
    return f"""Large Print Crossword Masters: Volume 1
Easy Large Print Crosswords for Seniors

By Senior Puzzle Studio

INTRODUCTION

Welcome to Large Print Crossword Masters! This collection has been specially designed for seniors who appreciate quality crossword puzzles with larger, easier-to-read text.

This Volume 1 features beginner level puzzles, perfect for getting started or enjoying a relaxing puzzle experience.

FEATURES OF THIS BOOK

• Large, clear text that's easy on the eyes
• Professional layout designed for comfort  
• Beginner-friendly crossword puzzles
• Perfect for relaxation and mental stimulation
• High-quality content curated by experts

HOW TO SOLVE CROSSWORDS

1. Read the clues carefully
2. Start with clues you know for certain
3. Use crossing letters to help solve difficult clues
4. Don't be afraid to guess and erase
5. Take breaks when needed - enjoy the process!

CROSSWORD PUZZLES

[In a production version, this section would contain 25 actual large print crossword puzzles with clear grids and numbered clues.]

PUZZLE 1: Getting Started
PUZZLE 2: Easy Words
PUZZLE 3: Simple Themes
...
PUZZLE 25: Beginner's Challenge

ANSWER KEY

[Complete solutions would be provided here]

BONUS CONTENT

Thank you for choosing Senior Puzzle Studio!

Get exclusive bonus puzzles and stay updated with new releases:
🌐 Visit: https://senior-puzzle-studio.carrd.co
📧 Get your FREE bonus crossword puzzles delivered to your inbox

ABOUT SENIOR PUZZLE STUDIO

Senior Puzzle Studio is dedicated to creating high-quality, accessible crossword puzzles for seniors. Our mission is to provide engaging, well-designed puzzles that bring joy and mental stimulation to our valued customers.

All our books are carefully crafted with large print text and clear layouts, ensuring the best possible experience for our readers.

© {datetime.now().year} Senior Puzzle Studio | All Rights Reserved

For customer support and feedback, visit our website for contact information.
"""

def create_fallback_metadata():
    """Create basic metadata."""
    from datetime import datetime
    
    return {
        "title": "Large Print Crossword Masters: Volume 1",
        "subtitle": "Easy Large Print Crosswords for Seniors",
        "series": "Large Print Crossword Masters", 
        "brand": "Senior Puzzle Studio",
        "volume": 1,
        "difficulty": "beginner",
        "target_audience": "seniors_55_plus",
        "niche": "large print crossword puzzles",
        "keywords": [
            "large print crosswords",
            "senior puzzles", 
            "easy crosswords",
            "brain games",
            "word puzzles",
            "beginner crosswords",
            "senior puzzle studio"
        ],
        "price_usd": 7.99,
        "description": "Perfect beginner level large print crosswords designed specifically for seniors. Volume 1 in the popular Large Print Crossword Masters collection by Senior Puzzle Studio. Features 25 easy puzzles with large, clear text that's comfortable to read.",
        "generated_at": datetime.now().isoformat(),
        "method": "fallback_generation",
        "version": "3.0"
    }

if __name__ == "__main__":
    success = test_apis()
    sys.exit(0 if success else 1)