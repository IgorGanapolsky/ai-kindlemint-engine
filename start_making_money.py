#!/usr/bin/env python3
"""
START MAKING MONEY IN 30 MINUTES
No complex setup. Just revenue.
"""

import webbrowser
import os

def setup_gumroad():
    """Setup Gumroad in 5 minutes"""
    print("🛍️  SETTING UP GUMROAD (5 minutes)")
    print("1. Opening Gumroad signup...")
    webbrowser.open("https://gumroad.com/signup")
    
    print("\n2. Create these products:")
    print("   - 5 Sudoku Puzzles PDF: $4.99")
    print("   - 20 Sudoku Puzzles PDF: $14.99")  
    print("   - 100 Puzzle Mega Pack: $29.99")
    
    print("\n3. Upload PDFs from generated/ folder")
    print("4. Get your Gumroad links")
    print("5. Add to landing page")

def create_buy_button():
    """Generate HTML for buy button"""
    html = """
<!-- Add this to your landing page -->
<div class="text-center mt-8">
    <h3 class="text-2xl font-bold mb-4">Want More Puzzles?</h3>
    
    <!-- Gumroad Buy Button -->
    <a class="gumroad-button" href="https://gumroad.com/l/YOUR_PRODUCT_ID">
        Buy 100 Puzzles - $29.99
    </a>
    
    <!-- Stripe Checkout Button -->
    <button id="checkout-button" class="bg-green-600 text-white px-8 py-4 rounded-lg text-xl font-bold">
        Buy Complete Collection - $29.99
    </button>
</div>

<script src="https://gumroad.com/js/gumroad.js"></script>
"""
    
    with open("buy_button.html", "w") as f:
        f.write(html)
    
    print("✅ Created buy_button.html - Add this to your landing page!")

def quick_reddit_marketing():
    """Post to Reddit for instant traffic"""
    subreddits = [
        "r/sudoku",
        "r/puzzles", 
        "r/CasualGames",
        "r/seniorcare",
        "r/Alzheimers"
    ]
    
    post_template = """
[FREE] 5 Large Print Sudoku Puzzles for Seniors

Hi everyone! I created some large print Sudoku puzzles specifically designed for seniors and those with vision issues.

Features:
- Extra large print (20pt+)
- Easy to medium difficulty
- Clear grids with thick lines
- Solutions included

Free download: https://dvdyff0b2oove.cloudfront.net

I also have puzzle packs available if you want more. Would love feedback!
"""
    
    print("\n📱 REDDIT MARKETING (10 minutes)")
    print("Post this to these subreddits:")
    for sub in subreddits:
        print(f"   - {sub}")
    
    print(f"\nPOST TEMPLATE:\n{post_template}")
    
    with open("reddit_post.txt", "w") as f:
        f.write(post_template)

def setup_kdp():
    """Quick KDP setup"""
    print("\n📚 KDP SETUP (Tonight)")
    print("1. Go to: https://kdp.amazon.com")
    print("2. Click 'Create a new title'")
    print("3. Upload PDFs from simple_book_generator.py")
    print("4. Use these categories:")
    print("   - Games & Activities > Puzzles")
    print("   - Games & Activities > Logic & Brain Teasers")
    print("5. Price at $7.99")
    print("6. Publish!")

def revenue_tracker():
    """Simple revenue tracking"""
    tracker = """
# DAILY REVENUE TRACKER

## Day 1
- Gumroad: $___
- KDP: $___
- Direct: $___
TOTAL: $___

## Day 2
- Gumroad: $___
- KDP: $___
- Direct: $___
TOTAL: $___

## Week 1 Total: $___
## Month 1 Goal: $5,000
"""
    
    with open("REVENUE.md", "w") as f:
        f.write(tracker)
    
    print("\n💰 Created REVENUE.md - Track your money!")

def main():
    print("🚀 START MAKING MONEY IN 30 MINUTES")
    print("=" * 50)
    
    # 1. Setup selling platforms
    setup_gumroad()
    
    # 2. Create buy buttons
    create_buy_button()
    
    # 3. Marketing templates
    quick_reddit_marketing()
    
    # 4. KDP instructions
    setup_kdp()
    
    # 5. Revenue tracking
    revenue_tracker()
    
    print("\n✅ COMPLETE MONETIZATION CHECKLIST:")
    print("[ ] Create Gumroad account (5 min)")
    print("[ ] Upload 3 products (10 min)")
    print("[ ] Add buy button to landing page (5 min)")
    print("[ ] Post to 5 Reddit communities (10 min)")
    print("[ ] Schedule KDP upload for tonight")
    
    print("\n💡 IMPORTANT MINDSET SHIFTS:")
    print("❌ Stop: Perfecting code, fixing infrastructure, planning")
    print("✅ Start: Selling ugly products that work")
    
    print("\n🎯 GOAL: First sale within 2 hours!")
    print("   If it doesn't sell, make it cheaper.")
    print("   If it still doesn't sell, make it simpler.")
    print("   Keep shipping until something clicks!")

if __name__ == "__main__":
    main()