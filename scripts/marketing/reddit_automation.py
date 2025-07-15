#!/usr/bin/env python3
"""
Reddit Marketing Automation - Post to relevant subreddits
"""

import praw
import time
import argparse
import os
from datetime import datetime
import secrets

# Reddit post templates
TEMPLATES = {
    'sudoku': {
        'title_options': [
            "Free Large Print Sudoku Puzzles for Seniors (No email required)",
            "I made 5 free Sudoku puzzles with extra large print - perfect for seniors",
            "Struggling with tiny Sudoku numbers? Try these large print puzzles (free)",
            "Free Sudoku puzzles designed for people who hate squinting",
            "Large print Sudoku - finally puzzles you can actually see!"
        ],
        'body_template': """Hi r/{subreddit}!

I've been creating large print Sudoku puzzles specifically for seniors and people with vision issues. The numbers are 20pt+ font size - much easier on the eyes than typical puzzle books.

I'm giving away 5 free puzzles to get feedback. No email required, just instant download.

**What's included:**
- 5 progressive puzzles (easy to medium difficulty)
- Extra large print (20pt+ font)
- Complete solutions
- Designed for comfortable solving

Get them here: https://dvdyff0b2oove.cloudfront.net

If you like them, I have a full book of 100 puzzles for $4.99.

Would love to hear your thoughts! What size print do you prefer for puzzles?"""
    },
    'puzzles': {
        'title_options': [
            "Made some large print puzzles for my grandma - sharing them free",
            "Free puzzle pack - extra large print for easier solving",
            "Large print puzzles (finally no more squinting!)"
        ],
        'body_template': """Hey r/{subreddit}!

Created these large print puzzles for my grandma who was struggling with regular puzzle books. Figured others might benefit too.

Free download (no email needed): https://dvdyff0b2oove.cloudfront.net

They're Sudoku puzzles with 20pt+ font. Much easier on the eyes!"""
    }
}

SUBREDDIT_RULES = {
    'sudoku': {
        'self_promotion_allowed': True,
        'flair': None,
        'best_time': 'morning'
    },
    'puzzles': {
        'self_promotion_allowed': True,
        'flair': 'Resource',
        'best_time': 'afternoon'
    },
    'seniorcare': {
        'self_promotion_allowed': False,  # Be careful here
        'flair': None,
        'best_time': 'morning'
    }
}


def create_reddit_client():
    """Create Reddit client using environment variables or config file"""
    # Check for environment variables first
    client_id = os.environ.get('REDDIT_CLIENT_ID')
    client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
    user_agent = os.environ.get('REDDIT_USER_AGENT', 'LargePrintPuzzles/1.0')
    username = os.environ.get('REDDIT_USERNAME')
    password = os.environ.get('REDDIT_PASSWORD')
    
    if not all([client_id, client_secret, username, password]):
        print("❌ Reddit credentials not found in environment variables!")
        print("\nTo set up Reddit automation:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create a 'script' application")
        print("3. Set these environment variables:")
        print("   export REDDIT_CLIENT_ID='your_client_id'")
        print("   export REDDIT_CLIENT_SECRET='your_client_secret'")
        print("   export REDDIT_USERNAME='your_username'")
        print("   export REDDIT_PASSWORD='your_password'")
        return None
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
        # Test authentication
        reddit.user.me()
        print("✅ Successfully authenticated to Reddit!")
        return reddit
    except Exception as e:
        print(f"❌ Failed to authenticate: {e}")
        return None


def post_to_subreddit(reddit, subreddit_name, template_key='sudoku'):
    """Post to a specific subreddit"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Check if subreddit exists and is accessible
        subreddit.id  # This will fail if subreddit doesn't exist
        
        # Get template
        template = TEMPLATES.get(template_key, TEMPLATES['sudoku'])
        
        # Select random title
        title = secrets.choice(template['title_options'])
        
        # Format body
        body = template['body_template'].format(subreddit=subreddit_name)
        
        # Check subreddit rules
        rules = SUBREDDIT_RULES.get(subreddit_name, {})
        
        if not rules.get('self_promotion_allowed', True):
            print(f"⚠️  Warning: {subreddit_name} may not allow self-promotion. Proceed with caution.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return None
        
        # Submit post
        submission = subreddit.submit(
            title=title,
            selftext=body,
            flair_id=rules.get('flair')
        )
        
        print(f"✅ Posted to r/{subreddit_name}")
        print(f"   Title: {title}")
        print(f"   URL: https://reddit.com{submission.permalink}")
        
        return submission
        
    except Exception as e:
        print(f"❌ Failed to post to r/{subreddit_name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Reddit Marketing Automation')
    parser.add_argument('action', choices=['post', 'schedule'], help='Action to perform')
    parser.add_argument('--subreddit', help='Subreddit to post to')
    parser.add_argument('--template', default='sudoku', help='Template to use')
    parser.add_argument('--delay', type=int, default=0, help='Delay in minutes before posting')
    
    args = parser.parse_args()
    
    # Create Reddit client
    reddit = create_reddit_client()
    if not reddit:
        return
    
    if args.action == 'post':
        if not args.subreddit:
            print("❌ Please specify a subreddit with --subreddit")
            return
        
        if args.delay > 0:
            print(f"⏰ Waiting {args.delay} minutes before posting...")
            time.sleep(args.delay * 60)
        
        post_to_subreddit(reddit, args.subreddit, args.template)
    
    elif args.action == 'schedule':
        # Schedule posts to multiple subreddits
        schedule = [
            ('sudoku', 0),
            ('puzzles', 30),  # 30 minutes later
            ('crossword', 60), # 1 hour later
        ]
        
        print("📅 Scheduled posts:")
        for subreddit, delay in schedule:
            print(f"   r/{subreddit} - in {delay} minutes")
        
        for subreddit, delay in schedule:
            if delay > 0:
                print(f"\n⏰ Waiting {delay} minutes before posting to r/{subreddit}...")
                time.sleep(delay * 60)
            
            post_to_subreddit(reddit, subreddit, args.template)
            
            # Add random delay to avoid looking like spam
            if subreddit != schedule[-1][0]:  # Not the last one
                wait = secrets.SystemRandom().randint(5, 10)
                print(f"   Waiting {wait} minutes before next post...")
                time.sleep(wait * 60)


if __name__ == "__main__":
    main()
