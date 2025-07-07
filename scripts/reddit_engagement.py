#!/usr/bin/env python3
"""
Reddit Engagement Automation for KindleMint Puzzle Masters
Respectful, value-first community engagement to drive organic traffic
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import secrets

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import openai
import requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditEngagement:
    """Respectful Reddit engagement for organic traffic generation"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.landing_page = "https://ai-kindlemint-engine.vercel.app"
        
        # Target subreddits with engagement strategies
        self.subreddits = {
            'r/puzzles': {
                'strategy': 'Share free puzzles, solve community puzzles, offer help',
                'mention_frequency': 'low',  # Only when directly relevant
                'value_ratio': '10:1'  # 10 value posts for every 1 subtle mention
            },
            'r/sudoku': {
                'strategy': 'Expert tips, solve challenges, share techniques',
                'mention_frequency': 'low',
                'value_ratio': '8:1'
            },
            'r/seniors': {
                'strategy': 'Brain health discussions, activity recommendations',
                'mention_frequency': 'medium',
                'value_ratio': '5:1'
            },
            'r/selfpublishing': {
                'strategy': 'Share publishing journey, offer insights on puzzle books',
                'mention_frequency': 'medium', 
                'value_ratio': '5:1'
            },
            'r/KDP': {
                'strategy': 'Publishing tips, niche insights, market data',
                'mention_frequency': 'high',  # Most commercial-friendly
                'value_ratio': '3:1'
            }
        }
        
        # Track engagement to avoid spam
        self.daily_engagement_limit = 5  # Max 5 comments/posts per day total
        self.engagement_log_file = 'data/reddit_engagement_log.json'
        
    def engage_respectfully(self) -> bool:
        """Main engagement function with built-in respect and value"""
        
        # Check daily limits
        if self._check_daily_limits():
            logger.info("✅ Daily engagement limit reached - respecting community")
            return True
        
        # Get market insights to inform engagement
        market_insights = self._get_market_insights()
        
        # Find engagement opportunities
        opportunities = self._find_engagement_opportunities(market_insights)
        
        # Execute respectful engagement
        for opportunity in opportunities[:2]:  # Max 2 engagements per run
            self._execute_engagement(opportunity)
            time.sleep(secrets.SystemRandom().randint(300, 600))  # 5-10 minute breaks between engagements
        
        return True
    
    def _check_daily_limits(self) -> bool:
        """Check if we've hit daily engagement limits"""
        try:
            if not os.path.exists(self.engagement_log_file):
                return False
                
            with open(self.engagement_log_file, 'r') as f:
                log = json.load(f)
            
            today = datetime.now().strftime('%Y-%m-%d')
            today_engagements = log.get(today, [])
            
            return len(today_engagements) >= self.daily_engagement_limit
            
        except Exception as e:
            logger.error(f"Error checking daily limits: {e}")
            return False
    
    def _get_market_insights(self) -> Dict:
        """Get recent market insights to inform engagement"""
        try:
            insights_file = 'data/market-insights/reddit_insights_20250705.json'
            if os.path.exists(insights_file):
                with open(insights_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading market insights: {e}")
        
        return {'trending_topics': [], 'opportunities': []}
    
    def _find_engagement_opportunities(self, market_insights: Dict) -> List[Dict]:
        """Find valuable engagement opportunities based on market data"""
        
        opportunities = []
        
        # Look for trending topics where we can add value
        trending_topics = market_insights.get('trending_topics', [])
        
        for topic in trending_topics:
            if self._is_relevant_topic(topic):
                opportunity = {
                    'type': 'value_comment',
                    'topic': topic,
                    'subreddit': self._best_subreddit_for_topic(topic),
                    'engagement_style': 'helpful_expert'
                }
                opportunities.append(opportunity)
        
        # Add proactive value opportunities
        opportunities.extend(self._generate_proactive_opportunities())
        
        return opportunities
    
    def _is_relevant_topic(self, topic: str) -> bool:
        """Check if topic is relevant to our niche"""
        relevant_keywords = [
            'puzzle', 'sudoku', 'brain', 'memory', 'senior', 'aging',
            'cognitive', 'mental', 'wellness', 'activity', 'retirement',
            'large print', 'crossword', 'game', 'challenge'
        ]
        
        topic_lower = topic.lower()
        return any(keyword in topic_lower for keyword in relevant_keywords)
    
    def _best_subreddit_for_topic(self, topic: str) -> str:
        """Determine best subreddit for a given topic"""
        topic_lower = topic.lower()
        
        if 'sudoku' in topic_lower:
            return 'r/sudoku'
        elif 'puzzle' in topic_lower:
            return 'r/puzzles'
        elif 'senior' in topic_lower or 'aging' in topic_lower:
            return 'r/seniors'
        elif 'publish' in topic_lower or 'kdp' in topic_lower:
            return 'r/selfpublishing'
        else:
            return 'r/puzzles'  # Default
    
    def _generate_proactive_opportunities(self) -> List[Dict]:
        """Generate proactive engagement opportunities"""
        proactive_opportunities = [
            {
                'type': 'free_puzzle_share',
                'subreddit': 'r/puzzles',
                'content_type': 'text_post',
                'title': 'Free Large-Print Sudoku for the Community',
                'engagement_style': 'gift_giving'
            },
            {
                'type': 'brain_health_tip',
                'subreddit': 'r/seniors', 
                'content_type': 'comment',
                'engagement_style': 'educational'
            },
            {
                'type': 'publishing_insight',
                'subreddit': 'r/selfpublishing',
                'content_type': 'comment',
                'engagement_style': 'experience_sharing'
            }
        ]
        
        # Return 1-2 random proactive opportunities
        return secrets.SystemRandom().sample(proactive_opportunities, k=secrets.SystemRandom().randint(1, 2))
    
    def _execute_engagement(self, opportunity: Dict):
        """Execute a specific engagement with maximum value and respect"""
        
        logger.info(f"🤝 Executing engagement: {opportunity['type']} in {opportunity['subreddit']}")
        
        # Generate appropriate content
        content = self._generate_engagement_content(opportunity)
        
        # Log the engagement (for tracking limits)
        self._log_engagement(opportunity, content)
        
        # In a real implementation, this would post to Reddit
        # For now, we save content for manual review/posting
        self._save_engagement_content(opportunity, content)
        
        logger.info(f"✅ Engagement content generated and saved for review")
    
    def _generate_engagement_content(self, opportunity: Dict) -> str:
        """Generate high-value engagement content using AI"""
        
        subreddit = opportunity['subreddit']
        engagement_style = opportunity['engagement_style']
        content_type = opportunity.get('content_type', 'comment')
        
        # Get subreddit-specific guidelines
        guidelines = self.subreddits.get(subreddit, {})
        strategy = guidelines.get('strategy', 'helpful expert advice')
        mention_frequency = guidelines.get('mention_frequency', 'low')
        
        # Determine if we should include subtle mention
        include_mention = self._should_include_mention(mention_frequency)
        
        mention_instruction = ""
        if include_mention:
            mention_instruction = f"""
SUBTLE MENTION: Only if naturally relevant, you may mention "I've been working on some free large-print puzzles" and provide the link {self.landing_page}. 
CRITICAL: Only include this if it adds genuine value to your response. Never force it."""
        
        prompt = f"""Create a valuable Reddit {content_type} for {subreddit} using {engagement_style} style.

SUBREDDIT STRATEGY: {strategy}

REQUIREMENTS:
- Provide genuine, actionable value first
- Professional but warm, human tone
- 100-200 words maximum 
- Focus on helping the community
- Share real expertise about puzzles/brain health
- Never sound promotional or salesy
- Follow Reddit community guidelines
- Be authentic and conversational

ENGAGEMENT TYPE: {opportunity['type']}

{mention_instruction}

Examples of good value-first content:
- Detailed solving techniques with step-by-step explanations
- Personal experience with brain health benefits (backed by research)
- Free resources and genuinely helpful tips
- Answering specific questions with expert knowledge

Generate the {content_type} content:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate engagement content: {e}")
            return self._get_fallback_content(opportunity)
    
    def _should_include_mention(self, frequency: str) -> bool:
        """Determine if we should include a subtle mention based on frequency setting"""
        if frequency == 'low':
            return secrets.SystemRandom().random() < 0.1  # 10% chance
        elif frequency == 'medium':
            return secrets.SystemRandom().random() < 0.3  # 30% chance  
        elif frequency == 'high':
            return secrets.SystemRandom().random() < 0.5  # 50% chance
        return False
    
    def _get_fallback_content(self, opportunity: Dict) -> str:
        """Fallback content if AI generation fails"""
        fallbacks = {
            'free_puzzle_share': "I've been creating some large-print Sudoku puzzles specifically for seniors. Happy to share them with the community if anyone's interested!",
            'brain_health_tip': "Daily puzzle solving has been shown in studies to improve memory and cognitive function by up to 20%. The key is consistency - even 15 minutes a day makes a difference!",
            'publishing_insight': "When publishing puzzle books, I've found that large-print formatting is crucial for the senior market. Font size 16+ makes a huge difference in sales."
        }
        
        return fallbacks.get(opportunity['type'], "Happy to help with any puzzle-related questions!")
    
    def _log_engagement(self, opportunity: Dict, content: str):
        """Log engagement for daily limit tracking"""
        try:
            # Load existing log
            log = {}
            if os.path.exists(self.engagement_log_file):
                with open(self.engagement_log_file, 'r') as f:
                    log = json.load(f)
            
            # Add today's engagement
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in log:
                log[today] = []
            
            log[today].append({
                'timestamp': datetime.now().isoformat(),
                'subreddit': opportunity['subreddit'],
                'type': opportunity['type'],
                'content_preview': content[:100] + "..." if len(content) > 100 else content
            })
            
            # Save updated log
            os.makedirs(os.path.dirname(self.engagement_log_file), exist_ok=True)
            with open(self.engagement_log_file, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging engagement: {e}")
    
    def _save_engagement_content(self, opportunity: Dict, content: str):
        """Save engagement content for manual review/posting"""
        output_dir = Path('generated/reddit_engagement')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"reddit_engagement_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                'opportunity': opportunity,
                'content': content,
                'generated_at': datetime.now().isoformat(),
                'instructions': 'Review content for quality, then post manually to maintain authenticity',
                'guidelines': 'Always prioritize community value over self-promotion'
            }, f, indent=2)
        
        logger.info(f"💾 Engagement content saved to: {filepath}")

def main():
    """Main execution function"""
    if '--respectful' not in sys.argv:
        print("❌ Must use --respectful flag to confirm value-first approach")
        sys.exit(1)
    
    engagement = RedditEngagement()
    
    # Execute respectful engagement
    success = engagement.engage_respectfully()
    
    if success:
        print("✅ Reddit engagement completed respectfully!")
        print("📋 Review generated content in generated/reddit_engagement/")
        print("🤝 Always prioritize community value over promotion")
    else:
        print("❌ Reddit engagement failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
