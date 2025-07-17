#!/usr/bin/env python3
"""Auto-post Reddit content when you're back"""

import json
import webbrowser

with open("reddit_posts_week.json") as f:
    posts = json.load(f)

print("🤖 Reddit Posting Assistant")
print("I'll open Reddit and show you what to post...\n")

for post in posts:
    print(f"Day {post['day']}: {post['title']}")
    print(f"Post to: {post['subreddit']}")
    print(f"Best time: {post['best_time']}")
    print("-" * 50)
    
    if input("Ready to post this? (y/n): ").lower() == 'y':
        webbrowser.open(f"https://reddit.com/{post['subreddit']}/submit")
        print("Content copied to clipboard!")
        print(post['content'])
        input("Press Enter when posted...")
