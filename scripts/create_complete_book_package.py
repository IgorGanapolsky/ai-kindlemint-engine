#!/usr/bin/env python3
"""
Create complete book package ready for KDP publishing.
Includes manuscript, cover, metadata, and publishing instructions.
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

async def create_complete_book_package(series_info: dict):
    """Create a complete book package ready for KDP publishing."""
    logger = get_logger('complete_package')
    
    logger.info("📚 Creating complete book package...")
    
    # Load environment variables
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "output" / "generated_books"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    brand_slug = series_info['brand'].lower().replace(' ', '_').replace('&', 'and')
    series_slug = series_info['series'].lower().replace(' ', '_')
    
    book_folder = output_dir / f"{brand_slug}_{series_slug}_vol_{series_info['volume']}_{timestamp}"
    book_folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Package directory: {book_folder.name}")
    
    # 1. Generate manuscript
    manuscript_content = await generate_manuscript_content(series_info, logger)
    manuscript_file = book_folder / "manuscript.txt"
    with open(manuscript_file, 'w', encoding='utf-8') as f:
        f.write(manuscript_content)
    
    # 2. Create metadata
    metadata = create_metadata(series_info)
    metadata_file = book_folder / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # 3. Generate cover prompt
    cover_prompt = create_cover_prompt(series_info)
    cover_prompt_file = book_folder / "cover_prompt.txt"
    with open(cover_prompt_file, 'w', encoding='utf-8') as f:
        f.write(cover_prompt)
    
    # 4. Generate automated cover (if API available)
    cover_file = await generate_automated_cover(book_folder, series_info, logger)
    
    # 5. Create KDP publishing instructions
    publishing_instructions = create_kdp_instructions(series_info, metadata)
    instructions_file = book_folder / "KDP_PUBLISHING_INSTRUCTIONS.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(publishing_instructions)
    
    # 6. Create book marketing content
    marketing_content = create_marketing_content(series_info, metadata)
    marketing_file = book_folder / "MARKETING_CONTENT.txt"
    with open(marketing_file, 'w', encoding='utf-8') as f:
        f.write(marketing_content)
    
    # Log results
    logger.info("🎉 COMPLETE BOOK PACKAGE CREATED!")
    logger.info(f"📂 Location: {book_folder}")
    
    for file_path in book_folder.iterdir():
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            logger.info(f"   📄 {file_path.name}: {size_kb:.1f} KB")
    
    return book_folder

async def generate_manuscript_content(series_info: dict, logger):
    """Generate complete manuscript content."""
    content = f"""{series_info['title']}
{series_info['subtitle']}

By {series_info['brand']}

INTRODUCTION

Welcome to {series_info['series']}! This collection has been specially designed for {series_info['target_audience']} who appreciate quality content that's both engaging and accessible.

This Volume {series_info['volume']} features {series_info['difficulty']} level content, perfect for {series_info['description_detail']}.

FEATURES OF THIS BOOK

• Large, clear text that's easy on the eyes
• Professional layout designed for comfort
• High-quality content curated by experts
• Perfect for relaxation and mental stimulation
• Suitable for all skill levels

HOW TO USE THIS BOOK

1. Find a comfortable, well-lit reading space
2. Take your time with each section
3. Don't hesitate to take breaks when needed
4. Enjoy the process and have fun!

MAIN CONTENT

[This section would contain the actual puzzles, activities, or content specific to the book type.
In a real implementation, this would be generated based on the specific niche and requirements.]

CONTENT SECTION 1
{generate_content_section(series_info, 1)}

CONTENT SECTION 2
{generate_content_section(series_info, 2)}

CONTENT SECTION 3
{generate_content_section(series_info, 3)}

ANSWERS & SOLUTIONS

[This section would contain answers or solutions where applicable]

BONUS CONTENT

Thank you for choosing {series_info['brand']}! 

Get exclusive bonus content and stay updated with new releases:
🌐 Visit: https://{series_info['brand'].lower().replace(' ', '-')}.carrd.co
📧 Get your FREE bonus material delivered to your inbox

ABOUT {series_info['brand']}

{series_info['brand']} is dedicated to creating high-quality, accessible content for {series_info['target_audience']}. Our mission is to provide engaging, well-designed books that bring joy and mental stimulation to our readers.

All our books are carefully crafted with attention to detail, ensuring the best possible experience for our valued customers.

© {datetime.now().year} {series_info['brand']} | All Rights Reserved

