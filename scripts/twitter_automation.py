#!/usr/bin/env python3
"""
Twitter Automation for KindleMint Puzzle Masters
Daily content generation and posting for brain health audience
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import secrets

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import openai
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterAutomation:
    """Automated Twitter content generation for puzzle/brain health niche"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.landing_page = "https://ai-kindlemint-engine.vercel.app"
        
        # Content themes for different days
        self.content_themes = {
            'monday': 'Brain Health Monday - Scientific benefits',
            'tuesday': 'Technique Tuesday - Puzzle solving tips', 
            'wednesday': 'Wisdom Wednesday - Senior success stories',
            'thursday': 'Throwback Thursday - Puzzle history',
            'friday': 'Feature Friday - Free puzzle Friday',
            'saturday': 'Saturday Challenge - Weekend puzzles',
            'sunday': 'Sunday Reflection - Weekly brain training recap'
        }
        
    def generate_daily_content(self) -> Dict[str, str]:
        """Generate Twitter content for today"""
        today = datetime.now().strftime('%A').lower()
        theme = self.content_themes.get(today, 'Daily brain training')
        
        # Generate main tweet
        main_tweet = self._generate_tweet(theme, include_cta=True)
        
        # Generate follow-up thread tweets
        thread_tweets = self._generate_thread_tweets(theme)
        
        return {
            'main_tweet': main_tweet,
            'thread_tweets': thread_tweets,
            'theme': theme,
            'hashtags': self._get_relevant_hashtags()
        }
    
    def _generate_tweet(self, theme: str, include_cta: bool = False) -> str:
        """Generate a single tweet using OpenAI"""
        
        cta_instruction = ""
        if include_cta:
            cta_instruction = f"Include a gentle call-to-action mentioning free puzzles at {self.landing_page}"
        
        prompt = f"""Create an engaging Twitter post for seniors (75+) about {theme}.

Requirements:
- 280 characters or less
- Professional, warm, encouraging tone
- Focus on brain health benefits of puzzles
- Include relevant emojis (but not too many)
- {cta_instruction}
- Target audience: Active seniors interested in brain health

Examples of good tone:
- "Did you know 15 minutes of daily Sudoku can improve memory by 20%? 🧠✨"
- "Puzzle tip: Start with the corners - they give you the most clues! 🧩"
- "At 82, Margaret credits daily puzzles for her sharp mind. What's your secret? 💭"

Generate one tweet:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            tweet = response.choices[0].message.content.strip()
            
            # Ensure tweet is under 280 characters
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
                
            return tweet
            
        except Exception as e:
            logger.error(f"Failed to generate tweet: {e}")
            return self._get_fallback_tweet(theme)
    
    def _generate_thread_tweets(self, theme: str) -> List[str]:
        """Generate 2-3 follow-up tweets for a thread"""
        
        prompt = f"""Create 2-3 follow-up tweets for a Twitter thread about {theme} for seniors.

Each tweet should:
- Be under 280 characters
- Build on the main theme
- Provide valuable, actionable tips
- Use warm, encouraging tone
- Include brain health benefits

Format as a numbered list:
1. [First follow-up tweet]
2. [Second follow-up tweet]  
3. [Third follow-up tweet if relevant]"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            thread_text = response.choices[0].message.content.strip()
            
            # Parse numbered list into individual tweets
            tweets = []
            for line in thread_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                    tweet = line[2:].strip()  # Remove number prefix
                    if len(tweet) <= 280:
                        tweets.append(tweet)
            
            return tweets[:3]  # Max 3 follow-up tweets
            
        except Exception as e:
            logger.error(f"Failed to generate thread tweets: {e}")
            return []
    
    def _get_relevant_hashtags(self) -> List[str]:
        """Get relevant hashtags for the puzzle/brain health niche"""
        hashtags = [
            '#BrainHealth', '#SeniorLife', '#PuzzleLife', '#Sudoku',
            '#BrainTraining', '#MemoryBoost', '#ActiveAging', '#WisdomYears',
            '#PuzzleMaster', '#LargePrint', '#MindfulAging', '#BrainGames',
            '#SeniorWellness', '#CognitiveHealth', '#PuzzleTime'
        ]
        
        # Return 3-5 random relevant hashtags
        return secrets.SystemRandom().sample(hashtags, k=secrets.SystemRandom().randint(3, 5))
    
    def _get_fallback_tweet(self, theme: str) -> str:
        """Fallback tweets if OpenAI fails"""
        fallback_tweets = [
            f"🧠 Daily brain training keeps your mind sharp! Try our free large-print puzzles: {self.landing_page} #BrainHealth #SeniorLife",
            f"🧩 Puzzle tip: Start with what you know, then build from there! Free puzzles waiting: {self.landing_page} #PuzzleLife #BrainTraining",
            f"✨ 15 minutes of daily Sudoku = stronger memory & sharper focus. Get started: {self.landing_page} #ActiveAging #MindfulAging"
        ]
        return secrets.choice(fallback_tweets)
    
    def post_to_twitter(self, content: Dict[str, str]) -> bool:
        """Post content to Twitter (placeholder - requires Twitter API setup)"""
        
        # This would use Twitter API v2 to actually post
        # For now, we'll just log the content that would be posted
        
        logger.info("📱 TWITTER CONTENT GENERATED:")
        logger.info(f"Main Tweet: {content['main_tweet']}")
        
        for i, thread_tweet in enumerate(content['thread_tweets'], 1):
            logger.info(f"Thread {i}: {thread_tweet}")
        
        logger.info(f"Hashtags: {' '.join(content['hashtags'])}")
        
        # Save content to file for manual posting if needed
        self._save_content_to_file(content)
        
        return True
    
    def _save_content_to_file(self, content: Dict[str, str]):
        """Save generated content to file"""
        output_dir = Path('generated/social_media/twitter')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"twitter_content_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                **content,
                'generated_at': datetime.now().isoformat(),
                'landing_page': self.landing_page
            }, f, indent=2)
        
        logger.info(f"💾 Content saved to: {filepath}")

def main():
    """Main execution function"""
    automation = TwitterAutomation()
    
    # Generate daily content
    content = automation.generate_daily_content()
    
    # Post to Twitter (or save for manual posting)
    success = automation.post_to_twitter(content)
    
    if success:
        print("✅ Twitter automation completed successfully!")
        print(f"🔗 Landing page: {automation.landing_page}")
    else:
        print("❌ Twitter automation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
