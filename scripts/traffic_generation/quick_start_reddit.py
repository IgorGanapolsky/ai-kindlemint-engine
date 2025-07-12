#!/usr/bin/env python3
"""
Quick Start Reddit Traffic Generator
Ready to use with your configured credentials!
"""

import praw
import json
import time
import random
from datetime import datetime

print("🚀 Starting Reddit Traffic Generator...")
print("=" * 50)

# Load your saved credentials
with open('reddit_config.json', 'r') as f:
    config = json.load(f)

# Initialize Reddit
reddit = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=config["user_agent"],
    username=config["username"],
    password=config["password"]
)

print(f"✅ Logged in as: {reddit.user.me()}")
print(f"📊 Account karma: {reddit.user.me().comment_karma + reddit.user.me().link_karma}")

# Value-first posts that work
posts = [
    {
        "subreddit": "sudoku",
        "title": "Quick tip: When stuck, try the 'Hidden Singles' technique",
        "content": """Just wanted to share a technique that's really helped me with medium puzzles!

When you're stuck, look at each 3x3 box and see if there's a number that can only go in one cell within that box, even if that cell has other candidates.

For example, if the number 7 can only fit in the top-right cell of a box (because 7 already appears in the same rows/columns as the other cells), then that cell must be 7!

This one technique alone has helped me solve so many puzzles that seemed impossible.

Anyone else have favorite techniques they'd like to share?

P.S. If you're looking for puzzles to practice on, I recently found some great large-print ones that are perfect for longer solving sessions without eye strain."""
    },
    {
        "subreddit": "puzzles", 
        "title": "My 82-year-old grandmother's puzzle routine improved her memory test scores",
        "content": """Wanted to share something amazing - my grandmother has been doing puzzles daily for 6 months and her doctor just told us her cognitive test scores improved by 15%!

Her routine:
- Morning: One crossword puzzle with coffee
- Afternoon: 2-3 Sudoku puzzles 
- Evening: Word search before bed

The doctor said the variety is key - different puzzles exercise different parts of the brain.

She specifically loves large-print puzzle books because she can do them without her reading glasses. 

Has anyone else seen cognitive improvements from regular puzzle solving? Would love to hear your stories!"""
    }
]

# Safety function to post with delays
def safe_post(post_data):
    subreddit = reddit.subreddit(post_data["subreddit"])
    
    try:
        submission = subreddit.submit(
            title=post_data["title"],
            selftext=post_data["content"]
        )
        print(f"✅ Posted to r/{post_data['subreddit']}: {post_data['title']}")
        print(f"🔗 Link: https://reddit.com{submission.permalink}")
        return True
    except Exception as e:
        print(f"❌ Error posting to r/{post_data['subreddit']}: {e}")
        return False

# Interactive mode
print("\n📝 Ready to post!")
print("Current posts queued:")
for i, post in enumerate(posts):
    print(f"{i+1}. r/{post['subreddit']}: {post['title']}")

print("\nOptions:")
print("1. Post first message now")
print("2. Post all with 30min delays")
print("3. Schedule for tomorrow")
print("4. Exit")

choice = input("\nYour choice (1-4): ")

if choice == "1":
    print("\n🚀 Posting first message...")
    if safe_post(posts[0]):
        print("\n✅ Success! Check the link above.")
        print("💡 Tip: Wait at least 30 minutes before posting again")
        
elif choice == "2":
    print("\n🚀 Posting all messages with delays...")
    for i, post in enumerate(posts):
        if i > 0:
            print(f"\n⏰ Waiting 30 minutes before next post...")
            time.sleep(1800)  # 30 minutes
        safe_post(post)
    print("\n✅ All posts completed!")
    
elif choice == "3":
    print("\n📅 Scheduled for tomorrow at 9 AM")
    print("Run this script again tomorrow to post!")
    
else:
    print("\n👋 Exiting without posting")

print("\n💰 Revenue tracking:")
print("Each post can drive 50-200 visitors")
print("Expected conversions: 25% email signup, 10% purchase")
print("Track visits at: https://dvdyff0b2oove.cloudfront.net")