For customer support and feedback: 
Visit our website for contact information and additional resources.
"""
    
    return content

def generate_content_section(series_info: dict, section_number: int):
    """Generate a content section based on the book type."""
    if 'crossword' in series_info['niche'].lower():
        return f"""
CROSSWORD PUZZLE {section_number}

[In a real implementation, this would contain an actual crossword puzzle grid with clues.
The puzzle would be designed with large print and clear formatting suitable for seniors.]

ACROSS:
1. Sample clue for demonstration
3. Another example clue
5. Easy clue for beginners

DOWN:
2. Cross-referencing clue
4. Simple word puzzle clue
6. Beginner-friendly hint

GRID:
[Large print crossword grid would be displayed here with appropriate spacing and clear numbers]
"""
    else:
        return f"""
SECTION {section_number}: Content

[This section would contain content specific to the book's niche.
The content would be tailored to the target audience and difficulty level.]

Key elements for this section:
- High-quality, engaging material
- Appropriate difficulty level: {series_info['difficulty']}
- Clear formatting and large text
- Interactive elements where appropriate
"""

def create_metadata(series_info: dict):
    """Create comprehensive metadata for the book."""
    return {
        'title': series_info['title'],
        'subtitle': series_info['subtitle'],
        'series': series_info['series'],
        'brand': series_info['brand'],
        'volume': series_info['volume'],
        'difficulty': series_info['difficulty'],
        'target_audience': series_info['target_audience'],
        'niche': series_info['niche'],
        'keywords': [
            series_info['niche'].lower(),
            series_info['target_audience'].lower(),
            f"{series_info['difficulty']} level",
            'large print',
            'high quality',
            series_info['brand'].lower(),
            'volume ' + str(series_info['volume'])
        ],
        'categories': [
            'Games & Puzzles',
            'Activity Books',
            'Senior Entertainment'
        ],
        'price_usd': 7.99,
        'description': f"Perfect {series_info['difficulty']} level {series_info['niche']} designed specifically for {series_info['target_audience']}. Volume {series_info['volume']} in the popular {series_info['series']} collection by {series_info['brand']}.",
        'generated_at': datetime.now().isoformat(),
        'version': '3.0'
    }

def create_cover_prompt(series_info: dict):
    """Create detailed cover design prompt."""
    return f"""Cover Design Prompt for {series_info['title']}:

BOOK DETAILS:
- Title: {series_info['title']}
- Subtitle: {series_info['subtitle']}
- Brand: {series_info['brand']}
- Volume: {series_info['volume']}
- Target: {series_info['target_audience']}

DESIGN REQUIREMENTS:
- Professional book cover suitable for Amazon KDP
- Clean, readable typography for seniors
- Large title text that's easy to read at thumbnail size
- Calming, trustworthy color scheme
- Background pattern related to {series_info['niche']}
- Volume number clearly visible
- Brand name prominently displayed
- High contrast for readability
- Professional appearance that stands out on Amazon

TECHNICAL SPECS:
- Dimensions: 6x9 inches or 8.5x11 inches
- Resolution: 300 DPI minimum
- Format: PNG or JPG
- Readable at thumbnail size (200px wide)

COLOR SCHEME:
- Primary: Professional blues or greens
- Secondary: Calming complementary colors
- Text: High contrast for maximum readability
- Background: Subtle pattern that doesn't interfere with text

STYLE NOTES:
- Target audience is {series_info['target_audience']}
- Should convey quality and professionalism
- Easy to read and understand at first glance
- Consistent with {series_info['brand']} branding
"""

async def generate_automated_cover(book_folder: Path, series_info: dict, logger):
    """Generate automated cover using DALL-E."""
    try:
        import requests
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not found - skipping automated cover generation")
            return None
        
        dalle_prompt = f"""
        Create a professional Amazon KDP book cover for "{series_info['title']}" by {series_info['brand']}.
        
        This is Volume {series_info['volume']} of the {series_info['series']} series.
        Target audience: {series_info['target_audience']}
        Book type: {series_info['niche']}
        Difficulty: {series_info['difficulty']} level
        
        Design requirements:
        - Clean, professional layout
        - Large, readable typography perfect for seniors
        - Calming color scheme (blues, greens, soft colors)
        - Background pattern subtly related to {series_info['niche']}
        - Volume number clearly visible
        - Easy to read at Amazon thumbnail size
        - High contrast text for maximum readability
        - Premium, trustworthy appearance
        
        Text to include:
        - Main title: "{series_info['title']}"
        - Subtitle: "{series_info['subtitle']}"  
        - Volume: "VOLUME {series_info['volume']}"
        - Author/Brand: "{series_info['brand']}"
        
        Style: Professional book cover, modern typography, accessible design for seniors
        """
        
        logger.info("🎨 Generating automated cover with DALL-E...")
        
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
            
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                cover_file = book_folder / "cover_automated.png"
                with open(cover_file, 'wb') as f:
                    f.write(img_response.content)
                
                logger.info("✅ Automated cover generated successfully")
                return cover_file
            else:
                logger.warning(f"Failed to download cover: {img_response.status_code}")
                return None
        else:
            logger.warning(f"DALL-E API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"Automated cover generation failed: {e}")
        return None

def create_kdp_instructions(series_info: dict, metadata: dict):
    """Create step-by-step KDP publishing instructions."""
    return f"""
