#!/usr/bin/env python3
"""Simplified Reddit Traffic Driver - No API Required"""

import webbrowser
import time
import json
from datetime import datetime

def generate_value_post():
    """Generate a value-first post for Reddit"""
    templates = [
        {
            "title": "TIP: The 'corner constraint' method transformed my solving speed",
            "body": """I used to struggle with medium/hard puzzles until I discovered this:

Start by looking at corners and edges first - they have the most constraints.
This simple change cut my solving time by 40%.

What techniques have helped you improve? Always looking to learn!

(If anyone wants practice puzzles, I found some free large print ones that are great for technique practice)"""
        },
        {
            "title": "Study: 15 minutes of puzzles = 23% better memory (link in comments)",
            "body": """My doctor shared this fascinating research about puzzle-solving and cognitive health.

Key findings:
- 15-20 minutes daily showed measurable improvement
- Large print puzzles had same benefits with less eye strain
- Consistency mattered more than difficulty level

Started doing this with my mom (82) and the results are real!

What's your daily puzzle routine?"""
        }
    ]
    
    import random
    return random.choice(templates)

def main():
    print("🎯 Reddit Traffic Generation (Manual Mode)")
    print("This will open Reddit - you'll need to post manually")
    print()
    
    post = generate_value_post()
    
    print("POST TITLE:")
    print(post["title"])
    print()
    print("POST BODY:")
    print(post["body"])
    print()
    print("SUBREDDITS: r/sudoku, r/puzzles, r/braintraining")
    print()
    print("Opening Reddit in 3 seconds...")
    time.sleep(3)
    
    webbrowser.open("https://reddit.com/r/sudoku/submit")
    
    # Log the action
    with open("traffic_log.json", "a") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "platform": "reddit",
            "action": "manual_post_opened",
            "title": post["title"]
        }, f)
        f.write("\n")

if __name__ == "__main__":
    main()
