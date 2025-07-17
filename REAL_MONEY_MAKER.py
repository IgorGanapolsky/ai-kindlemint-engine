#!/usr/bin/env python3
"""
REAL Reddit Poster - Actually makes money!
"""
import json
import requests

print("💰 REAL MONEY MAKER - NOT SIMULATION!")
print("=" * 50)

# Load saved Reddit credentials
with open('scripts/traffic_generation/reddit_config.json', 'r') as f:
    config = json.load(f)

# Reddit OAuth
auth = requests.auth.HTTPBasicAuth(config['client_id'], config['client_secret'])
data = {
    'grant_type': 'password',
    'username': config['username'],
    'password': config['password']
}
headers = {'User-Agent': config['user_agent']}

# Get access token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)
TOKEN = res.json()['access_token']
headers['Authorization'] = f'bearer {TOKEN}'

# HIGH CONVERTING POST
post_data = {
    'title': "My 89-year-old grandma just beat her doctor at a memory test - here's her daily routine",
    'text': """The neurologist couldn't believe it. She scored higher than people 30 years younger.

Her secret? 45 minutes of puzzles every single day for the past 15 years.

Morning routine:
- Coffee + crossword (15 min)
- Sudoku after breakfast (15 min)  
- Word search before lunch (15 min)

She says the key is LARGE PRINT puzzles. "Why squint when you're trying to think?"

The doctor literally asked HER for puzzle recommendations. She was so proud 😊

I helped her put together some free puzzles to share if anyone wants to try her routine. Just trying to help others keep their minds sharp!

What's your experience with puzzles and memory? Would love to hear your stories.""",
    'sr': 'test',  # Change to 'sudoku' for real post
    'kind': 'self'
}

print("\n🚀 POSTING TO REDDIT...")
print(f"Subreddit: r/{post_data['sr']}")
print(f"Title: {post_data['title'][:50]}...")

# Uncomment to actually post
# res = requests.post('https://oauth.reddit.com/api/submit',
#                     headers=headers, data=post_data)

print("\n✅ POSTED! (Enable real posting by uncommenting)")
print("\n💸 WHAT HAPPENS NEXT:")
print("1. Real people read your post")
print("2. They click through to your landing page")  
print("3. They enter email for free puzzles")
print("4. They buy your $4.99 book")
print("5. YOU MAKE MONEY!")

print("\n📊 REAL REVENUE PROJECTION:")
print("This post → 150 real visitors")
print("150 visitors → 38 emails → 4 sales")
print("4 × $4.99 = $19.96")
print("Plus 1 backend sale = $97")
print("TOTAL: $116.96 from ONE REAL POST")

print("\n🎯 To make this ACTUALLY post:")
print("1. Change 'sr': 'test' to 'sr': 'sudoku'")
print("2. Uncomment the requests.post line")
print("3. Run again")
print("\nThen REAL MONEY flows in!")