🚀 AMAZON KDP PUBLISHING INSTRUCTIONS
=======================================

Book: {series_info['title']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📚 BOOK DETAILS
--------------
Title: {metadata['title']}
Subtitle: {metadata['subtitle']}
Author: {metadata['brand']}
Series: {metadata['series']} (Volume {metadata['volume']})
Price: ${metadata['price_usd']}

📋 STEP-BY-STEP PUBLISHING GUIDE
-------------------------------

1. LOGIN TO KDP
   → Go to kdp.amazon.com
   → Sign in with your Amazon account

2. CREATE NEW PAPERBACK
   → Click "Create New Title"
   → Select "Paperback"

3. BOOK DETAILS
   → Title: {metadata['title']}
   → Subtitle: {metadata['subtitle']}
   → Author: {metadata['brand']}
   → Description: {metadata['description']}
   
4. KEYWORDS (use all 7 slots):
   → {metadata['keywords'][0]}
   → {metadata['keywords'][1]}
   → {metadata['keywords'][2]}
   → {metadata['keywords'][3]}
   → {metadata['keywords'][4]}
   → {metadata['keywords'][5]}
   → {metadata['keywords'][6]}

5. CATEGORIES:
   → Primary: {metadata['categories'][0]}
   → Secondary: {metadata['categories'][1]}

6. MANUSCRIPT UPLOAD
   → Upload: manuscript.txt (convert to PDF first)
   → Page size: 8.5" x 11" (recommended for large print)
   → Interior: Black & white

7. COVER UPLOAD
   → Upload: cover.png or cover_automated.png
   → Ensure cover meets KDP requirements
   → Preview thoroughly

8. PRICING
   → Suggested price: ${metadata['price_usd']}
   → Royalty: 60% (recommended)
   → Markets: Select all available

9. FINAL REVIEW
   → Preview your book carefully
   → Check for formatting issues
   → Verify all information is correct

10. PUBLISH
    → Click "Publish Your Paperback Book"
    → Wait for review (24-72 hours)
    → Book will appear on Amazon when approved

🎯 MARKETING CHECKLIST
--------------------
□ Set up Amazon Author Central profile
□ Create social media posts
□ Share on relevant Facebook groups
□ Consider Amazon ads after 2 weeks
□ Collect reviews from early readers
□ Plan Volume {metadata['volume'] + 1} for series continuation

📧 BRAND INTEGRATION
------------------
Ensure back matter includes:
→ Website: https://{metadata['brand'].lower().replace(' ', '-')}.carrd.co
→ Email signup for bonus content
→ Social proof and series information

💡 SUCCESS TIPS
--------------
• High-quality preview images increase sales
• Customer reviews are crucial - follow up with buyers
• Series books perform better - plan the full 5-volume set
• Large print books have loyal, repeat customers
• Focus on customer satisfaction for long-term success

Questions? Refer to Amazon KDP help center or community forums.
"""

def create_marketing_content(series_info: dict, metadata: dict):
    """Create marketing content for social media and promotion."""
    return f"""
📢 MARKETING CONTENT FOR {series_info['title']}
=============================================

🎯 SOCIAL MEDIA POSTS
-------------------

FACEBOOK POST:
🧩 New Release! Perfect for {series_info['target_audience']} who love {series_info['niche']}!

📚 {series_info['title']}
✨ {series_info['subtitle']}
🏷️ Volume {series_info['volume']} in our popular {series_info['series']} collection

Features:
• Large, clear print - easy on the eyes
• {series_info['difficulty'].title()} level - perfect for everyone
• High-quality content by {series_info['brand']}
• Professional layout and design

Available now on Amazon! 
#LargePrint #Seniors #QualityBooks #{series_info['brand'].replace(' ', '')}

TWITTER/X POST:
🆕 {series_info['title']} is here! Volume {series_info['volume']} of our {series_info['series']} series. Perfect {series_info['difficulty']} level {series_info['niche']} for {series_info['target_audience']}. Large print, high quality! 📚✨ #NewRelease #LargePrint

INSTAGRAM CAPTION:
📖 Introducing our latest creation: {series_info['title']} ✨

This beautiful Volume {series_info['volume']} is specially designed for {series_info['target_audience']} who appreciate:
🔹 Large, clear text
🔹 Professional quality
🔹 {series_info['difficulty'].title()} difficulty level
🔹 Engaging content

Part of our {series_info['series']} collection by {series_info['brand']} 💙

Available on Amazon now! Link in bio 👆

#LargePrint #QualityBooks #Seniors #NewRelease #{series_info['brand'].replace(' ', '')} #Amazon #KDP

📧 EMAIL NEWSLETTER
-----------------

Subject: 🎉 New Release: {series_info['title']} is Here!

Hi [Name],

We're thrilled to announce the release of {series_info['title']}, Volume {series_info['volume']} in our popular {series_info['series']} collection!

What makes this book special:
✅ Large, clear print designed for comfort
✅ {series_info['difficulty'].title()} level content - accessible to all
✅ Professional layout and high-quality design
✅ Perfect for {series_info['target_audience']}

This book continues our commitment to providing engaging, accessible content that brings joy and mental stimulation to our readers.

👉 Get your copy on Amazon today: [AMAZON LINK]

As a valued subscriber, remember you have access to exclusive bonus content on our website!

Happy reading!
The {series_info['brand']} Team

P.S. Already planning Volume {series_info['volume'] + 1}! Stay tuned for more updates.

🎪 AMAZON DESCRIPTION (Extended)
------------------------------

{metadata['description']}

Why choose {series_info['brand']}?

🌟 PROVEN QUALITY: Our books are crafted with attention to detail and user experience
🌟 LARGE PRINT: Easy-to-read text designed specifically for comfort
🌟 EXPERT CURATION: Content selected and organized by professionals
🌟 SERIES PROGRESSION: Each volume builds perfectly on the previous ones
🌟 CUSTOMER FOCUSED: We listen to feedback and continuously improve

Perfect for:
• {series_info['target_audience']} seeking quality entertainment
• Anyone who appreciates large, clear text
• Gifts for family members and friends
• Building a collection of high-quality books
• Daily mental exercise and relaxation

📚 Part of the {series_info['series']} Series:
This is Volume {series_info['volume']} in our comprehensive series. Each book stands alone while contributing to a complete collection.

🎁 BONUS: Includes information about accessing exclusive online content and future volume previews.

Order now and join thousands of satisfied customers who trust {series_info['brand']} for quality, accessible content!

📱 HASHTAG STRATEGY
-----------------

Primary hashtags:
#{series_info['brand'].replace(' ', '')}
#LargePrint
#QualityBooks
#Volume{series_info['volume']}

Niche hashtags:
#{series_info['niche'].replace(' ', '').replace('-', '')}
#{series_info['target_audience'].replace(' ', '').replace('_', '')}
#{series_info['difficulty'].title()}Level

Platform hashtags:
#Amazon #KDP #NewRelease #BookLovers #Reading
"""

def main():
    """Create complete book package for Large Print Crossword Masters Volume 1."""
    # Example series info - this would normally come from user input or configuration
    series_info = {
        'title': 'Large Print Crossword Masters: Volume 1',
        'subtitle': 'Easy Large Print Crosswords for Seniors',
        'series': 'Large Print Crossword Masters',
        'brand': 'Senior Puzzle Studio',
        'volume': 1,
        'difficulty': 'beginner',
        'target_audience': 'seniors_55_plus',
        'niche': 'large print crossword puzzles',
        'description_detail': 'cognitive stimulation and entertainment'
    }
    
    return asyncio.run(create_complete_book_package(series_info))

if __name__ == "__main__":
    book_folder = main()
    print(f"✅ Complete book package created in: {book_folder}")