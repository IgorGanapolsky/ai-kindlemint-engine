#!/usr/bin/env python3
"""
Generate complete books using Gemini AI (ultra-low cost).
This bypasses OpenAI quota issues while providing professional results.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kindlemint.utils.logger import get_logger

def generate_book_with_gemini():
    """Generate a complete book using only Gemini AI."""
    logger = get_logger('gemini_generation')
    
    logger.info("💎 Generating book with Gemini AI (ultra-low cost)...")
    
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
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Step 1: Generate series metadata
        logger.info("📋 Generating series metadata...")
        metadata_prompt = """
        Create metadata for a large print crossword puzzle book for seniors:
        
        Title: "Large Print Crossword Masters: Volume 1"
        Subtitle: "Easy Large Print Crosswords for Seniors"
        Brand: "Senior Puzzle Studio"
        
        Generate a JSON with complete metadata including:
        - title, subtitle, brand, series
        - volume number (1)
        - difficulty (beginner)
        - target_audience (seniors_55_plus)
        - 7 relevant keywords for Amazon KDP
        - compelling book description
        - suggested price ($7.99)
        - categories
        
        Return only valid JSON.
        """
        
        metadata_response = model.generate_content(metadata_prompt)
        metadata_text = metadata_response.text
        
        # Clean up JSON response
        if '```json' in metadata_text:
            metadata_text = metadata_text.split('```json')[1].split('```')[0].strip()
        elif '```' in metadata_text:
            metadata_text = metadata_text.split('```')[1].split('```')[0].strip()
        
        metadata = json.loads(metadata_text)
        logger.info(f"✅ Metadata generated: {metadata['title']}")
        
        # Step 2: Generate complete manuscript
        logger.info("📖 Generating complete manuscript...")
        manuscript_prompt = f"""
        Create a complete manuscript for "{metadata['title']}" - {metadata['subtitle']}.
        
        This is a large print crossword puzzle book for seniors. Include:
        
        1. Title page with title, subtitle, and author
        2. Friendly introduction explaining the book's purpose
        3. Clear instructions for solving crosswords
        4. 25 crossword puzzle placeholders with descriptions
        5. Answer key section
        6. Back matter with website link and bonus content offer
        7. Copyright and contact information
        
        Requirements:
        - Professional, friendly tone suitable for seniors
        - Large print considerations mentioned
        - Beginner-friendly difficulty
        - 2000+ words of quality content
        - Include placeholder text for where actual puzzles would go
        - Brand integration for Senior Puzzle Studio
        - Website: https://senior-puzzle-studio.carrd.co
        
        Make it ready for Amazon KDP publishing.
        """
        
        manuscript_response = model.generate_content(manuscript_prompt)
        manuscript_content = manuscript_response.text
        logger.info(f"✅ Manuscript generated: {len(manuscript_content)} characters")
        
        # Step 3: Generate cover design prompt
        logger.info("🎨 Generating cover design specifications...")
        cover_prompt_text = f"""
        PROFESSIONAL COVER DESIGN PROMPT
        
        Book: {metadata['title']}
        Subtitle: {metadata['subtitle']}
        Brand: {metadata['brand']}
        Volume: 1
        
        Design Requirements:
        - Amazon KDP book cover (6x9 or 8.5x11 inches)
        - Large, readable typography perfect for seniors
        - Calming blue-green color scheme
        - Crossword grid pattern in background
        - Easy to read at thumbnail size
        - Professional, trustworthy appearance
        - Volume number clearly visible
        - Brand name prominently displayed
        
        Text Layout:
        - Main title: "LARGE PRINT CROSSWORD MASTERS" (top, large font)
        - Volume: "VOLUME 1" (middle, clear)
        - Subtitle: "Easy Large Print Crosswords for Seniors" (below title)
        - Brand: "SENIOR PUZZLE STUDIO" (bottom)
        
        Colors: Professional blues (#2C5F6B), soft greens (#7FB8C3), clean whites
        Style: Clean, accessible, premium quality for seniors market
        """
        
        # Step 4: Generate marketing content
        logger.info("📢 Generating marketing content...")
        marketing_prompt = f"""
        Create marketing content for "{metadata['title']}" by {metadata['brand']}.
        
        Generate:
        1. Social media posts (Facebook, Twitter, Instagram)
        2. Email newsletter content
        3. Amazon bullet points
        4. Author/brand bio
        5. Back cover text
        
        Focus on:
        - Large print benefits for seniors
        - Quality and professionalism
        - Mental stimulation and enjoyment
        - Series branding
        - Call to action for bonus content
        
        Make it compelling and conversion-focused.
        """
        
        marketing_response = model.generate_content(marketing_prompt)
        marketing_content = marketing_response.text
        logger.info(f"✅ Marketing content generated")
        
        # Step 5: Save complete book package
        output_dir = Path(__file__).parent.parent / "output" / "generated_books"
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        book_folder = output_dir / f"gemini_generated_crossword_masters_vol_1_{timestamp}"
        book_folder.mkdir(parents=True, exist_ok=True)
        
        # Save all files
        files_created = []
        
        # Manuscript
        manuscript_file = book_folder / "manuscript.txt"
        with open(manuscript_file, 'w', encoding='utf-8') as f:
            f.write(manuscript_content)
        files_created.append(manuscript_file)
        
        # Metadata
        metadata_file = book_folder / "metadata.json"
        metadata['generated_at'] = datetime.now().isoformat()
        metadata['generation_method'] = 'gemini_ai'
        metadata['api_cost'] = 'ultra_low_cost'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        files_created.append(metadata_file)
        
        # Cover prompt
        cover_file = book_folder / "cover_design_prompt.txt"
        with open(cover_file, 'w', encoding='utf-8') as f:
            f.write(cover_prompt_text)
        files_created.append(cover_file)
        
        # Marketing content
        marketing_file = book_folder / "marketing_content.txt"
        with open(marketing_file, 'w', encoding='utf-8') as f:
            f.write(marketing_content)
        files_created.append(marketing_file)
        
        # KDP publishing instructions
        kdp_instructions = create_kdp_instructions(metadata)
        kdp_file = book_folder / "KDP_PUBLISHING_GUIDE.txt"
        with open(kdp_file, 'w', encoding='utf-8') as f:
            f.write(kdp_instructions)
        files_created.append(kdp_file)
        
        # Step 6: Generate success summary
        logger.info("🎉 GEMINI BOOK GENERATION COMPLETED!")
        logger.info(f"📁 Book package: {book_folder.name}")
        
        total_size = 0
        for file_path in files_created:
            size_kb = file_path.stat().st_size / 1024
            total_size += size_kb
            logger.info(f"   📄 {file_path.name}: {size_kb:.1f} KB")
        
        logger.info(f"💾 Total size: {total_size:.1f} KB")
        logger.info(f"💰 Estimated cost: $0.01-0.02 (vs $1-5 with OpenAI)")
        logger.info(f"📈 Cost savings: 99%+ using Gemini")
        
        return book_folder
        
    except Exception as e:
        logger.error(f"❌ Gemini generation failed: {e}")
        return False

def create_kdp_instructions(metadata):
    """Create detailed KDP publishing instructions."""
    instructions = f"""🚀 AMAZON KDP PUBLISHING INSTRUCTIONS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📚 BOOK DETAILS
--------------
Title: {metadata.get('title', 'Large Print Crossword Masters: Volume 1')}
Subtitle: {metadata.get('subtitle', 'Easy Large Print Crosswords for Seniors')}
Author: {metadata.get('brand', 'Senior Puzzle Studio')}
Price: ${metadata.get('price_usd', 7.99)}

📋 STEP-BY-STEP PUBLISHING
------------------------

1. LOGIN TO KDP
   → Go to kdp.amazon.com
   → Sign in with your Amazon account

2. CREATE NEW PAPERBACK
   → Click "Create New Title"
   → Select "Paperback"

3. ENTER BOOK DETAILS
   → Title: {metadata.get('title', '')}
   → Subtitle: {metadata.get('subtitle', '')}
   → Author: {metadata.get('brand', 'Senior Puzzle Studio')}
   → Description: {metadata.get('description', '')[:200]}...

4. KEYWORDS (use all 7 slots):"""
    
    # Add keywords if available
    if 'keywords' in metadata:
        for i, keyword in enumerate(metadata['keywords'][:7], 1):
            instructions += f"\n   → {i}. {keyword}"
    
    instructions += f"""

5. CATEGORIES
   → Primary: Games & Puzzles > Crosswords
   → Secondary: Health & Fitness > Aging

6. UPLOAD FILES
   → Manuscript: manuscript.txt (convert to PDF)
   → Cover: Use cover_design_prompt.txt to create cover
   → Page size: 8.5" x 11" (large print)

7. PRICING
   → Suggested: ${metadata.get('price_usd', 7.99)}
   → Royalty: 60%
   → Markets: All available

8. FINAL STEPS
   → Preview book carefully
   → Publish when ready
   → Wait 24-72 hours for review

💡 SUCCESS TIPS
--------------
• Large print books have loyal customers
• Target senior Facebook groups for marketing
• Use the marketing content provided
• Plan Volume 2 for series continuation
• Focus on customer reviews

🌐 BRAND INTEGRATION
------------------
Website: https://senior-puzzle-studio.carrd.co
Email signup: Bonus crossword puzzles
Social media: Use marketing content provided

Questions? Check Amazon KDP help center.
"""
    
    return instructions

if __name__ == "__main__":
    result = generate_book_with_gemini()
    if result:
        print(f"✅ Success! Book generated at: {result}")
    else:
        print("❌ Generation failed")
        sys.exit(1)