#!/usr/bin/env python3
"""
Direct crossword generation using approved series strategy.
Bypasses market intelligence and uses Gemini API to avoid OpenAI quota limits.
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

async def main():
    """Generate Large Print Crossword Masters Volume 1 directly."""
    logger = get_logger('direct_crossword')
    
    logger.info("🎯 Direct Large Print Crossword Masters Volume 1 generation...")
    
    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        logger.error("❌ GEMINI_API_KEY not found")
        return False
    
    logger.info("✅ Using Gemini API for generation")
    
    try:
        # Use the approved series strategy directly
        approved_opportunity = {
            'micro_niche': 'Large print crossword puzzles for seniors',
            'niche': 'Puzzle Books',
            'topic': 'Large Print Crosswords for Seniors',
            'market_score': 85,
            'estimated_revenue': 15.0,
            'difficulty_level': 'beginner',
            'target_demographic': 'seniors_55_plus',
            'suggested_brand': 'Senior Puzzle Studio'
        }
        
        logger.info(f"📚 Using approved opportunity: {approved_opportunity['topic']}")
        
        # Create series directly using Gemini
        book_series = await create_series_with_gemini(approved_opportunity, logger)
        
        # Create Volume 1 content
        volume_1_result = await generate_volume_1_content(book_series, logger)
        
        # Save to output directory
        output_dir = Path(__file__).parent.parent / "lambda" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        book_folder = output_dir / f"senior_puzzle_studio_crossword_masters_vol_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        book_folder.mkdir(exist_ok=True)
        
        # Save manuscript
        manuscript_file = book_folder / "manuscript.txt"
        with open(manuscript_file, 'w', encoding='utf-8') as f:
            f.write(volume_1_result['content'])
        
        # Save metadata
        metadata_file = book_folder / "metadata.json"
        metadata = {
            'title': book_series['books'][0]['title'],
            'subtitle': book_series['books'][0]['subtitle'],
            'series': book_series['series_name'],
            'brand': book_series['series_brand'],
            'volume': 1,
            'difficulty': 'beginner',
            'target_audience': 'seniors_55_plus',
            'keywords': book_series['books'][0]['keywords'],
            'description': volume_1_result['description'],
            'generated_at': datetime.now().isoformat()
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Create simple cover prompt
        cover_prompt_file = book_folder / "cover_prompt.txt"
        with open(cover_prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"""Cover Design Prompt for {metadata['title']}:

Professional book cover for large print crossword puzzle book for seniors.
- Title: {metadata['title']}
- Subtitle: {metadata['subtitle']}
- Brand: Senior Puzzle Studio
- Clean, readable fonts
- Calming colors (blues, greens)
- Crossword grid imagery
- Professional appearance
- Easy to read on Amazon thumbnail
""")
        
        # Generate automated cover using DALL-E
        cover_file = await generate_automated_cover(book_folder, metadata, logger)
        
        logger.info("🎉 BOOK GENERATION COMPLETED!")
        logger.info(f"📁 Generated files in: {book_folder}")
        logger.info(f"   📄 {manuscript_file.name}: {manuscript_file.stat().st_size / 1024:.1f} KB")
        logger.info(f"   📋 {metadata_file.name}: {metadata_file.stat().st_size / 1024:.1f} KB") 
        logger.info(f"   🎨 {cover_prompt_file.name}: {cover_prompt_file.stat().st_size / 1024:.1f} KB")
        if cover_file:
            logger.info(f"   🖼️ {cover_file.name}: {cover_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct generation failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

async def create_series_with_gemini(opportunity, logger):
    """Create series structure using Gemini API."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Create a 5-volume crossword puzzle book series for seniors with large print.
        
        Niche: {opportunity['micro_niche']}
        Brand: {opportunity['suggested_brand']}
        Target: Seniors 55+ who need large print puzzles
        
        Generate a JSON structure with:
        1. Series name and brand
        2. 5 volume progression (beginner to expert)
        3. Each volume with title, subtitle, keywords, difficulty
        
        Format as JSON:
        {{
            "series_name": "Large Print Crossword Masters",
            "series_brand": "Senior Puzzle Studio",
            "micro_niche": "{opportunity['micro_niche']}",
            "books": [
                {{
                    "volume_number": 1,
                    "title": "volume title",
                    "subtitle": "subtitle",
                    "difficulty": "beginner",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "target_pages": 100
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        content = response.text
        
        # Extract JSON from response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        series_data = json.loads(content)
        logger.info(f"✅ Series created: {series_data['series_name']}")
        
        return series_data
        
    except Exception as e:
        logger.warning(f"Gemini series creation failed: {e}")
        # Fallback to hardcoded series
        return {
            "series_name": "Large Print Crossword Masters",
            "series_brand": "Senior Puzzle Studio",
            "micro_niche": opportunity['micro_niche'],
            "books": [
                {
                    "volume_number": 1,
                    "title": "Large Print Crossword Masters: Volume 1",
                    "subtitle": "Easy Large Print Crosswords for Seniors",
                    "difficulty": "beginner",
                    "keywords": ["large print crosswords", "senior puzzles", "easy crosswords", "brain games", "word puzzles"],
                    "target_pages": 100
                }
            ]
        }

async def generate_volume_1_content(series, logger):
    """Generate content for Volume 1."""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        volume_1 = series['books'][0]
        
        prompt = f"""
        Create content for a large print crossword puzzle book for seniors.
        
        Title: {volume_1['title']}
        Subtitle: {volume_1['subtitle']}
        Difficulty: {volume_1['difficulty']}
        Target Pages: {volume_1['target_pages']}
        
        Generate:
        1. Title page
        2. Introduction explaining large print benefits for seniors
        3. Instructions for solving crosswords
        4. 25 easy crossword puzzles with large print
        5. Answer key
        6. Back matter with website link
        
        Format as readable manuscript text suitable for KDP publishing.
        Include proper spacing and formatting.
        """
        
        response = model.generate_content(prompt)
        content = response.text
        
        # Generate KDP description
        desc_prompt = f"""
        Write a compelling Amazon KDP book description for:
        {volume_1['title']} - {volume_1['subtitle']}
        
        This is a large print crossword book for seniors. Include benefits, features, and call to action.
        Format for Amazon with bullet points and compelling copy.
        """
        
        desc_response = model.generate_content(desc_prompt)
        description = desc_response.text
        
        logger.info(f"✅ Volume 1 content generated: {len(content)} characters")
        
        return {
            'content': content,
            'description': description
        }
        
    except Exception as e:
        logger.warning(f"Content generation failed: {e}")
        # Generate actual crossword content using the crossword generator
        try:
            # Import the crossword generator
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from kindlemint.core.crossword_generator import generate_complete_crossword_content
            
            # Generate complete crossword content with 50 puzzles
            actual_content = generate_complete_crossword_content(puzzle_count=50)
            logger.info(f"✅ Generated complete crossword content: {len(actual_content)} characters")
            
            return {
                'content': actual_content,
                'description': f"Easy large print crosswords perfect for seniors! This collection of 50 beginner-friendly puzzles features large, clear text that's easy on the eyes. Ideal for cognitive stimulation and entertainment."
            }
        except Exception as e:
            logger.error(f"Failed to generate actual crosswords: {e}")
            # Ultimate fallback
            return {
                'content': f"ERROR: Crossword generation failed. Please check the crossword_generator module.",
                'description': f"Easy large print crosswords perfect for seniors! This collection of 50 beginner-friendly puzzles features large, clear text that's easy on the eyes. Ideal for cognitive stimulation and entertainment."
            }

async def generate_automated_cover(book_folder: Path, metadata: dict, logger):
    """Generate cover using DALL-E API based on book metadata."""
    try:
        import requests
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not found - skipping automated cover generation")
            return None
        
        # Create enhanced cover prompt
        dalle_prompt = f"""
        Create a professional Amazon KDP book cover for "{metadata['title']}" by {metadata['brand']}.
        
        Style requirements:
        - Clean, professional design suitable for seniors
        - Large, readable typography for book title and subtitle
        - Crossword puzzle grid pattern in background
        - Calming blue-green color scheme (#2C5F6B, #4A8A94, #7FB8C3)
        - Easy to read at thumbnail size on Amazon
        - Premium quality appearance
        - Series volume indicator clearly visible
        
        Text elements:
        - Main title: "LARGE PRINT CROSSWORD MASTERS"
        - Volume: "VOLUME 1" 
        - Subtitle: "Easy Large Print Crosswords for Seniors"
        - Author/Brand: "SENIOR PUZZLE STUDIO"
        
        Layout:
        - Title at top in bold, dark text
        - Crossword grid background pattern
        - Clean typography hierarchy
        - Professional book cover proportions (6x9 or 8.5x11)
        - High contrast for readability
        """
        
        logger.info("🎨 Generating automated cover with DALL-E...")
        
        # Call DALL-E API
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'dall-e-3',
            'prompt': dalle_prompt,
            'size': '1024x1024',
            'quality': 'hd',
            'n': 1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Download the generated image
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                cover_file = book_folder / "cover_generated.png"
                with open(cover_file, 'wb') as f:
                    f.write(img_response.content)
                
                logger.info("✅ Automated cover generated successfully")
                return cover_file
            else:
                logger.error(f"❌ Failed to download generated cover: {img_response.status_code}")
                return None
        else:
            logger.warning(f"⚠️ DALL-E API error: {response.status_code} - using manual cover if available")
            return None
            
    except Exception as e:
        logger.warning(f"⚠️ Automated cover generation failed: {e} - manual cover can still be added")
        return None

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)