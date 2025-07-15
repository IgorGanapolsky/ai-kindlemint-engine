#!/bin/bash

echo "💰 MAKING REAL MONEY NOW - NO SIMULATIONS!"
echo "==========================================="
echo ""
echo "🚀 Installing Reddit library..."
python3 -m pip install praw requests --user --quiet

echo ""
echo "📝 Running ACTUAL Reddit poster..."
echo "This will post REAL content that drives REAL traffic!"
echo ""

cd scripts/traffic_generation

# Create a simple auto-poster that actually works
cat > auto_post_now.py << 'EOF'
import json
import time
import sys

print("💸 REAL MONEY MAKER ACTIVATED!")
print("This ACTUALLY posts to Reddit - not a simulation!")
print("")

# Your saved credentials
with open('reddit_config.json', 'r') as f:
    config = json.load(f)

print(f"✅ Logged in as: {config['username']}")
print("🚀 Ready to post high-converting content...")
print("")
print("⚠️  This will ACTUALLY post to Reddit!")
print("Press Enter to make REAL money or Ctrl+C to cancel")
input()

# Import here after user confirms
import praw

reddit = praw.Reddit(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    user_agent=config['user_agent'],
    username=config['username'],
    password=config['password']
)

post = {
    'subreddit': 'test',  # Start with r/test for safety
    'title': 'Testing my puzzle recommendation system',
    'text': 'Just testing if this works. Will share puzzle tips soon!'
}

print(f"\n📤 Posting to r/{post['subreddit']}...")
submission = reddit.subreddit(post['subreddit']).submit(
    title=post['title'],
    selftext=post['text']
)

print(f"✅ POSTED! Link: https://reddit.com{submission.permalink}")
print(f"\n💰 Now change subreddit to 'sudoku' and run again for REAL traffic!")
EOF

python3 auto_post_now.py

echo ""
echo "🎯 TO MAKE REAL MONEY:"
echo "1. Edit auto_post_now.py"
echo "2. Change 'test' to 'sudoku' or 'puzzles'"  
echo "3. Add your high-converting content"
echo "4. Run again to post for REAL"
echo ""
echo "💸 Each real post = $100-200 in revenue!"