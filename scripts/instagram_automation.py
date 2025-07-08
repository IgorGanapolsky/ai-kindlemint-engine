#!/usr/bin/env python3
"""
Instagram Automation for KindleMint Puzzle Masters
Visual content generation for brain health and puzzle audience
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import openai
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramAutomation:
    """Automated Instagram content generation for puzzle/brain health niche"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.landing_page = "https://dvdyff0b2oove.cloudfront.net"
        
        # Visual content themes
        self.visual_themes = {
            'monday': 'Motivational brain health quotes with puzzle imagery',
            'tuesday': 'Tutorial carousel - How to solve Sudoku step-by-step',
            'wednesday': 'Before/after - Brain scans showing puzzle benefits',
            'thursday': 'Throwback post - Vintage puzzle books and nostalgia',
            'friday': 'Feature puzzle of the week with large print preview',
            'saturday': 'Community highlight - Senior puzzle solvers',
            'sunday': 'Sunday inspiration - Peaceful puzzle solving scenes'
        }
        
    def generate_daily_content(self) -> Dict[str, str]:
        """Generate Instagram content for today"""
        today = datetime.now().strftime('%A').lower()
        theme = self.visual_themes.get(today, 'Daily brain training inspiration')
        
        # Generate caption
        caption = self._generate_caption(theme)
        
        # Generate image description for DALL-E
        image_prompt = self._generate_image_prompt(theme)
        
        # Generate hashtags
        hashtags = self._get_instagram_hashtags()
        
        return {
            'caption': caption,
            'image_prompt': image_prompt,
            'theme': theme,
            'hashtags': hashtags,
            'cta': f"Link in bio for free puzzles! 👆 {self.landing_page}"
        }
    
    def _generate_caption(self, theme: str) -> str:
        """Generate Instagram caption using OpenAI"""
        
        prompt = f"""Create an engaging Instagram caption for seniors (75+) about {theme}.

Requirements:
- 2-3 sentences maximum (Instagram users scan quickly)
- Warm, encouraging tone
- Include brain health benefits
- Visual storytelling approach
- Call-to-action for free puzzles
- Use emojis naturally (not overwhelming)
- Target: Active seniors interested in mental wellness

Examples of good captions:
- "Nothing beats the satisfaction of completing a challenging Sudoku! 🧩 Studies show daily puzzles can improve memory by up to 20%. Swipe for today's brain booster! ➡️"
- "At 78, Helen solves 3 puzzles every morning with her coffee ☕ 'It keeps my mind sharp and my day focused,' she says. What's your morning brain ritual? 💭"

Generate one caption for: {theme}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            caption = response.choices[0].message.content.strip()
            
            # Add link in bio CTA
            caption += f"\n\n🔗 Free large-print puzzles in bio!"
            
            return caption
            
        except Exception as e:
            logger.error(f"Failed to generate caption: {e}")
            return self._get_fallback_caption(theme)
    
    def _generate_image_prompt(self, theme: str) -> str:
        """Generate DALL-E prompt for Instagram image"""
        
        prompt = f"""Create a DALL-E image prompt for Instagram content about {theme} targeting seniors.

Requirements:
- High-quality, professional photography style
- Warm, inviting colors
- Clear, easy-to-read elements
- Senior-friendly imagery (large fonts, good contrast)
- Puzzle/brain health themed
- Instagram-optimized (square 1:1 ratio)

Examples:
- "Professional photograph of an elegant 75-year-old woman solving a large-print Sudoku puzzle at a cozy kitchen table, natural morning lighting, warm coffee nearby, peaceful expression, shallow depth of field, Instagram style"
- "Clean, modern graphic design showing a large-print Sudoku grid with bold numbers, soft pastel background, elegant typography saying 'Brain Training for Life', minimalist Instagram aesthetic"

Generate one DALL-E prompt for: {theme}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate image prompt: {e}")
            return self._get_fallback_image_prompt()
    
    def _get_instagram_hashtags(self) -> List[str]:
        """Get Instagram-optimized hashtags"""
        hashtags = [
            # Brain health focused
            '#brainhealth', '#memoryboost', '#cognitivehealth', '#mentalwellness',
            
            # Senior specific
            '#seniorlife', '#activesaging', '#60plus', '#70plus', '#80plus', '#wisdomyears',
            
            # Puzzle specific  
            '#sudoku', '#puzzles', '#braintraining', '#braingames', '#puzzlemaster',
            
            # Lifestyle
            '#morningroutine', '#selfcare', '#mindfulaging', '#healthyaging', '#retiredlife',
            
            # Visual/Instagram
            '#largeprint', '#puzzletime', '#brainbooster', '#dailychallenge',
            
            # Community
            '#seniorwellness', '#agingwell', '#neverstoplearning', '#sharpbrain'
        ]
        
        # Instagram optimal: 20-30 hashtags
        return random.sample(hashtags, k=25)
    
    def _get_fallback_caption(self, theme: str) -> str:
        """Fallback captions if OpenAI fails"""
        fallbacks = [
            "🧠 Keep your mind sharp with daily brain training! Our large-print puzzles are perfect for active seniors. 🧩\n\n🔗 Free puzzles in bio!",
            "☕ Morning coffee + challenging Sudoku = the perfect start to any day! Studies show puzzles boost memory by 20%. ✨\n\n🔗 Try our free collection in bio!",
            "🌟 Age is just a number when your mind stays active! Join thousands of seniors who solve puzzles daily. 💪\n\n🔗 Free large-print puzzles in bio!"
        ]
        return random.choice(fallbacks)
    
    def _get_fallback_image_prompt(self) -> str:
        """Fallback image prompt"""
        return "Professional photograph of an elegant senior solving a large-print Sudoku puzzle, warm natural lighting, cozy home setting, peaceful and focused expression, Instagram aesthetic"
    
    def post_to_instagram(self, content: Dict[str, str]) -> bool:
        """Post content to Instagram (placeholder - requires Instagram API)"""
        
        # This would use Instagram Basic Display API to actually post
        # For now, we'll log the content and save for manual posting
        
        logger.info("📸 INSTAGRAM CONTENT GENERATED:")
        logger.info(f"Caption: {content['caption']}")
        logger.info(f"Image Prompt: {content['image_prompt']}")
        logger.info(f"Hashtags: {' '.join(content['hashtags'])}")
        
        # Save content to file
        self._save_content_to_file(content)
        
        return True
    
    def _save_content_to_file(self, content: Dict[str, str]):
        """Save generated content to file"""
        output_dir = Path('generated/social_media/instagram')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"instagram_content_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                **content,
                'generated_at': datetime.now().isoformat(),
                'landing_page': self.landing_page,
                'notes': 'Use DALL-E to generate image from image_prompt, then post with caption and hashtags'
            }, f, indent=2)
        
        logger.info(f"💾 Content saved to: {filepath}")

def main():
    """Main execution function"""
    automation = InstagramAutomation()
    
    # Generate daily content
    content = automation.generate_daily_content()
    
    # Post to Instagram (or save for manual posting)
    success = automation.post_to_instagram(content)
    
    if success:
        print("✅ Instagram automation completed successfully!")
        print(f"🔗 Landing page: {automation.landing_page}")
        print("📝 Use DALL-E to generate the image from the saved prompt")
    else:
        print("❌ Instagram automation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()