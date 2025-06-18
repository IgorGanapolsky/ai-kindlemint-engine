#!/usr/bin/env python3
"""
Generate book cover using DALL-E API based on cover prompt.
Automates cover creation for KindleMint books.
"""
import os
import sys
import requests
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def generate_cover_from_prompt(book_directory: Path):
    """Generate cover using DALL-E based on cover_prompt.txt"""
    logger = get_logger('cover_generation')
    
    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.error("❌ OPENAI_API_KEY not found")
        return False
    
    # Read cover prompt
    prompt_file = book_directory / "cover_prompt.txt"
    if not prompt_file.exists():
        logger.error(f"❌ Cover prompt not found: {prompt_file}")
        return False
    
    with open(prompt_file, 'r') as f:
        cover_prompt = f.read()
    
    logger.info(f"🎨 Generating cover for: {book_directory.name}")
    
    try:
        # Enhanced prompt for better results
        dalle_prompt = f"""
        Create a professional Amazon KDP book cover with the following specifications:
        
        {cover_prompt}
        
        Additional requirements:
        - High resolution suitable for print (300 DPI quality)
        - Readable thumbnail at small sizes
        - Professional typography with clear hierarchy
        - Crossword puzzle grid background pattern
        - Calming, trustworthy color scheme
        - Easy-to-read fonts for seniors
        - Amazon KDP dimensions (6x9 or 8.5x11 inches)
        - No complex details that become unreadable when small
        """
        
        # Use OpenAI DALL-E API
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'dall-e-3',
            'prompt': dalle_prompt,
            'size': '1024x1024',  # Square format, can be resized for book
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
            
            # Download the image
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                cover_file = book_directory / "cover.png"
                with open(cover_file, 'wb') as f:
                    f.write(img_response.content)
                
                size_kb = cover_file.stat().st_size / 1024
                logger.info(f"✅ Cover generated: {cover_file.name} ({size_kb:.1f} KB)")
                return True
            else:
                logger.error(f"❌ Failed to download image: {img_response.status_code}")
                return False
        else:
            logger.error(f"❌ DALL-E API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cover generation failed: {str(e)}")
        return False

def main():
    """Generate cover for the latest book."""
    logger = get_logger('cover_generation')
    
    # Find the latest book directory
    output_dir = Path(__file__).parent.parent / "output" / "generated_books"
    book_dirs = [d for d in output_dir.iterdir() 
                if d.is_dir() and d.name != 'archive']
    
    if not book_dirs:
        logger.error("❌ No book directories found")
        return False
    
    # Get the most recent book
    latest_book = max(book_dirs, key=lambda d: d.stat().st_mtime)
    
    logger.info(f"🎯 Generating cover for: {latest_book.name}")
    
    return generate_cover_from_prompt(latest_book)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)