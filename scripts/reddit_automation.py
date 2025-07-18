#!/usr/bin/env python3
"""
Reddit Automation for Sudoku Business
Posts to relevant subreddits to drive traffic to the checkout page
"""

import praw
import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

class RedditAutomation:
    def __init__(self):
        # Reddit API credentials
        self.reddit = praw.Reddit(
            client_id="OX37oY5MNhf0iOdKRwhUSA",
            client_secret="mk-XEasANmHS9CnScSgNyuulH1xNDw",
            username="Virtual_Exit5690",
            password="Rockland25&*",
            user_agent="SudokuBusinessBot/1.0"
        )
        
        # Test with just one subreddit first
        self.target_subreddits = ["sudoku"]
        
        # Post templates
        self.post_templates = [
            {
                "title": "Large Print Sudoku Book for Seniors - Clear, Easy to Read",
                "content": """I just published a Sudoku book specifically designed for seniors! 

Features:
• Large print format for easy reading
• Clear, bold numbers
• Perfect for brain training and mental sharpness
• 100 puzzles with varying difficulty levels
• Great for seniors, caregivers, and anyone who prefers larger print

This book was created with input from senior communities and caregivers. The puzzles are challenging but accessible, perfect for maintaining cognitive health.

Check it out here: https://checkout.stripe.com/c/pay/cs_live_a1IH5vCC4STNf0hMJgNScGyw37thqsNLqgdHSAdxfP4VkE2jIlQQBb6kuW#fidkdWxOYHwnPyd1blppbHNgWjA0V0tmTzRCQkd1YTA3NVRcMEwwZ2dCcVNdS09BVklzTmxycERMYW9Mbn1JX2IyQmpXMGdQcH1gPUNLM3FPNW5rU0JLPUg2SkRWZHZnNkF8RHxfaTNhQVRcNTV%2FPGpzf25ofScpJ2N3amhWYHdzYHcnP3F3cGApJ2lkfGpwcVF8dWAnPyd2bGtiaWBabHFgaCcpJ2BrZGdpYFVpZGZgbWppYWB3dic%2FcXdwYHgl

Would love to hear feedback from the community!"""
            }
        ]
        
        # Track posted subreddits to avoid spam
        self.posted_subreddits = set()
        self.last_post_time = None
        
    def test_connection(self):
        """Test Reddit API connection"""
        try:
            user = self.reddit.user.me()
            print(f"✅ Connected to Reddit as: {user.name}")
            return True
        except Exception as e:
            print(f"❌ Reddit connection failed: {str(e)}")
            return False
    
    def can_post_to_subreddit(self, subreddit_name: str) -> bool:
        """Check if we can post to a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            # Try to get subreddit info
            subreddit.description
            print(f"✅ r/{subreddit_name} is accessible")
            return True
        except Exception as e:
            print(f"❌ r/{subreddit_name} error: {str(e)}")
            return False
    
    def post_to_subreddit(self, subreddit_name: str, template: Dict) -> bool:
        """Post to a specific subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Check if we've posted here recently
            if subreddit_name in self.posted_subreddits:
                print(f"⚠️ Already posted to r/{subreddit_name} recently")
                return False
                
            # Post the content
            post = subreddit.submit(
                title=template["title"],
                selftext=template["content"]
            )
            
            print(f"✅ Posted to r/{subreddit_name}: {template['title']}")
            print(f"   Post URL: https://reddit.com{post.permalink}")
            
            # Track this subreddit
            self.posted_subreddits.add(subreddit_name)
            self.last_post_time = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to post to r/{subreddit_name}: {str(e)}")
            return False
    
    def run_marketing_campaign(self):
        """Run the main marketing campaign"""
        print("🚀 Starting Reddit Marketing Campaign")
        print("=" * 50)
        
        # Test connection first
        if not self.test_connection():
            print("❌ Cannot connect to Reddit. Check credentials.")
            return 0
        
        # Get available subreddits
        available_subreddits = []
        for subreddit in self.target_subreddits:
            if self.can_post_to_subreddit(subreddit):
                available_subreddits.append(subreddit)
        
        print(f"\n📊 Found {len(available_subreddits)} available subreddits")
        
        if not available_subreddits:
            print("❌ No subreddits available for posting")
            return 0
        
        # Post to each available subreddit
        successful_posts = 0
        for subreddit in available_subreddits:
            # Choose a random template
            template = random.choice(self.post_templates)
            
            # Post with delay to avoid rate limiting
            if self.post_to_subreddit(subreddit, template):
                successful_posts += 1
                time.sleep(60)  # Wait 1 minute between posts
            else:
                time.sleep(30)  # Shorter wait if post failed
        
        print(f"\n🎯 Campaign Complete!")
        print(f"✅ Successfully posted to {successful_posts} subreddits")
        print(f"📈 Expected traffic: {successful_posts * 50} - {successful_posts * 200} visitors")
        print(f"💰 Expected sales: {successful_posts * 1} - {successful_posts * 5} sales")
        
        return successful_posts

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run automation
    automation = RedditAutomation()
    
    # Run single campaign
    automation.run_marketing_campaign() 